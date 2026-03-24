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
    ContinuePlayRequest,
    CreatePlaylistRequest,
    ImportFromDirectoryRequest,
    PlayModeRequest,
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


@router.get("/directories")
async def list_directories():
    """列出可用的目录
    
    - 本地模式：返回常用目录列表
    - Docker模式：返回 /data 下的可用目录列表
    """
    try:
        directories = PlaylistService.list_available_directories()
        is_docker = PlaylistService.is_docker_environment()
        return {
            "directories": directories,
            "is_docker": is_docker,
            "message": "Docker模式：从列表中选择目录" if is_docker else "本地模式：浏览目录"
        }
    except Exception as e:
        _log.error("Failed to list directories: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/directories/browse")
async def browse_directory(path: str | None = None):
    """浏览指定目录，返回子目录列表
    
    参数：
    - path: 目录路径（可选），如果为空则返回根目录
    
    返回：
    - current_path: 当前路径
    - parent_path: 父路径（如果有）
    - directories: 子目录列表
    - total: 子目录数量
    """
    try:
        result = PlaylistService.browse_directory(path)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        _log.error("Failed to browse directory: %s", e, exc_info=True)
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


@router.post("/{playlist_id}/continue")
async def continue_playlist(playlist_id: str, req: ContinuePlayRequest):
    """继续播放播单（从当前索引位置开始）"""
    try:
        return await PlaylistService.continue_playlist(playlist_id, req)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        _log.error("Failed to continue playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{playlist_id}/stop")
async def stop_playlist(playlist_id: str, device_id: str | None = None):
    """停止播放播单"""
    try:
        return await PlaylistService.stop_playlist(playlist_id, device_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log.error("Failed to stop playlist: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{playlist_id}/play-mode")
async def set_play_mode(playlist_id: str, req: PlayModeRequest):
    """设置播放模式
    
    支持的播放模式：
    - loop: 列表循环
    - single: 单曲循环
    - random: 随机播放
    """
    try:
        return PlaylistService.set_play_mode(playlist_id, req)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        _log.error("Failed to set play mode: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{playlist_id}/next")
async def play_next(playlist_id: str, device_id: str | None = None):
    """播放下一首（根据播放模式）"""
    try:
        return await PlaylistService.play_next_in_playlist(playlist_id, device_id)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        _log.error("Failed to play next: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/{playlist_id}/import")
async def import_from_directory(playlist_id: str, req: ImportFromDirectoryRequest):
    """从指定目录批量导入音频文件
    
    支持的音频格式：.mp3, .m4a, .flac, .wav, .ogg, .aac, .wma
    
    参数：
    - directory: 目录路径
      - 本地模式：完整的本地文件系统路径
      - Docker模式：/data 下的路径（通过 volume 挂载）
    - recursive: 是否递归扫描子目录
    - file_extensions: 要导入的文件扩展名列表（可选）
    
    返回：
    - imported: 成功导入的文件数量
    - skipped: 跳过的文件数量
    - total_scanned: 扫描的总文件数
    - playlist_total_items: 播单中的总项目数
    """
    try:
        result = PlaylistService.import_from_directory(
            playlist_id=playlist_id,
            directory=req.directory,
            recursive=req.recursive,
            file_extensions=req.file_extensions
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        _log.error("Failed to import from directory: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
