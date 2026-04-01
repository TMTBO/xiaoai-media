"""音乐API路由

处理音乐相关的HTTP请求，业务逻辑已移至services层。
"""

from __future__ import annotations

import asyncio
import json
import logging
from xiaoai_media.logger import get_logger

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from xiaoai_media.player import get_player
from xiaoai_media.services import (
    MusicService,
    PlaylistLoaderService,
    VoiceCommandService,
    SongItem,
)

_log = get_logger()

router = APIRouter(prefix="/music", tags=["music"])


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------


class PlayRequest(BaseModel):
    """播放请求"""
    index: int = 0
    device_id: str | None = None


class SyncPlaylistRequest(BaseModel):
    """同步播放列表请求"""
    songs: list[SongItem]
    device_id: str | None = None


class DeviceRequest(BaseModel):
    """设备请求"""
    device_id: str | None = None


class VoiceCommandRequest(BaseModel):
    """语音命令请求"""
    text: str
    device_id: str | None = None


class AnnounceSearchRequest(BaseModel):
    """播报搜索结果请求"""
    query: str
    count: int
    device_id: str | None = None


class LoadFromSearchRequest(BaseModel):
    """从搜索加载播放列表请求"""
    query: str
    device_id: str | None = None
    platform: str | None = None
    auto_play: bool = True


class LoadFromChartRequest(BaseModel):
    """从排行榜加载播放列表请求"""
    chart_id: str | None = None
    chart_keyword: str | None = None
    device_id: str | None = None
    platform: str | None = None
    auto_play: bool = True


class LoadFromPlaylistRequest(BaseModel):
    """从保存的播放列表加载请求"""
    playlist_id: str
    device_id: str | None = None
    auto_play: bool = True


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
    """搜索音乐"""
    return await MusicService.search_music(query, platform, page, limit)


@router.get("/ranks")
async def get_ranks(
    platform: str | None = Query(None, description="Platform: tx|kw|kg|wy|mg"),
):
    """获取平台的排行榜列表"""
    return await MusicService.get_ranks(platform)


@router.get("/rank/{rank_id}")
async def get_rank_songs(
    rank_id: str,
    platform: str | None = Query(None, description="Platform: tx|kw|kg|wy|mg"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """获取指定排行榜的歌曲列表"""
    return await MusicService.get_rank_songs(rank_id, platform, page, limit)


# ---------------------------------------------------------------------------
# Playback control
# ---------------------------------------------------------------------------


@router.post("/playlist")
async def sync_playlist(req: SyncPlaylistRequest):
    """同步（替换）设备的服务端播放列表"""
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
    """播放服务端播放列表中指定索引的歌曲"""
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
    """播放下一首歌曲"""
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
    """播放上一首歌曲"""
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
    """暂停播放"""
    try:
        player = get_player()
        return await player.pause(req.device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/resume")
async def resume_music(req: DeviceRequest):
    """恢复播放"""
    try:
        player = get_player()
        return await player.resume(req.device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stop")
async def stop_music(req: DeviceRequest):
    """停止播放"""
    try:
        player = get_player()
        return await player.stop(req.device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/status")
async def get_player_status(device_id: str | None = None):
    """获取当前播放器状态"""
    try:
        player = get_player()
        return await player.get_status(device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/status/stream")
async def stream_player_status(
    request: Request,
    device_id: str | None = Query(None, description="设备ID，不指定则监听所有设备")
):
    """SSE 流式推送播放器状态变化
    
    当播放状态发生变化时，主动推送给前端，避免轮询。
    
    返回格式：
        event: status
        data: {"device_id": "xxx", "status": "playing", "audio_id": "xxx", ...}
    """
    async def event_generator():
        """SSE 事件生成器"""
        queue: asyncio.Queue = asyncio.Queue()
        
        async def status_callback(dev_id: str, status: dict):
            """状态变化回调，将状态推送到队列"""
            # 如果指定了 device_id，只推送该设备的状态
            if device_id and dev_id != device_id:
                return
            
            await queue.put({
                "device_id": dev_id,
                **status
            })
        
        # 注册回调
        monitor = get_monitor()
        monitor.add_status_callback(status_callback)
        _log.info("SSE 客户端已连接: device_id=%s", device_id)
        
        try:
            # 首次连接时，立即发送当前状态
            try:
                player = get_player()
                current_status = await player.get_status(device_id)
                yield f"event: status\ndata: {json.dumps(current_status)}\n\n"
            except Exception as e:
                _log.warning("获取初始状态失败: %s", e)
            
            # 持续推送状态变化
            while True:
                # 检查客户端是否断开连接
                if await request.is_disconnected():
                    _log.info("SSE 客户端已断开连接: device_id=%s", device_id)
                    break
                
                try:
                    # 等待状态变化，设置超时以便定期检查连接状态
                    status_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # 发送 SSE 事件
                    yield f"event: status\ndata: {json.dumps(status_data)}\n\n"
                    
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield f": heartbeat\n\n"
                    
        except asyncio.CancelledError:
            _log.info("SSE 连接被取消: device_id=%s", device_id)
        finally:
            # 清理：移除回调
            monitor.remove_status_callback(status_callback)
            _log.info("SSE 客户端已清理: device_id=%s", device_id)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )


# ---------------------------------------------------------------------------
# Playlist loading from different sources
# ---------------------------------------------------------------------------


@router.post("/load-from-search")
async def load_from_search(req: LoadFromSearchRequest):
    """从搜索结果加载播放列表并可选自动播放
    
    允许用户搜索歌曲并将其加载到播放列表中进行语音控制。
    
    示例:
        POST /api/music/load-from-search
        {
            "query": "周杰伦",
            "device_id": "xxx",
            "platform": "tx",
            "auto_play": true
        }
    """
    return await PlaylistLoaderService.load_from_search(
        req.query, req.device_id, req.platform, req.auto_play
    )


@router.post("/load-from-chart")
async def load_from_chart(req: LoadFromChartRequest):
    """从排行榜加载播放列表并可选自动播放
    
    允许用户加载整个排行榜进行语音控制。
    
    示例:
        POST /api/music/load-from-chart
        {
            "chart_keyword": "热歌榜",
            "device_id": "xxx",
            "platform": "tx",
            "auto_play": true
        }
    """
    return await PlaylistLoaderService.load_from_chart(
        req.chart_id,
        req.chart_keyword,
        req.device_id,
        req.platform,
        req.auto_play,
    )


@router.post("/load-from-playlist")
async def load_from_playlist(req: LoadFromPlaylistRequest):
    """从保存的播放列表加载并可选自动播放
    
    允许用户加载他们保存的播放列表进行语音控制。
    
    示例:
        POST /api/music/load-from-playlist
        {
            "playlist_id": "音乐_1234567890",
            "device_id": "xxx",
            "auto_play": true
        }
    """
    return await PlaylistLoaderService.load_from_saved_playlist(
        req.playlist_id, req.device_id, req.auto_play
    )


@router.post("/voice-command")
async def voice_command(req: VoiceCommandRequest):
    """解析并执行自然语言语音命令
    
    支持的命令模式：
    - "播放/打开 [平台] [排行榜名称]" → 加载排行榜并播放
    - "播放 [播单名称]" → 加载保存的播放列表并播放
    - "搜索 [关键词]" → 搜索并加载结果
    - 其他文本 → 作为原始语音命令转发给音箱
    """
    return await VoiceCommandService.execute_command(req.text, req.device_id)


@router.post("/announce-search")
async def announce_search(req: AnnounceSearchRequest):
    """向音箱发送TTS，播报搜索结果数量"""
    return await VoiceCommandService.announce_search_results(
        req.query, req.count, req.device_id
    )


@router.get("/playlist")
async def get_playlist(device_id: str | None = None):
    """返回设备的当前播放列表状态"""
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
