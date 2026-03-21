"""
播单（播放列表）管理路由

支持多个播单（音乐、有声书、播客等），可通过语音命令控制播放。
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from xiaoai_media.services import (
    AddItemRequest,
    CreatePlaylistRequest,
    Playlist,
    PlaylistService,
    PlayPlaylistRequest,
    UpdatePlaylistRequest,
)

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("")
async def list_playlists() -> dict[str, Any]:
    """获取所有播单（仅返回索引信息）"""
    try:
        return PlaylistService.list_playlists()
    except Exception as e:
        _log.error("Failed to list playlists: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_playlist(req: CreatePlaylistRequest) -> Playlist:
    """创建新播单"""
    try:
        return PlaylistService.create_playlist(req)
    except Exception as e:
        _log.error("Failed to create playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{playlist_id}")
async def get_playlist(playlist_id: str) -> Playlist:
    """获取指定播单（包含完整数据）"""
    try:
        playlist = PlaylistService.get_playlist(playlist_id)
        if playlist is None:
            raise HTTPException(status_code=404, detail=f"Playlist not found: {playlist_id}")
        return playlist
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Failed to get playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{playlist_id}")
async def update_playlist(playlist_id: str, req: UpdatePlaylistRequest) -> Playlist:
    """更新播单信息"""
    try:
        return PlaylistService.update_playlist(playlist_id, req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log.error("Failed to update playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{playlist_id}")
async def delete_playlist(playlist_id: str):
    """删除播单"""
    try:
        PlaylistService.delete_playlist(playlist_id)
        return {"message": "Playlist deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log.error("Failed to delete playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{playlist_id}/items")
async def add_items(playlist_id: str, req: AddItemRequest):
    """添加播单项"""
    try:
        PlaylistService.add_items(playlist_id, req)
        return {"message": f"Added {len(req.items)} items"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log.error("Failed to add items: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{playlist_id}/items/{item_index}")
async def delete_item(playlist_id: str, item_index: int):
    """删除播单项"""
    try:
        removed_item = PlaylistService.delete_item(playlist_id, item_index)
        return {"message": f"Removed item: {removed_item.title}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log.error("Failed to delete item: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{playlist_id}/play")
async def play_playlist(playlist_id: str, req: PlayPlaylistRequest):
    """播放播单

    从指定位置开始播放播单中的音频。
    """
    try:
        return await PlaylistService.play_playlist(playlist_id, req)
    except ValueError as e:
        # 区分 404 和 400 错误
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        _log.error("Failed to play playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
    
    从索引文件中匹配唤醒词，然后加载对应的播单
    """
    try:
        return await PlaylistService.play_by_voice_command(voice_text, device_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        _log.error("Failed to play by voice: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
