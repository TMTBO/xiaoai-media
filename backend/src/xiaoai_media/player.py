"""
播放列表播放器模块

提供统一的播放列表管理和播放控制功能。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import quote

import aiohttp
from fastapi import HTTPException

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient

_log = logging.getLogger(__name__)


class PlaylistPlayer:
    """播放列表播放器

    管理每个设备的播放列表，并提供统一的播放控制接口。
    """

    def __init__(self):
        """初始化播放器"""
        # 播放列表存储: device_id -> {songs, current, device_id, ...}
        self._playlists: dict[str, dict[str, Any]] = {}

    def get_playlist(self, device_id: str) -> dict[str, Any] | None:
        """获取设备的播放列表

        Args:
            device_id: 设备ID

        Returns:
            播放列表信息，如果不存在则返回 None
        """
        return self._playlists.get(device_id)

    def set_playlist(
        self,
        device_id: str,
        songs: list[dict],
        current_index: int = 0,
        **metadata: Any,
    ) -> dict[str, Any]:
        """设置设备的播放列表

        Args:
            device_id: 设备ID
            songs: 歌曲列表
            current_index: 当前播放索引
            **metadata: 额外的元数据（如 source, source_id, source_name）

        Returns:
            设置后的播放列表信息
        """
        playlist = {
            "songs": songs,
            "current": current_index,
            "device_id": device_id,
            **metadata,
        }
        self._playlists[device_id] = playlist
        _log.info(
            "Set playlist for device %s: %d songs, current=%d",
            device_id,
            len(songs),
            current_index,
        )
        return playlist

    def clear_playlist(self, device_id: str) -> None:
        """清除设备的播放列表

        Args:
            device_id: 设备ID
        """
        if device_id in self._playlists:
            del self._playlists[device_id]
            _log.info("Cleared playlist for device %s", device_id)

    async def play_at_index(
        self,
        device_id: str,
        index: int,
        stop_first: bool = False,
        action_name: str = "play",
    ) -> dict:
        """播放指定索引的歌曲

        Args:
            device_id: 设备ID
            index: 歌曲索引
            stop_first: 是否先停止当前播放
            action_name: 操作名称（用于日志）

        Returns:
            播放结果

        Raises:
            HTTPException: 播放列表不存在、索引越界或播放失败
        """
        pl = self._playlists.get(device_id)
        if not pl or not pl.get("songs"):
            raise HTTPException(
                status_code=404,
                detail="No playlist for this device. Load a playlist first.",
            )

        songs = pl["songs"]
        if not (0 <= index < len(songs)):
            raise HTTPException(status_code=422, detail="Index out of range")

        song = songs[index]
        _log.info(
            "Getting URL for %s song %s (platform=%s, id=%s)",
            action_name,
            song["name"],
            song["platform"],
            song["id"],
        )

        # Get playback URL with quality fallback
        play_info = await self._get_play_url_with_fallback(song)
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
        url = self._make_proxy_url(original_url)

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

    async def play_next(self, device_id: str) -> dict:
        """播放下一首

        Args:
            device_id: 设备ID

        Returns:
            播放结果
        """
        pl = self._playlists.get(device_id)
        if not pl or not pl.get("songs"):
            raise HTTPException(
                status_code=404,
                detail="No playlist for this device.",
            )
        next_idx = (pl["current"] + 1) % len(pl["songs"])
        return await self.play_at_index(device_id, next_idx, action_name="next")

    async def play_prev(self, device_id: str) -> dict:
        """播放上一首

        Args:
            device_id: 设备ID

        Returns:
            播放结果
        """
        pl = self._playlists.get(device_id)
        if not pl or not pl.get("songs"):
            raise HTTPException(
                status_code=404,
                detail="No playlist for this device.",
            )
        prev_idx = (pl["current"] - 1) % len(pl["songs"])
        return await self.play_at_index(device_id, prev_idx, action_name="prev")

    async def pause(self, device_id: str) -> dict:
        """暂停播放

        Args:
            device_id: 设备ID

        Returns:
            操作结果
        """
        async with XiaoAiClient() as client:
            result = await client.player_pause(device_id)
        return result

    async def resume(self, device_id: str) -> dict:
        """继续播放

        Args:
            device_id: 设备ID

        Returns:
            操作结果
        """
        async with XiaoAiClient() as client:
            result = await client.player_play(device_id)
        return result

    async def stop(self, device_id: str) -> dict:
        """停止播放

        Args:
            device_id: 设备ID

        Returns:
            操作结果
        """
        async with XiaoAiClient() as client:
            result = await client.player_stop(device_id)
        return result

    async def get_status(self, device_id: str) -> dict:
        """获取播放状态

        Args:
            device_id: 设备ID

        Returns:
            播放状态
        """
        async with XiaoAiClient() as client:
            result = await client.player_get_status(device_id)
        return result

    # ------------------------------------------------------------------
    # Private helper methods
    # ------------------------------------------------------------------

    def _make_proxy_url(self, original_url: str) -> str:
        """将原始URL转换为代理URL

        音乐平台的URL通常有防盗链保护，无法直接从音箱访问。
        代理端点会添加必要的请求头并转发流到音箱。

        Args:
            original_url: 原始音乐URL

        Returns:
            代理URL
        """
        proxy_url = (
            f"{config.SERVER_BASE_URL}/api/proxy/stream?url={quote(original_url)}"
        )
        _log.debug(
            "Converted URL to proxy: %s -> %s", original_url[:100], proxy_url[:100]
        )
        return proxy_url

    async def _get_play_url_with_fallback(self, song: dict) -> dict | None:
        """获取播放URL，带音质降级重试

        尝试从最高音质开始，逐个降级直到找到可用的URL。

        Args:
            song: 歌曲信息字典

        Returns:
            包含 url, lyric, quality 的字典，如果全部失败则返回 None
        """
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

        qualities = (
            qualities_raw
            if qualities_raw
            else [{"type": "128k", "format": "mp3", "size": 0}]
        )

        # Sort by size descending — prefer higher quality
        qualities_sorted = sorted(
            qualities, key=lambda q: self._parse_size(q.get("size", 0)), reverse=True
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
                data = await self._proxy_music_api(
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

    async def _proxy_music_api(self, method: str, path: str, **kwargs: Any) -> dict:
        """代理请求到音乐下载服务

        Args:
            method: HTTP方法
            path: API路径
            **kwargs: 其他请求参数

        Returns:
            响应数据

        Raises:
            HTTPException: 请求失败
        """
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

    @staticmethod
    def _parse_size(size: int | str) -> int:
        """解析文件大小为字节数

        支持整数或字符串格式（如 '9.15M', '3.2K', '27.3MB'）

        Args:
            size: 文件大小

        Returns:
            字节数
        """
        if isinstance(size, int):
            return size
        s = str(size).strip().upper().rstrip("B")
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


# 全局播放器实例，供路由使用
_player = PlaylistPlayer()


def get_player() -> PlaylistPlayer:
    """获取全局播放器实例

    Returns:
        PlaylistPlayer 实例
    """
    return _player
