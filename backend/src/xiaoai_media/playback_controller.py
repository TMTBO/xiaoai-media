"""播放控制器模块（基于定时器）

使用定时器方式监控播放进度，在歌曲播放完成时自动播放下一曲。
相比轮询方式，定时器方式更加高效，减少了不必要的 API 调用。
"""

import asyncio
import logging
from typing import Awaitable, Callable, Dict, Optional, Set

from xiaoai_media.client import get_client_sync
from xiaoai_media.logger import get_logger
from xiaoai_media.services.state_service import get_state_service

_log = get_logger()

# 状态变化回调类型
StatusChangeCallback = Callable[[str, dict], Awaitable[None]]


class PlaybackController:
    """播放控制器（基于进度推送）
    
    采用进度推送机制监控播放状态：
    1. 播放时，启动进度推送循环，每秒推送一次播放进度
    2. 进度推送循环同时监控播放进度，在歌曲结束前 buffer_time 秒触发下一曲
    3. 停止/暂停时，取消进度推送循环
    4. 下/上一曲时，取出下/上一个音频，触发播放时逻辑
    """

    def __init__(self, buffer_time: float = 1.0):
        """初始化播放控制器
        
        Args:
            buffer_time: 定时器缓冲时间（秒），在歌曲结束前多久触发下一曲，默认 1.0 秒
        """
        self.buffer_time = buffer_time
        self.running = False
        self._state_service = get_state_service()
        
        # 记录每个设备的播放状态
        # device_id -> {"status": "playing"|"paused"|"stopped", "audio_id": str, ...}
        self._device_status: Dict[str, dict] = {}
        
        # 记录每个设备是否正在切换下一曲（防止重复触发）
        # device_id -> bool
        self._switching: Dict[str, bool] = {}
        
        # 记录每个设备的进度推送任务（同时负责触发下一曲）
        # device_id -> asyncio.Task
        self._progress_tasks: Dict[str, asyncio.Task] = {}
        
        # SSE 状态变化回调
        self._status_callbacks: Set[StatusChangeCallback] = set()

    async def start(self):
        """启动播放控制器"""
        if self.running:
            _log.warning("播放控制器已在运行")
            return
        
        self.running = True
        _log.info("播放控制器已启动（进度推送模式）")

    async def check_and_resume(self):
        """检查设备播放状态并恢复监听
        
        在应用启动时调用，检查是否有设备正在播放，
        如果有，则恢复监听状态。
        """
        try:
            client = get_client_sync()
            devices = await client.list_devices()
            
            has_active_playback = False
            
            for device in devices:
                device_id = device.get("deviceID")
                if not device_id:
                    continue
                
                # 获取播放信息
                playback_info = await self._get_device_playback_info(device_id)
                if not playback_info:
                    continue
                
                status_code = playback_info["status_code"]
                media_type = playback_info["media_type"]
                duration = playback_info["duration"]
                position = playback_info["position"]
                
                # 如果设备正在播放音乐（status=1, media_type=3）且有有效时长
                if status_code == 1 and media_type == 3 and duration > 0:
                    _log.info(
                        "检测到设备 %s 正在播放音乐，恢复监听状态",
                        device_id
                    )
                    
                    has_active_playback = True
                    
                    # 检查是否有保存的播放状态
                    current_playlist_id = self._get_current_playlist_id(device_id)
                    
                    if current_playlist_id:
                        _log.info(
                            "设备 %s 有播单信息: %s，设置定时器自动播放下一曲",
                            device_id,
                            current_playlist_id
                        )
                        # 设置定时器
                        await self.on_play_started(device_id, duration, position)
                    else:
                        _log.info(
                            "设备 %s 没有播单信息（可能是语音播放），不设置定时器",
                            device_id
                        )
            
            # 如果有活动的播放，启动控制器
            if has_active_playback and not self.running:
                await self.start()
                _log.info("已自动恢复播放控制")
            elif not has_active_playback:
                _log.info("没有检测到活动的播放，控制器保持待机状态")
                
        except Exception as e:
            _log.error("检查播放状态失败: %s", e, exc_info=True)

    async def stop(self):
        """停止播放控制器"""
        if not self.running:
            return
        
        self.running = False
        
        # 取消所有进度推送任务
        for device_id in list(self._progress_tasks.keys()):
            await self._cancel_progress_task(device_id)
        
        _log.info("播放控制器已停止")
    
    def add_status_callback(self, callback: StatusChangeCallback):
        """添加状态变化回调
        
        Args:
            callback: 回调函数，接收 (device_id, status_dict) 参数
        """
        self._status_callbacks.add(callback)
        _log.debug("添加状态变化回调，当前回调数: %d", len(self._status_callbacks))
    
    def remove_status_callback(self, callback: StatusChangeCallback):
        """移除状态变化回调
        
        Args:
            callback: 要移除的回调函数
        """
        self._status_callbacks.discard(callback)
        _log.debug("移除状态变化回调，当前回调数: %d", len(self._status_callbacks))
    
    def _get_current_playlist_id(self, device_id: str) -> Optional[str]:
        """获取设备当前播单 ID
        
        Args:
            device_id: 设备 ID
            
        Returns:
            播单 ID，如果没有则返回 None
        """
        return (
            self._state_service.get(f"current_playlist_{device_id}") or
            self._state_service.get("current_playlist_default")
        )
    
    async def _get_device_playback_info(self, device_id: str) -> Optional[dict]:
        """获取设备播放信息
        
        Args:
            device_id: 设备 ID
            
        Returns:
            包含 duration 和 position 的字典，失败返回 None
        """
        try:
            client = get_client_sync()
            status = await client.player_get_status(device_id)
            
            # 直接使用展平后的数据
            return {
                "duration": status.get("duration", 0),
                "position": status.get("position", 0),
                "status_code": status.get("status_code", 0),
                "media_type": status.get("media_type", 0)
            }
        except Exception as e:
            _log.error("获取设备 %s 播放信息失败: %s", device_id, e, exc_info=True)
            return None
    
    async def _stop_current_playback(self, device_id: str):
        """停止当前播放
        
        Args:
            device_id: 设备 ID
        """
        try:
            _log.info("停止当前播放...")
            client = get_client_sync()
            await client.player_pause(device_id)
            await asyncio.sleep(0.3)
            await client.player_stop(device_id)
            _log.info("当前播放已停止")
        except Exception as e:
            _log.warning("停止播放失败（可能已经停止）: %s", e)
    
    async def _update_device_status(self, device_id: str, status_update: dict):
        """更新设备状态并通知订阅者
        
        Args:
            device_id: 设备 ID
            status_update: 状态更新字典
        """
        if device_id not in self._device_status:
            self._device_status[device_id] = {}
        
        self._device_status[device_id].update(status_update)
        await self._notify_status_change(device_id, self._device_status[device_id])
    
    async def _notify_status_change(self, device_id: str, status: dict):
        """通知所有订阅者状态已变化
        
        Args:
            device_id: 设备 ID
            status: 状态信息
        """
        if not self._status_callbacks:
            return
        
        _log.debug("通知 %d 个订阅者设备 %s 状态变化", len(self._status_callbacks), device_id)
        
        # 并发调用所有回调
        await asyncio.gather(
            *[callback(device_id, status) for callback in self._status_callbacks],
            return_exceptions=True
        )

    async def on_play_started(self, device_id: str, duration: int, position: int = 0):
        """播放开始时调用
        
        Args:
            device_id: 设备 ID
            duration: 音频总时长（毫秒）
            position: 当前播放位置（毫秒），默认为 0
        """
        if not self.running:
            await self.start()
        
        # 取消之前的进度推送任务（如果有）
        await self._cancel_progress_task(device_id)
        
        # 计算剩余播放时间（秒）
        remaining_ms = duration - position
        remaining_sec = remaining_ms / 1000.0
        
        _log.info(
            "设备 %s 开始播放，时长 %d ms，当前位置 %d ms，剩余 %.1f 秒",
            device_id,
            duration,
            position,
            remaining_sec
        )
        
        # 更新设备状态并通知
        await self._update_device_status(device_id, {
            "status": "playing",
            "duration": duration,
            "position": position,
            "start_time": asyncio.get_event_loop().time(),
        })
        
        # 启动进度推送任务（每秒推送一次，同时负责触发下一曲）
        self._progress_tasks[device_id] = asyncio.create_task(
            self._progress_push_loop(device_id)
        )

    async def on_play_paused(self, device_id: str):
        """播放暂停时调用
        
        Args:
            device_id: 设备 ID
        """
        _log.info("设备 %s 暂停播放，取消进度推送", device_id)
        
        # 取消进度推送任务
        await self._cancel_progress_task(device_id)
        
        # 更新设备状态并通知
        if device_id in self._device_status:
            await self._update_device_status(device_id, {"status": "paused"})

    async def on_play_resumed(self, device_id: str):
        """播放继续时调用
        
        Args:
            device_id: 设备 ID
        """
        _log.info("设备 %s 继续播放，重新读取状态并设置进度推送", device_id)
        
        # 获取播放信息
        playback_info = await self._get_device_playback_info(device_id)
        if not playback_info:
            _log.warning("设备 %s 播放状态无效，无法启动进度推送", device_id)
            return
        
        duration = playback_info["duration"]
        position = playback_info["position"]
        
        if duration > 0:
            # 重新启动播放
            await self.on_play_started(device_id, duration, position)
        else:
            _log.warning("设备 %s 播放状态无效，无法启动进度推送", device_id)

    async def on_play_stopped(self, device_id: str):
        """播放停止时调用
        
        Args:
            device_id: 设备 ID
        """
        _log.info("设备 %s 停止播放，取消进度推送", device_id)
        
        # 取消进度推送任务
        await self._cancel_progress_task(device_id)
        
        # 更新设备状态并通知
        if device_id in self._device_status:
            await self._update_device_status(device_id, {"status": "stopped"})
        
        # 清除播放状态
        self._state_service.set(f"current_playlist_{device_id}", None)
        if device_id in self._device_status:
            del self._device_status[device_id]

    async def _cancel_progress_task(self, device_id: str):
        """取消设备的进度推送任务
        
        Args:
            device_id: 设备 ID
        """
        if device_id in self._progress_tasks:
            task = self._progress_tasks[device_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self._progress_tasks[device_id]
            _log.debug("已取消设备 %s 的进度推送任务", device_id)

    async def _progress_push_loop(self, device_id: str):
        """进度推送循环，每秒推送一次播放进度，并在接近结束时触发下一曲
        
        Args:
            device_id: 设备 ID
        """
        try:
            last_push_time = asyncio.get_event_loop().time()
            next_song_triggered = False  # 标记是否已触发下一曲
            
            while True:
                await asyncio.sleep(1.0)
                
                # 检查设备状态是否存在
                if device_id not in self._device_status:
                    _log.debug("设备 %s 状态不存在，停止进度推送", device_id)
                    break
                
                status = self._device_status[device_id]
                
                # 只在播放状态下推送进度
                if status.get("status") != "playing":
                    _log.debug("设备 %s 非播放状态，停止进度推送", device_id)
                    break
                
                # 计算自上次推送以来经过的时间
                current_time = asyncio.get_event_loop().time()
                elapsed_ms = int((current_time - last_push_time) * 1000)
                last_push_time = current_time
                
                # 更新播放位置
                current_position = status.get("position", 0) + elapsed_ms
                duration = status.get("duration", 0)
                
                # 检查是否需要触发下一曲（在结束前 buffer_time 秒）
                remaining_ms = duration - current_position
                remaining_sec = remaining_ms / 1000.0
                
                if not next_song_triggered and remaining_sec <= self.buffer_time:
                    next_song_triggered = True
                    _log.info("设备 %s 即将播放完成（剩余 %.1f 秒），触发下一曲", device_id, remaining_sec)
                    # 异步触发下一曲，不阻塞进度推送
                    asyncio.create_task(self._on_playback_finished(device_id))
                
                # 如果播放位置已达到或超过总时长，停止推送
                if current_position >= duration:
                    current_position = duration
                    status["position"] = current_position
                    # 推送最后一次进度更新
                    await self._notify_status_change(device_id, status)
                    _log.debug(
                        "设备 %s 播放结束，最终进度: %d/%d ms",
                        device_id,
                        current_position,
                        duration
                    )
                    break
                
                # 更新状态中的位置
                status["position"] = current_position
                
                # 推送进度更新
                await self._notify_status_change(device_id, status)
                
                _log.debug(
                    "设备 %s 进度推送: %d/%d ms",
                    device_id,
                    current_position,
                    duration
                )
                
        except asyncio.CancelledError:
            _log.debug("设备 %s 进度推送循环被取消", device_id)
            raise
        except Exception as e:
            _log.error("设备 %s 进度推送循环异常: %s", device_id, e, exc_info=True)

    async def _on_playback_finished(self, device_id: str):
        """播放完成时的处理
        
        Args:
            device_id: 设备 ID
        """
        # 检查是否有播单
        current_playlist_id = self._get_current_playlist_id(device_id)
        
        if not current_playlist_id:
            _log.info("设备 %s 没有播单信息，不自动播放下一曲", device_id)
            return
        
        # 检查是否正在切换下一曲（防止重复触发）
        if self._switching.get(device_id, False):
            _log.debug("设备 %s 正在切换下一曲，跳过本次触发", device_id)
            return
        
        # 设置切换标志
        self._switching[device_id] = True
        
        try:
            # 播放下一曲
            await self._play_next(device_id, current_playlist_id)
        except Exception as e:
            _log.error("播放下一曲过程出错: %s", e, exc_info=True)
        finally:
            # 清除切换标志
            self._switching[device_id] = False

    async def _play_next(self, device_id: str, playlist_id: str):
        """播放下一曲
        
        Args:
            device_id: 设备 ID
            playlist_id: 播单 ID
        """
        try:
            _log.info(
                "准备播放下一曲: device_id=%s, playlist_id=%s",
                device_id,
                playlist_id
            )
            
            # 取消当前的进度推送
            await self._cancel_progress_task(device_id)
            
            # 停止当前播放
            await self._stop_current_playback(device_id)
            
            # 等待一小段时间，确保设备已经完全停止
            await asyncio.sleep(0.5)
            
            # 播放下一曲（这会触发 play_playlist，进而调用 on_play_started 设置新的定时器）
            # Lazy import to avoid circular dependency
            from xiaoai_media.services.playlist_service import PlaylistService
            
            _log.info("调用 PlaylistService.play_next_in_playlist...")
            result = await PlaylistService.play_next_in_playlist(
                playlist_id,
                device_id,
            )
            _log.info(
                "自动播放下一曲成功: %s",
                result.get("item", {}).get("title", "")
            )
        except Exception as e:
            _log.error("自动播放下一曲失败: %s", e, exc_info=True)
            # 如果播放失败，清除当前播单状态
            self._state_service.set(f"current_playlist_{device_id}", None)


# 全局控制器实例
_controller: Optional[PlaybackController] = None


def get_controller() -> PlaybackController:
    """获取全局播放控制器实例
    
    Returns:
        PlaybackController 实例
    """
    global _controller
    if _controller is None:
        _controller = PlaybackController()
    return _controller


def reset_controller():
    """重置全局控制器实例（用于测试或重启）"""
    global _controller
    if _controller is not None and _controller.running:
        _controller.running = False
    _controller = None
