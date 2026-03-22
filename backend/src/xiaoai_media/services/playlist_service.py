"""
播单业务逻辑服务
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient
from xiaoai_media.services.playlist_models import (
    AddItemRequest,
    ContinuePlayRequest,
    CreatePlaylistRequest,
    PlayModeRequest,
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

        # 构建完整的参数字典
        # 注意：custom_params 中的值会覆盖 PlaylistItem 的基础字段
        # 这样可以确保 get_audio_url 接收到正确的字段名（如 id, name, singer）
        params = {
            "title": item.title,
            "artist": item.artist,
            "album": item.album,
            "audio_id": item.audio_id,
            "interval": item.interval,
            "pic_url": item.pic_url,
            **item.custom_params,  # custom_params 中的值会覆盖上面的默认值
        }

        _log.info("Calling get_audio_url with params: %s", {k: v for k, v in params.items() if k not in ['qualities', 'meta']})

        # 调用函数获取 URL
        if asyncio.iscoroutinefunction(get_audio_url):
            url = await get_audio_url(params)
        else:
            url = get_audio_url(params)

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
            interval=req.interval,
            pic_url=req.pic_url,
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
        if req.interval is not None:
            playlist.interval = req.interval
        if req.pic_url is not None:
            playlist.pic_url = req.pic_url
        if req.play_mode is not None:
            if req.play_mode not in ["loop", "single", "random"]:
                raise ValueError(f"Invalid play_mode: {req.play_mode}")
            playlist.play_mode = req.play_mode
        if req.current_index is not None:
            if req.current_index < 0 or req.current_index >= len(playlist.items):
                raise ValueError(f"Invalid current_index: {req.current_index}")
            playlist.current_index = req.current_index

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

        # 更新当前播放索引
        playlist.current_index = req.start_index
        playlist.updated_at = datetime.now().isoformat()
        PlaylistStorage.save_playlist(playlist)

        # 保存当前播放的播单ID到状态服务
        from xiaoai_media.services.state_service import get_state_service
        state_service = get_state_service()
        state_service.set(f"current_playlist_{req.device_id or 'default'}", playlist_id)

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

            # 直接使用 play_url 播放
            result = await client.play_url(play_url, req.device_id, _type=1)
            _log.info("Play URL result: %s", result)

        return {
            "message": "Playing",
            "playlist": playlist.name,
            "item": item.model_dump(),
            "index": req.start_index,
            "total": len(playlist.items),
            "play_mode": playlist.play_mode,
        }

    @staticmethod
    async def continue_playlist(playlist_id: str, req: ContinuePlayRequest) -> dict:
        """继续播放播单（从当前索引位置开始）"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if not playlist.items:
            raise ValueError("Playlist is empty")

        # 从当前索引开始播放
        return await PlaylistService.play_playlist(
            playlist_id,
            PlayPlaylistRequest(
                device_id=req.device_id,
                start_index=playlist.current_index,
                announce=req.announce,
            ),
        )

    @staticmethod
    async def stop_playlist(playlist_id: str, device_id: str | None = None) -> dict:
        """停止播放播单"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        # 发送停止命令
        async with XiaoAiClient() as client:
            await client.player_stop(device_id)

        _log.info("Stopped playlist: %s", playlist.name)
        return {
            "message": "Stopped",
            "playlist": playlist.name,
        }

    @staticmethod
    def set_play_mode(playlist_id: str, req: PlayModeRequest) -> Playlist:
        """设置播放模式"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if req.play_mode not in ["loop", "single", "random"]:
            raise ValueError(f"Invalid play_mode: {req.play_mode}")

        playlist.play_mode = req.play_mode
        playlist.updated_at = datetime.now().isoformat()
        PlaylistStorage.save_playlist(playlist)

        _log.info("Set play mode for playlist %s: %s", playlist.name, req.play_mode)
        return playlist

    @staticmethod
    async def play_next_in_playlist(playlist_id: str, device_id: str | None = None) -> dict:
        """播放播单中的下一首（根据播放模式）"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if not playlist.items:
            raise ValueError("Playlist is empty")

        # 根据播放模式计算下一首的索引
        if playlist.play_mode == "single":
            # 单曲循环：保持当前索引
            next_index = playlist.current_index
        elif playlist.play_mode == "random":
            # 随机播放：随机选择一首
            next_index = random.randint(0, len(playlist.items) - 1)
        else:  # loop
            # 列表循环：下一首，到末尾后回到开头
            next_index = (playlist.current_index + 1) % len(playlist.items)

        return await PlaylistService.play_playlist(
            playlist_id,
            PlayPlaylistRequest(device_id=device_id, start_index=next_index, announce=False),
        )

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
