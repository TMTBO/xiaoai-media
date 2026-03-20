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
from xiaoai_media.player import get_player

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/music", tags=["music"])

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


# URL conversion helpers moved to player.py


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


class LoadFromSearchRequest(BaseModel):
    query: str
    device_id: str | None = None
    platform: str | None = None
    auto_play: bool = True  # Whether to start playing immediately


class LoadFromChartRequest(BaseModel):
    chart_id: str | None = None  # If None, will try to match chart_keyword
    chart_keyword: str | None = None  # Natural language keyword like "热歌榜"
    device_id: str | None = None
    platform: str | None = None
    auto_play: bool = True  # Whether to start playing immediately


class LoadFromPlaylistRequest(BaseModel):
    playlist_id: str
    device_id: str | None = None
    auto_play: bool = True  # Whether to start playing immediately


# ---------------------------------------------------------------------------
# Play URL resolution with quality fallback
# ---------------------------------------------------------------------------
# These functions moved to player.py


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
# Playlist management functions moved to player.py


@router.post("/playlist")
async def sync_playlist(req: SyncPlaylistRequest):
    """Sync (replace) the server-side playlist for a device."""
    if not req.songs:
        raise HTTPException(status_code=422, detail="songs must not be empty")

    player = get_player()
    player.set_playlist(
        req.device_id,
        [s.model_dump() for s in req.songs],
        current_index=0,
    )

    _log.info("Playlist synced for device %s: %d songs", req.device_id, len(req.songs))
    return {
        "device_id": req.device_id,
        "total": len(req.songs),
        "current": 0,
    }


@router.post("/play")
async def play_music(req: PlayRequest):
    """Play the song at the given index from the server-side playlist."""
    try:
        player = get_player()
        return await player.play_at_index(
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
        player = get_player()
        return await player.play_next(req.device_id)
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play next: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/prev")
async def play_prev(req: DeviceRequest):
    """Go back to the previous song in the server-side playlist."""
    try:
        player = get_player()
        return await player.play_prev(req.device_id)
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to play previous: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/pause")
async def pause_music(req: DeviceRequest):
    """Pause playback using the player_pause API."""
    try:
        player = get_player()
        return await player.pause(req.device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/resume")
async def resume_music(req: DeviceRequest):
    """Resume playback using the player_play API."""
    try:
        player = get_player()
        return await player.resume(req.device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stop")
async def stop_music(req: DeviceRequest):
    """Stop playback using the player_stop API."""
    try:
        player = get_player()
        return await player.stop(req.device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/status")
async def get_player_status(device_id: str | None = None):
    """Get current player status."""
    try:
        player = get_player()
        return await player.get_status(device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------------------------------------------------------------------
# Playlist loading from different sources
# ---------------------------------------------------------------------------


@router.post("/load-from-search")
async def load_from_search(req: LoadFromSearchRequest):
    """Load playlist from search results and optionally start playing.

    This allows users to search for songs and load them into the playlist for voice control.

    Example:
        POST /api/music/load-from-search
        {
            "query": "周杰伦",
            "device_id": "xxx",
            "platform": "tx",
            "auto_play": true
        }
    """
    if not req.query.strip():
        raise HTTPException(status_code=422, detail="query must not be empty")

    plat = _platform(req.platform)

    # Search for music
    _log.info("Loading playlist from search: query=%s platform=%s", req.query, plat)
    search_data = await _proxy(
        "POST",
        "/api/v3/search",
        json={"platform": plat, "query": req.query.strip(), "page": 1, "limit": 50},
    )

    songs_raw: list[dict] = search_data.get("data", {}).get("list", []) or []
    if not songs_raw:
        raise HTTPException(status_code=404, detail=f"没有找到歌曲: {req.query}")

    # Convert to SongItem objects
    songs = []
    for s in songs_raw:
        try:
            songs.append(
                SongItem(
                    id=str(s.get("id", "")),
                    name=str(s.get("name", "")),
                    singer=str(s.get("singer", "")),
                    platform=plat,
                    qualities=s.get("qualities", []),
                    interval=s.get("interval", 0),
                    meta=s.get("meta", {}),
                )
            )
        except Exception as e:
            _log.warning("Failed to parse song: %s", e)
            continue

    if not songs:
        raise HTTPException(status_code=404, detail="Failed to parse search results")

    # Load into playlist
    player = get_player()
    player.set_playlist(
        req.device_id,
        [s.model_dump() for s in songs],
        current_index=0,
    )
    _log.info(
        "Loaded %d songs from search into playlist for device %s",
        len(songs),
        req.device_id,
    )

    result = {
        "action": "load_from_search",
        "query": req.query,
        "platform": plat,
        "device_id": req.device_id,
        "total": len(songs),
        "songs": [
            {"name": s.name, "singer": s.singer} for s in songs[:10]
        ],  # Preview first 10
    }

    # Auto play if requested
    if req.auto_play:
        _log.info("Auto-playing first song from search results")
        try:
            play_result = await player.play_at_index(
                req.device_id, 0, stop_first=True, action_name="play"
            )
            result["play_result"] = play_result
        except Exception as e:
            _log.error("Auto-play failed: %s", e, exc_info=True)
            result["play_error"] = str(e)

    return result


@router.post("/load-from-chart")
async def load_from_chart(req: LoadFromChartRequest):
    """Load playlist from a music chart and optionally start playing.

    This allows users to load entire charts (rankings) for voice control.

    Example:
        POST /api/music/load-from-chart
        {
            "chart_keyword": "热歌榜",
            "device_id": "xxx",
            "platform": "tx",
            "auto_play": true
        }
    """
    if not req.chart_id and not req.chart_keyword:
        raise HTTPException(
            status_code=422,
            detail="Either chart_id or chart_keyword must be provided",
        )

    plat = _platform(req.platform)

    # Get chart list
    _log.info("Loading playlist from chart: platform=%s", plat)
    charts_data = await _proxy("GET", f"/api/v3/{plat}/ranks")
    chart_list: list[dict] = charts_data.get("data", {}).get("list", []) or []

    if not chart_list:
        raise HTTPException(
            status_code=404, detail=f"No charts available for platform {plat}"
        )

    # Find the chart
    matched_chart = None
    if req.chart_id:
        # Find by ID
        for c in chart_list:
            if str(c.get("id", "")) == req.chart_id:
                matched_chart = c
                break
    else:
        # Find by keyword
        matched_chart = _find_chart(chart_list, req.chart_keyword or "")

    if not matched_chart:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {req.chart_id or req.chart_keyword}",
        )

    rank_id = str(matched_chart.get("id", ""))
    chart_name = matched_chart.get("name", "")

    # Get chart songs
    _log.info("Loading songs from chart: %s (id=%s)", chart_name, rank_id)
    songs_data = await _proxy(
        "GET",
        f"/api/v3/{plat}/rank/{rank_id}",
        params={"page": 1, "limit": 50},
    )

    songs_raw: list[dict] = songs_data.get("data", {}).get("list", []) or []
    if not songs_raw:
        raise HTTPException(status_code=404, detail=f"No songs in chart: {chart_name}")

    # Convert to SongItem objects
    songs = []
    for s in songs_raw:
        try:
            songs.append(
                SongItem(
                    id=str(s.get("id", "")),
                    name=str(s.get("name", "")),
                    singer=str(s.get("singer", "")),
                    platform=plat,
                    qualities=s.get("qualities", []),
                    interval=s.get("interval", 0),
                    meta=s.get("meta", {}),
                )
            )
        except Exception as e:
            _log.warning("Failed to parse song: %s", e)
            continue

    if not songs:
        raise HTTPException(status_code=404, detail="Failed to parse chart songs")

    # Load into playlist
    player = get_player()
    player.set_playlist(
        req.device_id,
        [s.model_dump() for s in songs],
        current_index=0,
    )
    _log.info(
        "Loaded %d songs from chart '%s' into playlist for device %s",
        len(songs),
        chart_name,
        req.device_id,
    )

    result = {
        "action": "load_from_chart",
        "chart_name": chart_name,
        "chart_id": rank_id,
        "platform": plat,
        "device_id": req.device_id,
        "total": len(songs),
        "songs": [
            {"name": s.name, "singer": s.singer} for s in songs[:10]
        ],  # Preview first 10
    }

    # Auto play if requested
    if req.auto_play:
        _log.info("Auto-playing first song from chart")
        try:
            play_result = await player.play_at_index(
                req.device_id, 0, stop_first=True, action_name="play"
            )
            result["play_result"] = play_result
        except Exception as e:
            _log.error("Auto-play failed: %s", e, exc_info=True)
            result["play_error"] = str(e)

    return result


@router.post("/load-from-playlist")
async def load_from_playlist(req: LoadFromPlaylistRequest):
    """Load playlist from a saved playlist (from playlist.py) and optionally start playing.

    This allows users to load their saved playlists for voice control.

    Example:
        POST /api/music/load-from-playlist
        {
            "playlist_id": "音乐_1234567890",
            "device_id": "xxx",
            "auto_play": true
        }
    """
    # Import playlist loading functions
    from xiaoai_media.api.routes.playlist import _load_playlists

    playlists = _load_playlists()
    if req.playlist_id not in playlists:
        raise HTTPException(
            status_code=404,
            detail=f"Playlist not found: {req.playlist_id}",
        )

    playlist = playlists[req.playlist_id]

    if not playlist.items:
        raise HTTPException(
            status_code=400,
            detail=f"Playlist is empty: {playlist.name}",
        )

    _log.info(
        "Loading playlist '%s' with %d items for device %s",
        playlist.name,
        len(playlist.items),
        req.device_id,
    )

    # Convert playlist items to SongItem format
    # Note: Playlist items may not have all song metadata, so we create minimal SongItems
    songs = []
    for item in playlist.items:
        try:
            # Create a SongItem from PlaylistItem
            # If item has url, use it directly; otherwise we'll need to fetch it later
            songs.append(
                SongItem(
                    id=item.url
                    or f"playlist_{playlist.id}_{len(songs)}",  # Use URL as ID or generate one
                    name=item.title,
                    singer=item.artist,
                    platform="custom",  # Mark as custom source
                    qualities=[],  # No quality info for playlist items
                    interval=item.duration,
                    meta=SongMeta(albumName=item.album, picUrl=item.cover_url),
                )
            )
        except Exception as e:
            _log.warning("Failed to convert playlist item to SongItem: %s", e)
            continue

    if not songs:
        raise HTTPException(
            status_code=400,
            detail="Failed to convert playlist items",
        )

    # Load into playlist
    player = get_player()
    player.set_playlist(
        req.device_id,
        [s.model_dump() for s in songs],
        current_index=0,
        source="playlist",
        source_id=req.playlist_id,
        source_name=playlist.name,
    )
    _log.info(
        "Loaded %d songs from playlist '%s' for device %s",
        len(songs),
        playlist.name,
        req.device_id,
    )

    result = {
        "action": "load_from_playlist",
        "playlist_name": playlist.name,
        "playlist_id": req.playlist_id,
        "device_id": req.device_id,
        "total": len(songs),
        "songs": [
            {"name": s.name, "singer": s.singer} for s in songs[:10]
        ],  # Preview first 10
    }

    # Auto play if requested
    if req.auto_play:
        _log.info("Auto-playing first item from playlist")
        try:
            # For custom playlists, we need to handle URL differently
            # Since playlist items might use custom_params to get URLs
            # For now we'll attempt to play, but it might need special handling
            play_result = await player.play_at_index(
                req.device_id, 0, stop_first=True, action_name="play"
            )
            result["play_result"] = play_result
        except Exception as e:
            _log.error("Auto-play failed: %s", e, exc_info=True)
            result["play_error"] = str(e)
            result["play_error_note"] = (
                "Playlist items may require custom URL resolution. "
                "Please ensure playlist items have valid URLs or implement custom URL fetching."
            )

    return result


@router.post("/voice-command")
async def voice_command(req: VoiceCommandRequest):
    """Parse and execute a natural-language voice command.

    Supported patterns:
    - "播放/打开 [平台] [排行榜名称]" → load chart and play
    - "播放 [播单名称]" → load saved playlist and play
    - "搜索 [关键词]" → search and load results
    - Any other text → relay as raw voice command to the speaker
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="text must not be empty")

    # Pattern 1: Playlist play - "播放音乐播单", "打开我的有声书"
    # Check for playlist keywords
    if re.search(r"播单|列表", text):
        _log.info("VoiceCommand: playlist intent detected for text=%r", text)
        try:
            # Extract playlist name/keyword from command
            playlist_keyword = re.sub(r"^(播放|打开|加载)\s*", "", text)
            playlist_keyword = re.sub(r"(播单|列表)\s*$", "", playlist_keyword).strip()

            # Load playlists and find matching one
            from xiaoai_media.api.routes.playlist import _load_playlists

            playlists = _load_playlists()
            matched_playlist = None

            # Try to match by name or voice keywords
            for pid, playlist in playlists.items():
                # Check if playlist name contains keyword
                if playlist_keyword.lower() in playlist.name.lower():
                    matched_playlist = (pid, playlist)
                    break
                # Check voice keywords
                for vk in playlist.voice_keywords:
                    if vk.lower() in text.lower():
                        matched_playlist = (pid, playlist)
                        break
                if matched_playlist:
                    break

            if not matched_playlist:
                raise HTTPException(
                    status_code=404,
                    detail=f"找不到匹配的播单: {playlist_keyword}",
                )

            playlist_id, playlist = matched_playlist

            # Load the playlist
            load_result = await load_from_playlist(
                LoadFromPlaylistRequest(
                    playlist_id=playlist_id,
                    device_id=req.device_id,
                    auto_play=True,
                )
            )

            _log.info(
                "VoiceCommand: loaded playlist %r for device %s",
                playlist.name,
                req.device_id,
            )

            return {
                "action": "play_playlist",
                "playlist_name": playlist.name,
                "playlist_id": playlist_id,
                "device_id": req.device_id,
                "result": load_result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to load playlist: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    # Pattern 2: Chart play - contains 榜 or 排行
    if re.search(r"(榜|排行)", text):
        platform_hint, chart_keyword = _parse_chart_command(text)
        plat = platform_hint or config.MUSIC_DEFAULT_PLATFORM
        _log.info(
            "VoiceCommand: chart intent detected, platform=%s keyword=%r",
            plat,
            chart_keyword,
        )

        try:
            # Use the new load_from_chart endpoint
            load_result = await load_from_chart(
                LoadFromChartRequest(
                    chart_keyword=chart_keyword,
                    device_id=req.device_id,
                    platform=plat,
                    auto_play=True,
                )
            )

            return {
                "action": "play_chart",
                "chart_name": load_result.get("chart_name"),
                "platform": plat,
                "device_id": req.device_id,
                "result": load_result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to load chart: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    # Pattern 3: Search and play - "搜索周杰伦", "播放周杰伦的歌"
    # This pattern should be more specific to avoid false positives
    search_match = re.match(r"^(搜索|查找)(.+)$", text)
    if search_match:
        search_query = search_match.group(2).strip()
        _log.info("VoiceCommand: search intent detected, query=%r", search_query)

        try:
            # Use the new load_from_search endpoint
            load_result = await load_from_search(
                LoadFromSearchRequest(
                    query=search_query,
                    device_id=req.device_id,
                    auto_play=True,
                )
            )

            return {
                "action": "search_and_play",
                "query": search_query,
                "device_id": req.device_id,
                "result": load_result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to search and load: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

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
    player = get_player()
    pl = player.get_playlist(device_id)
    if not pl:
        return {"device_id": device_id, "songs": [], "current": -1, "total": 0}
    return {
        "device_id": pl["device_id"],
        "songs": pl["songs"],
        "current": pl["current"],
        "total": len(pl["songs"]),
    }
