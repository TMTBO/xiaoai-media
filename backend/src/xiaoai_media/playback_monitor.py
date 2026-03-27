"""播放监控模块

监控设备播放状态，在歌曲播放完成时自动播放下一曲。
采用轮询 + position 回退检测机制。
支持 SSE 状态推送。
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Set, Callable, Awaitable

from xiaoai_media.api.dependencies import get_client_sync
from xiaoai_media.services.state_service import get_state_service
from xiaoai_media.services.playlist_service import PlaylistService

_log = logging.getLogger(__name__)

# 状态变化回调类型
StatusChangeCallback = Callable[[str, dict], Awaitable[None]]


class PlaybackMonitor:
    """播放监控器
    
    采用轮询机制监控播放状态：
    1. 定期检查设备播放状态
    2. 检测 position 回退（从接近结尾跳回开头或变成 0/0）
    3. 立即播放下一曲
    """

    def __init__(self, poll_interval: float = 3.0, max_paused_checks: int = 5):
        """初始化播放监控器
        
        Args:
            poll_interval: 轮询间隔（秒），默认 3.0 秒
            max_paused_checks: 暂停状态最大检查次数，超过后停止监控该设备，默认 5 次（15秒）
        """
        self.poll_interval = poll_interval
        self.max_paused_checks = max_paused_checks
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._state_service = get_state_service()
        
        # 记录每个设备的上次播放状态
        # device_id -> {"status": "playing"|"paused"|"stopped", "audio_id": str, ...}
        self._last_status: Dict[str, dict] = {}
        
        # 记录每个设备是否正在切换下一曲（防止重复触发）
        # device_id -> bool
        self._switching: Dict[str, bool] = {}
        
        # 记录每个设备连续暂停的次数
        # device_id -> int
        self._paused_count: Dict[str, int] = {}
        
        # SSE 状态变化回调
        # 当状态变化时，会调用所有注册的回调函数
        self._status_callbacks: Set[StatusChangeCallback] = set()

    async def start(self):
        """启动播放监控"""
        if self.running:
            _log.warning("播放监控器已在运行")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._monitor_loop())
        _log.info("播放监控器已启动 (轮询间隔: %.1f秒)", self.poll_interval)

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
                
                try:
                    # 获取播放状态
                    status_result = await client.player_get_status(device_id)
                    status_data = status_result.get("status", {})
                    data = status_data.get("data", {})
                    info_str = data.get("info", "{}")
                    
                    try:
                        info = json.loads(info_str)
                    except (json.JSONDecodeError, TypeError):
                        continue
                    
                    status_code = info.get("status", 0)
                    media_type = info.get("media_type", 0)
                    play_song_detail = info.get("play_song_detail", {})
                    duration = play_song_detail.get("duration", 0)
                    
                    # 如果设备正在播放音乐（status=1, media_type=3）且有有效时长
                    if status_code == 1 and media_type == 3 and duration > 0:
                        _log.info(
                            "检测到设备 %s 正在播放音乐，恢复监听状态",
                            device_id
                        )
                        
                        has_active_playback = True
                        
                        # 初始化该设备的状态（这样 _check_all_devices 就会监控它）
                        position = play_song_detail.get("position", 0)
                        audio_id = play_song_detail.get("audio_id", "")
                        self._last_status[device_id] = {
                            "status": "playing",
                            "audio_id": audio_id,
                            "position": position,
                            "duration": duration,
                            "media_type": media_type,
                        }
                        
                        # 检查是否有保存的播放状态
                        current_playlist_id = (
                            self._state_service.get(f"current_playlist_{device_id}") or
                            self._state_service.get("current_playlist_default")
                        )
                        
                        if current_playlist_id:
                            _log.info(
                                "设备 %s 有播单信息: %s，将支持自动播放下一曲",
                                device_id,
                                current_playlist_id
                            )
                        else:
                            _log.info(
                                "设备 %s 没有播单信息（可能是语音播放），将监控状态但不自动播放下一曲",
                                device_id
                            )
                            
                except Exception as e:
                    _log.debug("检查设备 %s 状态失败: %s", device_id, e)
            
            # 如果有活动的播放，启动监控器
            if has_active_playback and not self.running:
                await self.start()
                _log.info("已自动恢复播放监控")
            elif not has_active_playback:
                _log.info("没有检测到活动的播放，监控器保持待机状态")
                
        except Exception as e:
            _log.error("检查播放状态失败: %s", e, exc_info=True)

    async def stop(self):
        """停止播放监控"""
        if not self.running:
            return
        
        self.running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        _log.info("播放监控器已停止")
    
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

    async def _monitor_loop(self):
        """主监控循环"""
        try:
            while self.running:
                try:
                    await self._check_all_devices()
                except Exception as e:
                    _log.error("播放监控出错: %s", e, exc_info=True)
                
                await asyncio.sleep(self.poll_interval)
        except asyncio.CancelledError:
            _log.info("播放监控已取消")
            raise

    async def _check_all_devices(self):
        """检查所有设备的播放状态
        
        监控所有正在播放的设备（不管是否有播单）。
        如果没有任何设备有活动的播放，自动停止监听。
        """
        has_active_playback = False
        
        try:
            client = get_client_sync()
            devices = await client.list_devices()
            
            for device in devices:
                device_id = device.get("deviceID")
                if not device_id:
                    continue
                
                # 检查该设备是否有正在播放的播单
                current_playlist_id = self._state_service.get(
                    f"current_playlist_{device_id}"
                )
                
                # 检查设备上次的播放状态
                last_status = self._last_status.get(device_id, {})
                last_play_status = last_status.get("status", "stopped")
                
                # 如果设备有播单，或者上次在播放/暂停状态，则检查状态
                # 这样可以监控所有正在播放的设备，不管是否通过播单系统
                should_check = (
                    current_playlist_id or  # 有播单
                    last_play_status in ["playing", "paused"]  # 上次在播放
                )
                
                if not should_check:
                    continue
                
                has_active_playback = True
                
                try:
                    await self._check_device_status(client, device_id, current_playlist_id)
                except Exception as e:
                    _log.error(
                        "检查设备 %s 播放状态失败: %s",
                        device_id,
                        e,
                        exc_info=True
                    )
        except Exception as e:
            _log.error("检查设备播放状态失败: %s", e, exc_info=True)
        
        # 如果没有活动的播放，自动停止监听
        if not has_active_playback:
            _log.info("没有活动的播放，自动停止监听")
            await self.stop()

    async def _check_device_status(
        self,
        client,
        device_id: str,
        playlist_id: str | None = None,
    ):
        """检查单个设备的播放状态
        
        Args:
            client: XiaoAI 客户端
            device_id: 设备 ID
            playlist_id: 当前播放的播单 ID（可选，如果为空则不自动播放下一曲）
        """
        try:
            # 获取播放状态
            status_result = await client.player_get_status(device_id)
            
            status_data = status_result.get("status", {})
            data = status_data.get("data", {})
            info_str = data.get("info", "{}")
            
            # 解析 info JSON 字符串
            try:
                info = json.loads(info_str)
            except (json.JSONDecodeError, TypeError) as e:
                _log.warning("解析播放状态 info 失败: %s, info_str=%s", e, info_str)
                return
            
            # 提取关键状态信息
            # status: 0=停止, 1=播放中, 2=暂停
            status_code = info.get("status", 0)
            media_type = info.get("media_type", 0)
            
            # 播放详情
            play_song_detail = info.get("play_song_detail", {})
            audio_id = play_song_detail.get("audio_id", "")
            position = play_song_detail.get("position", 0)  # 当前播放位置（毫秒）
            duration = play_song_detail.get("duration", 0)  # 总时长（毫秒）
            
            # 转换状态码为字符串
            play_status = {0: "stopped", 1: "playing", 2: "paused"}.get(status_code, "unknown")
            
            # 检测暂停状态
            if play_status == "paused":
                self._paused_count[device_id] = self._paused_count.get(device_id, 0) + 1
                
                # 如果连续暂停次数超过阈值，停止监控该设备（但不清除播放列表状态）
                if self._paused_count[device_id] >= self.max_paused_checks:
                    _log.info(
                        "设备 %s 已暂停 %d 次（%.1f秒），停止监控该设备",
                        device_id,
                        self._paused_count[device_id],
                        self._paused_count[device_id] * self.poll_interval
                    )
                    # 清除该设备的监控状态，但保留播放列表信息
                    # 这样用户恢复播放时，播放列表信息仍然存在
                    if device_id in self._last_status:
                        del self._last_status[device_id]
                    if device_id in self._paused_count:
                        del self._paused_count[device_id]
                    return
                else:
                    _log.debug(
                        "设备 %s 暂停中 (%d/%d): audio_id=%s, position=%d/%d",
                        device_id,
                        self._paused_count[device_id],
                        self.max_paused_checks,
                        audio_id,
                        position,
                        duration,
                    )
            else:
                # 如果不是暂停状态，重置暂停计数
                if device_id in self._paused_count:
                    self._paused_count[device_id] = 0
                
                _log.debug(
                    "设备 %s 播放状态: status=%s(%d), audio_id=%s, position=%d/%d, media_type=%d",
                    device_id,
                    play_status,
                    status_code,
                    audio_id,
                    position,
                    duration,
                    media_type,
                )
            
            # 获取上次状态
            last_status = self._last_status.get(device_id, {})
            last_position = last_status.get("position", 0)
            last_duration = last_status.get("duration", 0)
            last_audio_id = last_status.get("audio_id", "")
            last_media_type = last_status.get("media_type", 0)
            
            # 检测 position 回退（歌曲播放完成）
            # 情况1: position 从接近结尾跳回开头（duration 不变）
            position_rollback_with_duration = (
                last_position > 0 and
                last_duration > 0 and
                last_position > last_duration * 0.9 and  # 上次在最后 10%
                duration > 0 and
                position < last_duration * 0.1 and       # 现在在前 10%
                audio_id == last_audio_id and
                duration == last_duration
            )
            # 情况2: position 从接近结尾变成 0/0（播放完成的瞬间）
            position_reset_to_zero = (
                last_position > 0 and
                last_duration > 0 and
                last_position > last_duration * 0.8 and  # 上次在最后 20%
                position == 0 and
                duration == 0 and
                audio_id == last_audio_id and
                last_media_type == 3  # 上次是音乐播放
            )
            
            position_rollback = position_rollback_with_duration or position_reset_to_zero
            
            # 构建新状态
            new_status = {
                "status": play_status,
                "audio_id": audio_id,
                "position": position,
                "duration": duration,
                "media_type": media_type,
            }
            
            # 检查状态是否变化
            status_changed = (
                last_status.get("status") != play_status or
                last_status.get("audio_id") != audio_id or
                abs(last_status.get("position", 0) - position) > 1000  # 位置变化超过1秒
            )
            
            # 更新当前状态
            self._last_status[device_id] = new_status
            
            # 如果状态变化，通知订阅者
            if status_changed:
                await self._notify_status_change(device_id, new_status)
            
            # 如果检测到 position 回退，说明歌曲播放完成
            if position_rollback:
                # 只有在有播单时才自动播放下一曲
                if playlist_id:
                    # 检查是否正在切换下一曲（防止重复触发）
                    if self._switching.get(device_id, False):
                        _log.debug("设备 %s 正在切换下一曲，跳过本次触发", device_id)
                        return
                    
                    _log.info(
                        "检测到设备 %s 歌曲播放完成 (position 回退: %d -> %d)，立即播放下一曲",
                        device_id,
                        last_position,
                        position
                    )
                    
                    # 设置切换标志
                    self._switching[device_id] = True
                    
                    try:
                        # 立即播放下一曲
                        await self._play_next(device_id, playlist_id)
                    except Exception as e:
                        _log.error("播放下一曲过程出错: %s", e, exc_info=True)
                    finally:
                        # 清除切换标志
                        self._switching[device_id] = False
                else:
                    _log.debug(
                        "检测到设备 %s 歌曲播放完成，但没有播单信息，不自动播放下一曲",
                        device_id
                    )
                
                return
            
            # 如果播放已完全停止（没有播放进度），清除播放状态
            # 注意：只有在 duration 和 position 都为 0 时才清除
            # 暂停状态不应该清除播放列表信息
            if play_status == "stopped" and duration == 0 and position == 0:
                _log.info("设备 %s 播放已完全停止，清除播放状态", device_id)
                self._state_service.set(f"current_playlist_{device_id}", None)
                # 清除该设备的状态记录
                if device_id in self._last_status:
                    del self._last_status[device_id]
            
        except Exception as e:
            _log.debug("获取设备 %s 播放状态失败: %s", device_id, e)
    
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
            
            # 先停止当前播放
            try:
                _log.info("停止当前播放...")
                client = get_client_sync()
                await client.player_pause(device_id)
                await asyncio.sleep(0.3)
                await client.player_stop(device_id)
                _log.info("当前播放已停止")
            except Exception as e:
                _log.warning("停止播放失败（可能已经停止）: %s", e)
            
            # 等待一小段时间，确保设备已经完全停止
            await asyncio.sleep(0.5)
            
            # 播放下一曲
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


# 全局监控器实例
_monitor: Optional[PlaybackMonitor] = None


def get_monitor() -> PlaybackMonitor:
    """获取全局播放监控器实例
    
    Returns:
        PlaybackMonitor 实例
    """
    global _monitor
    if _monitor is None:
        from xiaoai_media import config as app_config
        _monitor = PlaybackMonitor(poll_interval=app_config.PLAYBACK_MONITOR_INTERVAL)
    return _monitor


def reset_monitor():
    """重置全局监控器实例（用于测试或重启）"""
    global _monitor
    if _monitor is not None and _monitor.running:
        # 注意：这是同步函数，不能 await
        # 只是标记停止，不等待任务完成
        _monitor.running = False
    _monitor = None
