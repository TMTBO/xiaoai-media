"""
播单（播放列表）管理路由

支持多个播单（音乐、有声书、播客等），可通过语音命令控制播放。
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/playlists", tags=["playlists"])


def _get_playlist_file() -> Path:
    """获取播单存储文件路径"""
    storage_dir = Path(config.PLAYLIST_STORAGE_DIR).expanduser()
    return storage_dir / "playlists.json"


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


class PlaylistItem(BaseModel):
    """播单项（单个音频/视频）"""

    title: str = Field(..., description="标题")
    url: str | None = Field(
        None, description="播放 URL，如果为空则需要通过 custom_params 动态获取"
    )
    artist: str = Field("", description="艺术家/作者")
    album: str = Field("", description="专辑/系列")
    duration: int = Field(0, description="时长（秒）")
    cover_url: str = Field("", description="封面图片 URL")
    custom_params: dict[str, Any] = Field(
        default_factory=dict,
        description="自定义参数，用于调用 user_config.py 中的 get_audio_url 函数",
    )


class Playlist(BaseModel):
    """播单（播放列表）"""

    id: str = Field(..., description="播单唯一标识")
    name: str = Field(..., description="播单名称，例如：音乐、有声书、播客")
    type: str = Field("", description="播单类型，例如：music, audiobook, podcast")
    description: str = Field("", description="播单描述")
    items: list[PlaylistItem] = Field(default_factory=list, description="播单项列表")
    voice_keywords: list[str] = Field(
        default_factory=list,
        description="语音识别关键词，用于语音命令控制",
    )
    created_at: str = ""
    updated_at: str = ""


class CreatePlaylistRequest(BaseModel):
    name: str
    type: str = ""
    description: str = ""
    voice_keywords: list[str] = []


class UpdatePlaylistRequest(BaseModel):
    name: str | None = None
    type: str | None = None
    description: str | None = None
    voice_keywords: list[str] | None = None


class AddItemRequest(BaseModel):
    items: list[PlaylistItem]


class PlayPlaylistRequest(BaseModel):
    device_id: str | None = None
    start_index: int = Field(0, description="从第几首开始播放（从 0 开始）")
    announce: bool = Field(True, description="是否语音播报")


# ---------------------------------------------------------------------------
# 存储管理
# ---------------------------------------------------------------------------


def _ensure_storage_dir():
    """确保存储目录存在"""
    _get_playlist_file().parent.mkdir(parents=True, exist_ok=True)


def _load_playlists() -> dict[str, Playlist]:
    """从文件加载播单"""
    playlist_file = _get_playlist_file()
    if not playlist_file.exists():
        return {}
    try:
        with open(playlist_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {pid: Playlist(**pdata) for pid, pdata in data.items()}
    except Exception as e:
        _log.error("Failed to load playlists from %s: %s", playlist_file, e)
        return {}


def _save_playlists(playlists: dict[str, Playlist]):
    """保存播单到文件"""
    _ensure_storage_dir()
    playlist_file = _get_playlist_file()
    try:
        data = {pid: p.model_dump() for pid, p in playlists.items()}
        with open(playlist_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        _log.info("Saved %d playlists to %s", len(playlists), playlist_file)
    except Exception as e:
        _log.error("Failed to save playlists to %s: %s", playlist_file, e)
        raise HTTPException(status_code=500, detail=f"Failed to save playlists: {e}")


def _generate_playlist_id(name: str) -> str:
    """生成播单 ID"""
    import time

    timestamp = str(int(time.time() * 1000))
    # 使用名称的拼音首字母 + 时间戳（简化实现，实际可以使用 pypinyin）
    return f"{name[:10]}_{timestamp}"


# ---------------------------------------------------------------------------
# URL 处理
# ---------------------------------------------------------------------------


def _make_proxy_url(original_url: str) -> str:
    """将原始 URL 转换为代理 URL"""
    proxy_url = f"{config.SERVER_BASE_URL}/api/proxy/stream?url={quote(original_url)}"
    _log.debug("Converted URL to proxy: %s -> %s", original_url[:100], proxy_url[:100])
    return proxy_url


async def _get_item_url(item: PlaylistItem) -> str:
    """获取播单项的播放 URL

    如果 item.url 存在，直接使用；
    否则调用 user_config.py 中的 get_audio_url 函数获取。
    """
    if item.url:
        return _make_proxy_url(item.url)

    # 尝试从 user_config.py 加载 get_audio_url 函数
    try:
        import sys

        user_config_path = Path.cwd() / "user_config.py"
        if not user_config_path.exists():
            raise HTTPException(
                status_code=500,
                detail="user_config.py not found, cannot get audio URL for item without URL",
            )

        # 动态导入 user_config
        spec = importlib.util.spec_from_file_location("user_config", user_config_path)
        if spec and spec.loader:
            user_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_config)

            # 检查是否有 get_audio_url 函数
            if not hasattr(user_config, "get_audio_url"):
                raise HTTPException(
                    status_code=500,
                    detail="get_audio_url function not found in user_config.py",
                )

            get_audio_url = user_config.get_audio_url

            # 调用函数获取 URL
            if asyncio.iscoroutinefunction(get_audio_url):
                url = await get_audio_url(item.custom_params)
            else:
                url = get_audio_url(item.custom_params)

            if not url:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get audio URL for item: {item.title}",
                )

            return _make_proxy_url(url)

    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to get audio URL for item %s: %s", item.title, e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audio URL: {e}",
        )


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------


@router.get("")
async def list_playlists() -> dict[str, Any]:
    """获取所有播单"""
    playlists = _load_playlists()
    return {
        "playlists": [p.model_dump() for p in playlists.values()],
        "total": len(playlists),
    }


@router.post("")
async def create_playlist(req: CreatePlaylistRequest) -> Playlist:
    """创建新播单"""
    playlists = _load_playlists()

    playlist_id = _generate_playlist_id(req.name)

    from datetime import datetime

    now = datetime.now().isoformat()

    playlist = Playlist(
        id=playlist_id,
        name=req.name,
        type=req.type,
        description=req.description,
        voice_keywords=req.voice_keywords,
        created_at=now,
        updated_at=now,
    )

    playlists[playlist_id] = playlist
    _save_playlists(playlists)

    _log.info("Created playlist: %s (id=%s)", req.name, playlist_id)
    return playlist


@router.get("/{playlist_id}")
async def get_playlist(playlist_id: str) -> Playlist:
    """获取指定播单"""
    playlists = _load_playlists()
    if playlist_id not in playlists:
        raise HTTPException(
            status_code=404, detail=f"Playlist not found: {playlist_id}"
        )
    return playlists[playlist_id]


@router.put("/{playlist_id}")
async def update_playlist(playlist_id: str, req: UpdatePlaylistRequest) -> Playlist:
    """更新播单信息"""
    playlists = _load_playlists()
    if playlist_id not in playlists:
        raise HTTPException(
            status_code=404, detail=f"Playlist not found: {playlist_id}"
        )

    playlist = playlists[playlist_id]

    if req.name is not None:
        playlist.name = req.name
    if req.type is not None:
        playlist.type = req.type
    if req.description is not None:
        playlist.description = req.description
    if req.voice_keywords is not None:
        playlist.voice_keywords = req.voice_keywords

    from datetime import datetime

    playlist.updated_at = datetime.now().isoformat()

    _save_playlists(playlists)

    _log.info("Updated playlist: %s", playlist_id)
    return playlist


@router.delete("/{playlist_id}")
async def delete_playlist(playlist_id: str):
    """删除播单"""
    playlists = _load_playlists()
    if playlist_id not in playlists:
        raise HTTPException(
            status_code=404, detail=f"Playlist not found: {playlist_id}"
        )

    del playlists[playlist_id]
    _save_playlists(playlists)

    _log.info("Deleted playlist: %s", playlist_id)
    return {"message": "Playlist deleted"}


@router.post("/{playlist_id}/items")
async def add_items(playlist_id: str, req: AddItemRequest):
    """添加播单项"""
    playlists = _load_playlists()
    if playlist_id not in playlists:
        raise HTTPException(
            status_code=404, detail=f"Playlist not found: {playlist_id}"
        )

    playlist = playlists[playlist_id]
    playlist.items.extend(req.items)

    from datetime import datetime

    playlist.updated_at = datetime.now().isoformat()

    _save_playlists(playlists)

    _log.info("Added %d items to playlist: %s", len(req.items), playlist_id)
    return {"message": f"Added {len(req.items)} items"}


@router.delete("/{playlist_id}/items/{item_index}")
async def delete_item(playlist_id: str, item_index: int):
    """删除播单项"""
    playlists = _load_playlists()
    if playlist_id not in playlists:
        raise HTTPException(
            status_code=404, detail=f"Playlist not found: {playlist_id}"
        )

    playlist = playlists[playlist_id]
    if item_index < 0 or item_index >= len(playlist.items):
        raise HTTPException(
            status_code=404,
            detail=f"Item index out of range: {item_index}",
        )

    removed_item = playlist.items.pop(item_index)

    from datetime import datetime

    playlist.updated_at = datetime.now().isoformat()

    _save_playlists(playlists)

    _log.info("Removed item %d from playlist: %s", item_index, playlist_id)
    return {"message": f"Removed item: {removed_item.title}"}


@router.post("/{playlist_id}/play")
async def play_playlist(playlist_id: str, req: PlayPlaylistRequest):
    """播放播单

    从指定位置开始播放播单中的音频。
    """
    playlists = _load_playlists()
    if playlist_id not in playlists:
        raise HTTPException(
            status_code=404, detail=f"Playlist not found: {playlist_id}"
        )

    playlist = playlists[playlist_id]

    if not playlist.items:
        raise HTTPException(status_code=400, detail="Playlist is empty")

    if req.start_index < 0 or req.start_index >= len(playlist.items):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid start_index: {req.start_index}",
        )

    # 获取要播放的项
    item = playlist.items[req.start_index]

    try:
        # 获取播放 URL
        play_url = await _get_item_url(item)

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
            result = await client.send_command(play_command, req.device_id, silent=True)

        return {
            "message": "Playing",
            "playlist": playlist.name,
            "item": item.model_dump(),
            "index": req.start_index,
            "total": len(playlist.items),
        }

    except Exception as e:
        _log.error("Failed to play playlist item: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=f"Failed to play: {e}")


@router.post("/play-by-voice")
async def play_by_voice_command(
    voice_text: str,
    device_id: str | None = None,
):
    """根据语音命令播放播单

    支持的命令格式：
    - "播放音乐播单"
    - "播放有声书"
    - "播放我的播客"
    """
    playlists = _load_playlists()

    # 查找匹配的播单
    matched_playlist: Playlist | None = None

    for playlist in playlists.values():
        # 检查播单名称是否在语音文本中
        if playlist.name in voice_text:
            matched_playlist = playlist
            break

        # 检查语音关键词
        for keyword in playlist.voice_keywords:
            if keyword in voice_text:
                matched_playlist = playlist
                break

        if matched_playlist:
            break

    if not matched_playlist:
        raise HTTPException(
            status_code=404,
            detail=f"No playlist matched for voice command: {voice_text}",
        )

    # 播放匹配的播单
    return await play_playlist(
        matched_playlist.id,
        PlayPlaylistRequest(device_id=device_id, start_index=0, announce=True),
    )
