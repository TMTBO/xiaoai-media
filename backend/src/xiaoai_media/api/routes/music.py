from __future__ import annotations

import asyncio
import logging
import re
from difflib import get_close_matches
from typing import Any
from urllib.parse import quote

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


def _make_proxy_url(original_url: str) -> str:
    """Convert a music platform URL to a proxy URL that the speaker can access.

    Music platform URLs often have anti-hotlinking protection that blocks direct
    access from speakers. The proxy endpoint adds necessary headers and forwards
    the stream to the speaker.

    Args:
        original_url: Original music URL from platform (e.g., https://music.qq.com/xxx.mp3)

    Returns:
        Proxy URL (e.g., http://192.168.1.100:8000/api/proxy/stream?url=https%3A%2F%2F...)

    Example:
        >>> _make_proxy_url("https://music.qq.com/song.mp3")
        'http://192.168.1.100:8000/api/proxy/stream?url=https%3A%2F%2Fmusic.qq.com%2Fsong.mp3'
    """
    proxy_url = f"{config.SERVER_BASE_URL}/api/proxy/stream?url={quote(original_url)}"
    _log.debug("Converted URL to proxy: %s -> %s", original_url[:100], proxy_url[:100])
    return proxy_url


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


class SongQuality(BaseModel):
    type: str  # e.g. '128k', '320k', 'flac'
    format: str = "mp3"
    size: int | str = 0  # bytes or human-readable string, e.g. '9.15M'


class SongMeta(BaseModel):
    albumName: str = ""
    picUrl: str = ""
    songId: int | str = 0


class SongItem(BaseModel):
    id: str
    name: str
    singer: str
    platform: str
    qualities: list[SongQuality] = []
    interval: int = 0  # duration in seconds
    meta: SongMeta = SongMeta()


class PlayRequest(BaseModel):
    index: int = 0
    device_id: str | None = None


class SyncPlaylistRequest(BaseModel):
    songs: list[SongItem]
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
# Play URL resolution with quality fallback
# ---------------------------------------------------------------------------


def _parse_size(size: int | str) -> int:
    """Convert a size value to bytes. Supports int or strings like '9.15M', '3.2K', '27.3MB', '165.9MB'."""
    if isinstance(size, int):
        return size
    s = str(size).strip().upper().rstrip("B")  # strip trailing 'B' so MB→M, KB→K, GB→G
    try:
        if s.endswith("G"):
            return int(float(s[:-1]) * 1024**3)
        if s.endswith("M"):
            return int(float(s[:-1]) * 1024**2)
        if s.endswith("K"):
            return int(float(s[:-1]) * 1024)
        return int(float(s))
    except ValueError:
        return 0


async def _get_play_url_with_fallback(song: SongItem | dict) -> dict | None:
    """Fetch a playable URL from the music API, trying qualities from highest to lowest.

    Mirrors the JavaScript ``getPlayUrlWithFallback`` logic:
    - Sort qualities by size descending (highest quality first).
    - Try each quality in order; skip on error or missing URL.
    - Fall back to a single '128k/mp3' attempt if no qualities are declared.
    Returns a dict ``{url, lyric, quality}`` or ``None`` if all attempts fail.
    """
    if isinstance(song, dict):
        song_id = song.get("id", "")
        platform = song.get("platform", "")
        name = song.get("name", "")
        singer = song.get("singer", "")
        interval = song.get("interval", 0)
        meta = song.get("meta") or {}
        album_name = meta.get("albumName", "") if isinstance(meta, dict) else ""
        pic_url = meta.get("picUrl", "") if isinstance(meta, dict) else ""
        song_platform_id = meta.get("songId", 0) if isinstance(meta, dict) else 0
        qualities_raw: list[dict] = song.get("qualities") or []
    else:
        song_id = song.id
        platform = song.platform
        name = song.name
        singer = song.singer
        interval = song.interval
        album_name = song.meta.albumName
        pic_url = song.meta.picUrl
        song_platform_id = song.meta.songId
        qualities_raw = [q.model_dump() for q in song.qualities]

    qualities = (
        qualities_raw
        if qualities_raw
        else [{"type": "128k", "format": "mp3", "size": 0}]
    )

    # Sort by size descending — prefer higher quality
    qualities_sorted = sorted(
        qualities, key=lambda q: _parse_size(q.get("size", 0)), reverse=True
    )

    for q in qualities_sorted:
        quality_type = q.get("type", "128k")
        quality_format = q.get("format", "mp3")
        _log.info(
            "MusicAPI: trying quality=%s format=%s for %s - %s",
            quality_type,
            quality_format,
            singer,
            name,
        )
        try:
            data = await _proxy(
                "POST",
                "/api/v3/play",
                json={
                    "songId": song_id,
                    "platform": platform,
                    "quality": quality_type,
                    "format": quality_format,
                    "name": name,
                    "singer": singer,
                    "interval": interval,
                    "size": q.get("size", 0),
                    "albumName": album_name,
                    "picUrl": pic_url,
                    "song_platform_id": song_platform_id,
                },
            )
            url = data.get("data", {}).get("url") if data.get("code") == 0 else None
            if url:
                _log.info("MusicAPI: quality=%s succeeded", quality_type)
                return {
                    "url": url,
                    "lyric": data.get("data", {}).get("lyric", ""),
                    "quality": quality_type,
                }
            _log.warning(
                "MusicAPI: quality=%s returned no URL (code=%s)",
                quality_type,
                data.get("code"),
            )
        except HTTPException as e:
            _log.warning(
                "MusicAPI: quality=%s request failed: %s", quality_type, e.detail
            )

    _log.error("MusicAPI: all qualities failed for %s - %s", singer, name)
    return None


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


@router.post("/playlist")
async def sync_playlist(req: SyncPlaylistRequest):
    """Sync (replace) the server-side playlist for a device."""
    if not req.songs:
        raise HTTPException(status_code=422, detail="songs must not be empty")
    pl = _playlists.get(req.device_id) or {}
    _playlists[req.device_id] = {
        "songs": [s.model_dump() for s in req.songs],
        "current": pl.get("current", 0),
        "device_id": req.device_id,
    }
    _log.info("Playlist synced for device %s: %d songs", req.device_id, len(req.songs))
    return {
        "device_id": req.device_id,
        "total": len(req.songs),
        "current": _playlists[req.device_id]["current"],
    }


async def _play_song_at_index(
    device_id: str, index: int, stop_first: bool = False, action_name: str = "play"
) -> dict:
    """
    Common logic for playing a song at a specific index.

    Args:
        device_id: Device ID to play on
        index: Index of the song in the playlist
        stop_first: Whether to stop current playback before playing
        action_name: Name of the action for logging (play/next/prev)

    Returns:
        Response dict with playback info
    """
    pl = _playlists.get(device_id)
    if not pl or not pl.get("songs"):
        raise HTTPException(
            status_code=404,
            detail="No playlist for this device. Use POST /api/music/playlist first.",
        )

    songs = pl["songs"]
    if not (0 <= index < len(songs)):
        raise HTTPException(status_code=422, detail="index out of range")

    song = songs[index]
    _log.info(
        "Getting URL for %s song %s (platform=%s, id=%s)",
        action_name,
        song["name"],
        song["platform"],
        song["id"],
    )

    # Get playback URL with quality fallback
    play_info = await _get_play_url_with_fallback(song)
    if not play_info:
        raise HTTPException(
            status_code=404,
            detail=f"Cannot get playback URL for song {song['name']}: all qualities failed",
        )

    original_url = play_info["url"]
    _log.info(
        "Got original playback URL (quality=%s): %s",
        play_info["quality"],
        original_url[:200],
    )

    # Convert to proxy URL
    url = _make_proxy_url(original_url)

    async with XiaoAiClient() as client:
        # Stop current playback if requested
        if stop_first:
            try:
                _log.debug("Stopping current playback before playing new song...")
                await client.player_stop(device_id)
                _log.debug("Current playback stopped")
                await asyncio.sleep(0.5)
            except Exception as e:
                _log.warning(
                    "Failed to stop current playback (may not be playing): %s", e
                )

        # Play the new URL
        _log.info("About to play URL: %s", url[:200])
        result = await client.play_url(url, device_id, _type=1)
        _log.info("Play result: %s", result)

    # Update current index
    pl["current"] = index
    _log.info(
        "Playing device %s: index=%d/%d song=%s",
        device_id,
        index,
        len(songs),
        song["name"],
    )

    return {
        "device_id": device_id,
        "url": url,
        "result": result,
        "current": song,
        "index": index,
        "total": len(songs),
    }


@router.post("/play")
async def play_music(req: PlayRequest):
    """Play the song at the given index from the server-side playlist."""
    try:
        return await _play_song_at_index(
            req.device_id, req.index, stop_first=True, action_name="play"
        )
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play music: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/next")
async def play_next(req: DeviceRequest):
    """Advance to the next song in the server-side playlist."""
    try:
        pl = _playlists.get(req.device_id)
        if not pl or not pl.get("songs"):
            raise HTTPException(
                status_code=404,
                detail="No playlist for this device. Use POST /api/music/play first.",
            )
        next_idx = (pl["current"] + 1) % len(pl["songs"])
        return await _play_song_at_index(req.device_id, next_idx, action_name="next")
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play next: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/prev")
async def play_prev(req: DeviceRequest):
    """Go back to the previous song in the server-side playlist."""
    try:
        pl = _playlists.get(req.device_id)
        if not pl or not pl.get("songs"):
            raise HTTPException(
                status_code=404,
                detail="No playlist for this device. Use POST /api/music/play first.",
            )
        prev_idx = (pl["current"] - 1) % len(pl["songs"])
        return await _play_song_at_index(req.device_id, prev_idx, action_name="prev")
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play previous: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/pause")
async def pause_music(req: DeviceRequest):
    """Pause playback using the new player_pause API."""
    try:
        async with XiaoAiClient() as client:
            result = await client.player_pause(req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/resume")
async def resume_music(req: DeviceRequest):
    """Resume playback using the new player_play API."""
    try:
        async with XiaoAiClient() as client:
            result = await client.player_play(req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stop")
async def stop_music(req: DeviceRequest):
    """Stop playback using the new player_stop API."""
    try:
        async with XiaoAiClient() as client:
            result = await client.player_stop(req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/status")
async def get_player_status(device_id: str | None = None):
    """Get current player status."""
    try:
        async with XiaoAiClient() as client:
            result = await client.player_get_status(device_id)
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
    pl = _playlists.get(device_id)
    if not pl:
        return {"device_id": device_id, "songs": [], "current": -1, "total": 0}
    return {
        "device_id": pl["device_id"],
        "songs": pl["songs"],
        "current": pl["current"],
        "total": len(pl["songs"]),
    }
