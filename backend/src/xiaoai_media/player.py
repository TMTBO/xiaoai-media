"""
播放列表播放器模块

提供统一的播放列表管理和播放控制功能。
"""

from __future__ import annotations

import asyncio
import logging
from xiaoai_media.logger import get_logger
from typing import Any

from fastapi import HTTPException

from xiaoai_media.api.dependencies import get_client_sync
from xiaoai_media.services.playlist_models import PlaylistItem
from xiaoai_media.services.playlist_service import PlaylistService
from xiaoai_media.playback_controller import get_controller

_log = get_logger()


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

        # Convert song dict to PlaylistItem
        playlist_item = self._song_to_playlist_item(song)

        # Get playback URL using PlaylistService (already returns proxy URL)
        try:
            url = await PlaylistService.get_item_url(playlist_item)
            _log.info("Got playback URL: %s", url[:200])
        except Exception as e:
            _log.error("Failed to get playback URL: %s", e)
            raise HTTPException(
                status_code=404,
                detail=f"Cannot get playback URL for song {song['name']}: {e}",
            )

        client = get_client_sync()
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
        client = get_client_sync()
        result = await client.player_pause(device_id)
        
        # 通知播放控制器
        controller = get_controller()
        await controller.on_play_paused(device_id)
        
        return result

    async def resume(self, device_id: str) -> dict:
        """继续播放

        Args:
            device_id: 设备ID

        Returns:
            操作结果
        """
        client = get_client_sync()
        result = await client.player_play(device_id)
        
        # 通知播放控制器
        controller = get_controller()
        await controller.on_play_resumed(device_id)
        
        return result

    async def stop(self, device_id: str) -> dict:
        """停止播放

        Args:
            device_id: 设备ID

        Returns:
            操作结果
        """
        client = get_client_sync()
        result = await client.player_stop(device_id)
        
        # 通知播放控制器
        controller = get_controller()
        await controller.on_play_stopped(device_id)
        
        return result

    async def get_status(self, device_id: str) -> dict:
        """获取播放状态

        Args:
            device_id: 设备ID

        Returns:
            播放状态
        """
        client = get_client_sync()
        result = await client.player_get_status(device_id)
        return result

    # ------------------------------------------------------------------
    # Private helper methods
    # ------------------------------------------------------------------

    @staticmethod
    def _song_to_playlist_item(song: dict) -> PlaylistItem:
        """将歌曲字典转换为 PlaylistItem

        Args:
            song: 歌曲信息字典

        Returns:
            PlaylistItem 对象
        """
        return PlaylistItem(
            title=song.get("name", ""),
            artist=song.get("singer", ""),
            album=song.get("meta", {}).get("albumName", "") if isinstance(song.get("meta"), dict) else "",
            audio_id=song.get("id", ""),
            url=None,  # 不使用预设 URL，让 get_item_url 动态获取
            custom_params={
                "type": "music",
                "id": song.get("id", ""),
                "platform": song.get("platform", ""),
                "name": song.get("name", ""),
                "singer": song.get("singer", ""),
                "interval": song.get("interval", 0),
                "qualities": song.get("qualities", []),
                "meta": song.get("meta", {}),
            },
        )


# 全局播放器实例，供路由使用
_player = PlaylistPlayer()


def get_player() -> PlaylistPlayer:
    """获取全局播放器实例

    Returns:
        PlaylistPlayer 实例
    """
    return _player
