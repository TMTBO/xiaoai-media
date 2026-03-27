"""全局状态 SSE 路由

提供统一的 SSE 端点，推送设备状态、播放状态、播单信息等全局状态变化。
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from xiaoai_media.api.dependencies import get_client_sync
from xiaoai_media.services.state_service import get_state_service
from xiaoai_media.services.playlist_service import PlaylistService

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/state", tags=["state"])


@router.get("/stream")
async def stream_global_state(
    request: Request,
    device_id: str | None = Query(None, description="设备ID，不指定则监听所有设备")
):
    """SSE 流式推送全局状态变化
    
    推送内容包括：
    - 设备在线状态
    - 播放状态（playing/paused/stopped）
    - 当前播放的播单信息
    - 播放进度（position/duration）
    - 当前播放的音频信息（歌名、歌手、专辑等）
    
    事件类型：
    - event: state - 完整状态更新
    - event: heartbeat - 心跳保持连接
    
    返回格式：
        event: state
        data: {
            "device_id": "xxx",
            "device_online": true,
            "device_name": "小爱音箱",
            "play_status": "playing",
            "audio_id": "xxx",
            "position": 12345,
            "duration": 234567,
            "current_song": {
                "name": "歌曲名",
                "singer": "歌手",
                "album": "专辑",
                ...
            },
            "playlist": {
                "current": 0,
                "total": 10,
                "songs": [...]
            }
        }
    """
    from xiaoai_media.playback_monitor import get_monitor
    
    async def event_generator():
        """SSE 事件生成器"""
        queue: asyncio.Queue = asyncio.Queue()
        
        async def status_callback(dev_id: str, status: dict):
            """状态变化回调，将状态推送到队列"""
            # 如果指定了 device_id，只推送该设备的状态
            if device_id and dev_id != device_id:
                return
            
            # 构建完整的状态信息
            try:
                full_state = await _build_full_state(dev_id, device=None, basic_status=status)
                await queue.put(full_state)
            except Exception as e:
                _log.error("构建完整状态失败: %s", e, exc_info=True)
        
        # 注册回调
        monitor = get_monitor()
        monitor.add_status_callback(status_callback)
        _log.info("SSE 全局状态客户端已连接: device_id=%s", device_id)
        
        # 检查并启动 playback monitor（如果设备正在播放）
        try:
            if not monitor.running:
                _log.info("playback_monitor 未运行，检查是否需要启动...")
                await monitor.check_and_resume()
        except Exception as e:
            _log.warning("检查 playback_monitor 状态失败: %s", e)
        
        try:
            # 首次连接时，立即发送当前状态
            try:
                initial_state = await _get_initial_state(device_id)
                yield f"event: state\ndata: {json.dumps(initial_state, ensure_ascii=False)}\n\n"
            except Exception as e:
                _log.warning("获取初始状态失败: %s", e)
            
            # 持续推送状态变化
            while True:
                # 检查客户端是否断开连接
                if await request.is_disconnected():
                    _log.info("SSE 全局状态客户端已断开连接: device_id=%s", device_id)
                    break
                
                try:
                    # 等待状态变化，设置超时以便定期检查连接状态
                    state_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # 发送 SSE 事件
                    yield f"event: state\ndata: {json.dumps(state_data, ensure_ascii=False)}\n\n"
                    
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield f"event: heartbeat\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
                    
        except asyncio.CancelledError:
            _log.info("SSE 全局状态连接被取消: device_id=%s", device_id)
        finally:
            # 清理：移除回调
            monitor.remove_status_callback(status_callback)
            _log.info("SSE 全局状态客户端已清理: device_id=%s", device_id)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )


async def _get_initial_state(device_id: str | None) -> dict[str, Any]:
    """获取初始状态
    
    Args:
        device_id: 设备 ID
        
    Returns:
        完整的状态信息
    """
    try:
        client = get_client_sync()
        
        # 获取设备信息
        devices = await client.list_devices()
        device = None
        if device_id:
            device = next((d for d in devices if d.get("deviceID") == device_id), None)
        elif devices:
            device = devices[0]
        
        if not device:
            return {"error": "Device not found"}
        
        dev_id = device.get("deviceID")
        
        # 获取播放状态
        status_result = await client.player_get_status(dev_id)
        status_data = status_result.get("status", {})
        data = status_data.get("data", {})
        info_str = data.get("info", "{}")
        
        try:
            info = json.loads(info_str)
        except (json.JSONDecodeError, TypeError):
            info = {}
        
        # 提取播放状态
        status_code = info.get("status", 0)
        play_status = {0: "stopped", 1: "playing", 2: "paused"}.get(status_code, "unknown")
        
        play_song_detail = info.get("play_song_detail", {})
        
        # 构建基础状态
        basic_status = {
            "status": play_status,
            "audio_id": play_song_detail.get("audio_id", ""),
            "position": play_song_detail.get("position", 0),
            "duration": play_song_detail.get("duration", 0),
            "media_type": info.get("media_type", 0),
        }
        
        # 复用 _build_full_state 构建完整状态
        return await _build_full_state(dev_id, device, basic_status, play_song_detail)
    except Exception as e:
        _log.error("获取初始状态失败: %s", e, exc_info=True)
        return {"error": str(e)}


async def _build_full_state(
    device_id: str, 
    device: dict | None = None,
    basic_status: dict | None = None,
    play_song_detail: dict | None = None
) -> dict[str, Any]:
    """构建完整的状态信息
    
    Args:
        device_id: 设备 ID
        device: 设备信息（可选，如果不提供会重新获取）
        basic_status: 基础状态（可选，来自 playback_monitor 或 _get_initial_state）
        play_song_detail: 播放歌曲详情（可选，如果不提供且需要会重新获取）
        
    Returns:
        完整的状态信息
    """
    try:
        client = get_client_sync()
        
        # 如果没有提供设备信息，获取设备信息
        if device is None:
            devices = await client.list_devices()
            device = next((d for d in devices if d.get("deviceID") == device_id), None)
            
            if not device:
                return {"error": "Device not found", "device_id": device_id}
        
        # 如果没有提供基础状态，使用默认值
        if basic_status is None:
            basic_status = {}
        
        # 从 state service 获取当前播放的播单 ID
        state_service = get_state_service()
        current_playlist_id = state_service.get(f"current_playlist_{device_id}")
        
        # 从 playlist service 获取播单信息和当前歌曲
        current_song = None
        playlist_info = None
        
        if current_playlist_id:
            try:
                playlist = PlaylistService.get_playlist(current_playlist_id)
                if playlist and playlist.items:
                    # 获取当前播放索引
                    current_index = playlist.current_index
                    
                    # 从播单中获取当前歌曲信息
                    if 0 <= current_index < len(playlist.items):
                        item = playlist.items[current_index]
                        current_song = {
                            "name": item.title,
                            "singer": item.artist,
                            "album": item.album,
                            "cover": "",
                            "audio_id": item.audio_id or "",
                        }
                        
                        # 如果有 custom_params，尝试获取更多信息
                        if item.custom_params:
                            # 从音乐搜索结果导入的歌曲
                            if "meta" in item.custom_params:
                                meta = item.custom_params["meta"]
                                if isinstance(meta, dict):
                                    current_song["cover"] = meta.get("picUrl", "")
                    
                    # 构建播单信息
                    playlist_info = {
                        "id": playlist.id,
                        "name": playlist.name,
                        "current": current_index,
                        "total": len(playlist.items),
                        "play_mode": playlist.play_mode,
                    }
            except Exception as e:
                _log.warning("获取播单信息失败: %s", e)
        
        # 如果没有从播单获取到歌曲信息，尝试从设备状态获取
        if not current_song:
            # 如果没有提供 play_song_detail，重新获取
            if play_song_detail is None:
                try:
                    status_result = await client.player_get_status(device_id)
                    status_data = status_result.get("status", {})
                    data = status_data.get("data", {})
                    info_str = data.get("info", "{}")
                    
                    _log.debug("获取设备状态用于歌曲信息: info_str=%s", info_str[:200])
                    
                    try:
                        info = json.loads(info_str)
                    except (json.JSONDecodeError, TypeError):
                        info = {}
                    
                    play_song_detail = info.get("play_song_detail", {})
                    _log.debug("play_song_detail 内容: %s", play_song_detail)
                except Exception as e:
                    _log.warning("获取设备播放状态失败: %s", e, exc_info=True)
                    play_song_detail = {}
            
            if play_song_detail:
                current_song = {
                    "name": play_song_detail.get("name", ""),
                    "singer": play_song_detail.get("singer", ""),
                    "album": play_song_detail.get("album_name", ""),
                    "cover": play_song_detail.get("cover", ""),
                    "audio_id": play_song_detail.get("audio_id", ""),
                }
                _log.info("从设备状态获取歌曲信息: name=%s, singer=%s, album=%s, cover=%s", 
                         current_song.get("name"), 
                         current_song.get("singer"),
                         current_song.get("album"),
                         "有" if current_song.get("cover") else "无")
            else:
                _log.warning("play_song_detail 为空，无法获取歌曲信息")
        
        # 构建完整状态
        return {
            "device_id": device_id,
            "device_online": device.get("isOnline", False),
            "device_name": device.get("name", ""),
            "device_hardware": device.get("hardware", ""),
            "play_status": basic_status.get("status", "unknown"),
            "audio_id": basic_status.get("audio_id", ""),
            "position": basic_status.get("position", 0),
            "duration": basic_status.get("duration", 0),
            "media_type": basic_status.get("media_type", 0),
            "current_song": current_song,
            "playlist": playlist_info,
        }
    except Exception as e:
        _log.error("构建完整状态失败: %s", e, exc_info=True)
        return {
            "error": str(e),
            "device_id": device_id,
            **basic_status
        }

