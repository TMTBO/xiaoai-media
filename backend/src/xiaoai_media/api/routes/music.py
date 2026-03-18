from __future__ import annotations

import logging
import re
from difflib import get_close_matches
from typing import Any

import aiohttp
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/music", tags=["music"])

# In-memory playlist store: resolved_device_id -> {songs, current, device_id}
_playlists: dict[str, dict[str, Any]] = {}

_PLATFORMS = {"tx", "kw", "kg", "wy", "mg"}

# Platform name → code mapping for natural-language command parsing
_PLATFORM_KEYWORDS: dict[str, str] = {
    "腾讯音乐": "tx",
    "腾讯": "tx",
    "qq音乐": "tx",
    "qq": "tx",
    "网易云音乐": "wy",
    "网易云": "wy",
    "网易": "wy",
    "酷我音乐": "kw",
    "酷我": "kw",
    "酷狗音乐": "kg",
    "酷狗": "kg",
    "咪咕音乐": "mg",
    "咪咕": "mg",
}


async def _proxy(method: str, path: str, **kwargs: Any) -> dict:
    """Proxy a request to the music_download service."""
    base = config.MUSIC_API_BASE_URL.rstrip("/")
    url = f"{base}{path}"
    _log.info("MusicAPI: %s %s", method.upper(), url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, timeout=aiohttp.ClientTimeout(total=10), **kwargs
            ) as resp:
                data: dict = await resp.json(content_type=None)
                _log.info(
                    "MusicAPI: response code=%s status=%d",
                    data.get("code"),
                    resp.status,
                )
                if resp.status >= 500:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Music API returned HTTP {resp.status}",
                    )
                return data
    except aiohttp.ClientError as e:
        _log.error("MusicAPI connection error: %s", e)
        raise HTTPException(
            status_code=502,
            detail=f"Cannot connect to music service at {config.MUSIC_API_BASE_URL}: {e}",
        )


def _platform(platform: str | None) -> str:
    plat = platform or config.MUSIC_DEFAULT_PLATFORM
    if plat not in _PLATFORMS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid platform: {plat!r}. Must be one of: {', '.join(sorted(_PLATFORMS))}",
        )
    return plat


def _build_command(song: dict) -> str:
    """Build an idiomatic Chinese voice command to play a song."""
    name = song.get("name", "")
    singer = song.get("singer", "")
    return f"播放{singer}的{name}" if singer else f"播放{name}"


def _parse_chart_command(text: str) -> tuple[str | None, str]:
    """Parse a chart play command, returning (platform_code|None, chart_keyword).

    Handles: "播放腾讯热歌榜", "打开网易云飙升榜", "播放排行榜" etc.
    """
    text = re.sub(r"^(打开|播放)\s*", "", text.strip())
    platform: str | None = None
    # Sort by length descending to match longer keywords first
    for keyword in sorted(_PLATFORM_KEYWORDS, key=len, reverse=True):
        if keyword.lower() in text.lower():
            platform = _PLATFORM_KEYWORDS[keyword]
            text = re.sub(re.escape(keyword), "", text, flags=re.IGNORECASE)
            break
    text = re.sub(r"^[的\s]+", "", text).strip()
    return platform, text


def _find_chart(chart_list: list[dict], keyword: str) -> dict | None:
    """Find the best-matching chart by keyword (substring → difflib → first)."""
    if not chart_list:
        return None
    if not keyword:
        return chart_list[0]
    kw = keyword.lower()
    # Exact substring match
    for c in chart_list:
        if kw in c.get("name", "").lower():
            return c
    # Fuzzy match via difflib
    names = [c.get("name", "") for c in chart_list]
    matches = get_close_matches(keyword, names, n=1, cutoff=0.3)
    if matches:
        matched_name = matches[0]
        for c in chart_list:
            if c.get("name") == matched_name:
                return c
    # Char-level partial match
    for c in chart_list:
        name = c.get("name", "").lower()
        if any(ch in name for ch in kw if ch.strip()):
            return c
    return chart_list[0]


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------


class SongItem(BaseModel):
    id: str
    name: str
    singer: str
    platform: str


class PlayRequest(BaseModel):
    songs: list[SongItem]
    index: int = 0
    device_id: str | None = None


class DeviceRequest(BaseModel):
    device_id: str | None = None


class VoiceCommandRequest(BaseModel):
    text: str
    device_id: str | None = None


class AnnounceSearchRequest(BaseModel):
    query: str
    count: int
    device_id: str | None = None


# ---------------------------------------------------------------------------
# Search & Charts (proxy routes)
# ---------------------------------------------------------------------------


@router.get("/search")
async def search_music(
    query: str = Query(..., description="Search keyword"),
    platform: str | None = Query(None, description="Platform: tx|kw|kg|wy|mg"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
):
    """Search for music via the music service."""
    if not query.strip():
        raise HTTPException(status_code=422, detail="query must not be empty")
    plat = _platform(platform)
    return await _proxy(
        "POST",
        "/api/v3/search",
        json={"platform": plat, "query": query.strip(), "page": page, "limit": limit},
    )


@router.get("/ranks")
async def get_ranks(
    platform: str | None = Query(None, description="Platform: tx|kw|kg|wy|mg"),
):
    """Get the list of music charts for a platform."""
    plat = _platform(platform)
    return await _proxy("GET", f"/api/v3/{plat}/ranks")


@router.get("/rank/{rank_id}")
async def get_rank_songs(
    rank_id: str,
    platform: str | None = Query(None, description="Platform: tx|kw|kg|wy|mg"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """Get songs in a specific chart."""
    plat = _platform(platform)
    return await _proxy(
        "GET",
        f"/api/v3/{plat}/rank/{rank_id}",
        params={"page": page, "limit": limit},
    )


# ---------------------------------------------------------------------------
# Playback control (via Xiaomi voice commands + server-side playlist)
# ---------------------------------------------------------------------------


@router.post("/play")
async def play_music(req: PlayRequest):
    """Set the playlist and play the song at the given index by URL."""
    if not req.songs:
        raise HTTPException(status_code=422, detail="songs must not be empty")
    if not (0 <= req.index < len(req.songs)):
        raise HTTPException(status_code=422, detail="index out of range")

    song = req.songs[req.index]
    
    # Get the song URL from music API
    plat = song.platform
    song_id = song.id
    _log.info("Getting URL for song %s (platform=%s, id=%s)", song.name, plat, song_id)
    
    try:
        # Get playback URL from music API
        url_data = await _proxy(
            "POST",
            "/api/v3/play",
            json={"songId": song_id, "platform": plat, "quality": "128k"}
        )
        url = url_data.get("data", {}).get("url")
        
        if not url:
            raise HTTPException(
                status_code=404,
                detail=f"Cannot get playback URL for song {song.name}"
            )
        
        _log.info("Got playback URL: %s", url)
        
        # Play the URL directly using the correct method
        async with XiaoAiClient() as client:
            result = await client.play_url(url, req.device_id, _type=2)

        _playlists[req.device_id] = {
            "songs": [s.model_dump() for s in req.songs],
            "current": req.index,
            "device_id": req.device_id,
        }
        _log.info(
            "Playlist set for device %s: %d songs, current=%d",
            req.device_id,
            len(req.songs),
            req.index,
        )
        return {
            "device_id": req.device_id,
            "url": url,
            "result": result,
            "current": song.model_dump(),
            "index": req.index,
            "total": len(req.songs),
        }
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play music: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/next")
async def play_next(req: DeviceRequest):
    """Advance to the next song in the server-side playlist."""
    try:
        async with XiaoAiClient() as client:
            pl = _playlists.get(req.device_id)
            if not pl or not pl["songs"]:
                raise HTTPException(
                    status_code=404,
                    detail="No playlist for this device. Use POST /api/music/play first.",
                )
            songs = pl["songs"]
            next_idx = (pl["current"] + 1) % len(songs)
            song = songs[next_idx]
            
            # Get the song URL
            plat = song["platform"]
            song_id = song["id"]
            _log.info("Getting URL for next song %s (platform=%s, id=%s)", song["name"], plat, song_id)
            
            url_data = await _proxy(
                "POST",
                "/api/v3/play",
                json={"songId": song_id, "platform": plat, "quality": "128k"}
            )
            url = url_data.get("data", {}).get("url")
            if not url:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cannot get playback URL for song {song['name']}"
                )
            
            result = await client.play_url(url, req.device_id, _type=2)

        pl["current"] = next_idx
        return {
            "device_id": req.device_id,
            "url": url,
            "result": result,
            "current": song,
            "index": next_idx,
            "total": len(songs),
        }
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play next: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/prev")
async def play_prev(req: DeviceRequest):
    """Go back to the previous song in the server-side playlist."""
    try:
        async with XiaoAiClient() as client:
            pl = _playlists.get(req.device_id)
            if not pl or not pl["songs"]:
                raise HTTPException(
                    status_code=404,
                    detail="No playlist for this device. Use POST /api/music/play first.",
                )
            songs = pl["songs"]
            prev_idx = (pl["current"] - 1) % len(songs)
            song = songs[prev_idx]
            
            # Get the song URL
            plat = song["platform"]
            song_id = song["id"]
            _log.info("Getting URL for previous song %s (platform=%s, id=%s)", song["name"], plat, song_id)
            
            url_data = await _proxy(
                "POST",
                "/api/v3/play",
                json={"songId": song_id, "platform": plat, "quality": "128k"}
            )
            url = url_data.get("data", {}).get("url")
            if not url:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cannot get playback URL for song {song['name']}"
                )
            
            result = await client.play_url(url, req.device_id, _type=2)

        pl["current"] = prev_idx
        return {
            "device_id": req.device_id,
            "url": url,
            "result": result,
            "current": song,
            "index": prev_idx,
            "total": len(songs),
        }
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play previous: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/pause")
async def pause_music(req: DeviceRequest):
    """Pause playback via voice command."""
    try:
        async with XiaoAiClient() as client:
            result = await client.send_command("暂停", req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/resume")
async def resume_music(req: DeviceRequest):
    """Resume playback via voice command."""
    try:
        async with XiaoAiClient() as client:
            result = await client.send_command("继续播放", req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/voice-command")
async def voice_command(req: VoiceCommandRequest):
    """Parse and execute a natural-language voice command.

    - "播放/打开 [平台] [排行榜名称]" → load chart and play via voice command
    - Any other text → relay as raw voice command to the speaker
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="text must not be empty")

    # Chart play pattern: contains 榜 or 排行
    if re.search(r"(榜|排行)", text):
        platform_hint, chart_keyword = _parse_chart_command(text)
        plat = platform_hint or config.MUSIC_DEFAULT_PLATFORM
        _log.info(
            "VoiceCommand: chart intent detected, platform=%s keyword=%r",
            plat,
            chart_keyword,
        )
        charts_data = await _proxy("GET", f"/api/v3/{plat}/ranks")
        chart_list: list[dict] = charts_data.get("data", {}).get("list", []) or []
        matched = _find_chart(chart_list, chart_keyword)
        if not matched:
            raise HTTPException(
                status_code=404, detail=f"找不到匹配的排行榜：{chart_keyword!r}"
            )
        rank_id = str(matched.get("id", ""))
        songs_data = await _proxy(
            "GET", f"/api/v3/{plat}/rank/{rank_id}", params={"page": 1, "limit": 50}
        )
        songs_raw: list[dict] = songs_data.get("data", {}).get("list", []) or []
        if not songs_raw:
            raise HTTPException(status_code=404, detail="排行榜暂无歌曲")
        songs = [
            SongItem(
                id=str(s.get("id", "")),
                name=str(s.get("name", "")),
                singer=str(s.get("singer", "")),
                platform=plat,
            )
            for s in songs_raw
        ]
        first = songs[0]
        cmd = (
            f"播放{first.singer}的{first.name}" if first.singer else f"播放{first.name}"
        )
        try:
            async with XiaoAiClient() as client:
                # did = await client._resolve_device_id(req.device_id)
                result = await client.send_command(cmd, req.device_id)
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
        _playlists[req.device_id] = {
            "songs": [s.model_dump() for s in songs],
            "current": 0,
            "device_id": req.device_id,
        }
        _log.info(
            "VoiceCommand: playing chart %r for device %s (%d songs)",
            matched.get("name"),
            req.device_id,
            len(songs),
        )
        return {
            "action": "play_chart",
            "chart": matched.get("name"),
            "platform": plat,
            "device_id": req.device_id,
            "command": cmd,
            "result": result,
            "index": 0,
            "total": len(songs),
        }

    # Fallback: relay as raw voice command to the speaker
    _log.info("VoiceCommand: relaying raw command %r", text)
    try:
        async with XiaoAiClient() as client:
            result = await client.send_command(text, req.device_id)
        return {"action": "command", "command": text, "result": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/announce-search")
async def announce_search(req: AnnounceSearchRequest):
    """Send TTS to the speaker announcing search result count."""
    if req.count <= 0:
        raise HTTPException(status_code=422, detail="count must be > 0")
    tts_text = f"搜索到{req.count}首{req.query}的歌曲，是否播放？"
    _log.info("AnnounceSearch: TTS %r", tts_text)
    try:
        async with XiaoAiClient() as client:
            result = await client.text_to_speech(tts_text, req.device_id)
        return {"tts": tts_text, "result": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/playlist")
async def get_playlist(device_id: str | None = None):
    """Return the current playlist state for a device."""
    did: str | None
    if device_id:
        did = device_id
    elif config.MI_DID:
        did = config.MI_DID
    else:
        return {"device_id": None, "songs": [], "current": -1, "total": 0}

    pl = _playlists.get(did)
    if not pl:
        return {"device_id": did, "songs": [], "current": -1, "total": 0}
    return {
        "device_id": pl["device_id"],
        "songs": pl["songs"],
        "current": pl["current"],
        "total": len(pl["songs"]),
    }
