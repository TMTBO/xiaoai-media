"""
播单业务逻辑服务
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient
from xiaoai_media.services.playlist_models import (
    AddItemRequest,
    CreatePlaylistRequest,
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    PlayPlaylistRequest,
    UpdatePlaylistRequest,
)
from xiaoai_media.services.playlist_storage import PlaylistStorage

_log = logging.getLogger(__name__)


class PlaylistService:
    """播单业务逻辑服务"""

    @staticmethod
    def generate_playlist_id(name: str) -> str:
        """生成播单 ID"""
        timestamp = str(int(time.time() * 1000))
        return f"{name[:10]}_{timestamp}"

    @staticmethod
    def make_proxy_url(original_url: str) -> str:
        """将原始 URL 转换为代理 URL"""
        proxy_url = f"{config.SERVER_BASE_URL}/api/proxy/stream?url={quote(original_url)}"
        _log.debug("Converted URL to proxy: %s -> %s", original_url[:100], proxy_url[:100])
        return proxy_url

    @staticmethod
    async def get_item_url(item: PlaylistItem) -> str:
        """获取播单项的播放 URL

        如果 item.url 存在，直接使用；
        否则调用 user_config.py 中的 get_audio_url 函数获取。
        """
        if item.url:
            return PlaylistService.make_proxy_url(item.url)

        # 尝试从 user_config.py 加载 get_audio_url 函数
        user_config_path = config.get_config_file_path(required=False)
        if not user_config_path or not user_config_path.exists():
            raise RuntimeError(
                "user_config.py not found, cannot get audio URL for item without URL"
            )

        # 动态导入 user_config
        spec = importlib.util.spec_from_file_location("user_config", user_config_path)
        if not spec or not spec.loader:
            raise RuntimeError("Failed to load user_config.py")

        user_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_config)

        # 检查是否有 get_audio_url 函数
        if not hasattr(user_config, "get_audio_url"):
            raise RuntimeError("get_audio_url function not found in user_config.py")

        get_audio_url = user_config.get_audio_url

        # 调用函数获取 URL
        if asyncio.iscoroutinefunction(get_audio_url):
            url = await get_audio_url(item.custom_params)
        else:
            url = get_audio_url(item.custom_params)

        if not url:
            raise RuntimeError(f"Failed to get audio URL for item: {item.title}")

        return PlaylistService.make_proxy_url(url)

    @staticmethod
    def list_playlists() -> dict[str, list[PlaylistIndex]]:
        """获取所有播单（仅返回索引信息）"""
        index = PlaylistStorage.load_index()
        return {
            "playlists": list(index.values()),
            "total": len(index),
        }

    @staticmethod
    def create_playlist(req: CreatePlaylistRequest) -> Playlist:
        """创建新播单"""
        playlist_id = PlaylistService.generate_playlist_id(req.name)
        now = datetime.now().isoformat()

        playlist = Playlist(
            id=playlist_id,
            name=req.name,
            type=req.type,
            description=req.description,
            voice_keywords=req.voice_keywords,
            items=[],
            created_at=now,
            updated_at=now,
        )

        PlaylistStorage.save_playlist(playlist)
        _log.info("Created playlist: %s (id=%s)", req.name, playlist_id)
        return playlist

    @staticmethod
    def get_playlist(playlist_id: str) -> Playlist | None:
        """获取指定播单（包含完整数据）"""
        return PlaylistStorage.load_playlist(playlist_id)

    @staticmethod
    def update_playlist(playlist_id: str, req: UpdatePlaylistRequest) -> Playlist:
        """更新播单信息"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if req.name is not None:
            playlist.name = req.name
        if req.type is not None:
            playlist.type = req.type
        if req.description is not None:
            playlist.description = req.description
        if req.voice_keywords is not None:
            playlist.voice_keywords = req.voice_keywords

        playlist.updated_at = datetime.now().isoformat()
        PlaylistStorage.save_playlist(playlist)

        _log.info("Updated playlist: %s", playlist_id)
        return playlist

    @staticmethod
    def delete_playlist(playlist_id: str) -> None:
        """删除播单"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        PlaylistStorage.delete_playlist(playlist_id)
        _log.info("Deleted playlist: %s", playlist_id)

    @staticmethod
    def add_items(playlist_id: str, req: AddItemRequest) -> None:
        """添加播单项"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        playlist.items.extend(req.items)
        playlist.updated_at = datetime.now().isoformat()

        PlaylistStorage.save_playlist(playlist)
        _log.info("Added %d items to playlist: %s", len(req.items), playlist_id)

    @staticmethod
    def delete_item(playlist_id: str, item_index: int) -> PlaylistItem:
        """删除播单项"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if item_index < 0 or item_index >= len(playlist.items):
            raise ValueError(f"Item index out of range: {item_index}")

        removed_item = playlist.items.pop(item_index)
        playlist.updated_at = datetime.now().isoformat()

        PlaylistStorage.save_playlist(playlist)
        _log.info("Removed item %d from playlist: %s", item_index, playlist_id)
        return removed_item

    @staticmethod
    async def play_playlist(playlist_id: str, req: PlayPlaylistRequest) -> dict:
        """播放播单"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if not playlist.items:
            raise ValueError("Playlist is empty")

        if req.start_index < 0 or req.start_index >= len(playlist.items):
            raise ValueError(f"Invalid start_index: {req.start_index}")

        # 获取要播放的项
        item = playlist.items[req.start_index]

        # 获取播放 URL
        play_url = await PlaylistService.get_item_url(item)

        _log.info(
            "Playing playlist item: %s - %s (url=%s)",
            playlist.name,
            item.title,
            play_url[:100],
        )

        # 发送播放命令
        async with XiaoAiClient() as client:
            # 如果需要播报，先播报
            if req.announce:
                announce_text = f"正在播放{playlist.name}，{item.title}"
                if item.artist:
                    announce_text += f"，{item.artist}"
                await client.send_command(announce_text, req.device_id, silent=False)
                await asyncio.sleep(1)  # 等待播报完成

            # 发送播放 URL 命令
            play_command = f"播放 {play_url}"
            await client.send_command(play_command, req.device_id, silent=True)

        return {
            "message": "Playing",
            "playlist": playlist.name,
            "item": item.model_dump(),
            "index": req.start_index,
            "total": len(playlist.items),
        }

    @staticmethod
    async def play_by_voice_command(voice_text: str, device_id: str | None = None) -> dict:
        """根据语音命令播放播单

        从索引文件中匹配唤醒词，然后加载对应的播单
        """
        # 从索引文件中查找匹配的播单
        index = PlaylistStorage.load_index()
        matched_playlist_id: str | None = None

        for playlist_id, idx in index.items():
            # 检查播单名称是否在语音文本中
            if idx.name in voice_text:
                matched_playlist_id = playlist_id
                break

            # 检查语音关键词
            for keyword in idx.voice_keywords:
                if keyword in voice_text:
                    matched_playlist_id = playlist_id
                    break

            if matched_playlist_id:
                break

        if not matched_playlist_id:
            raise ValueError(f"No playlist matched for voice command: {voice_text}")

        # 加载完整的播单数据并播放
        return await PlaylistService.play_playlist(
            matched_playlist_id,
            PlayPlaylistRequest(device_id=device_id, start_index=0, announce=True),
        )
