"""播放监控模块

监控设备播放状态，在歌曲播放完成时自动播放下一曲。
采用轮询 + position 回退检测机制。
"""

import asyncio
import json
import logging
from typing import Dict, Optional

from xiaoai_media.api.dependencies import get_client_sync
from xiaoai_media.services.state_service import get_state_service
from xiaoai_media.services.playlist_service import PlaylistService

_log = logging.getLogger(__name__)


class PlaybackMonitor:
    """播放监控器
    
    采用轮询机制监控播放状态：
    1. 定期检查设备播放状态
    2. 检测 position 回退（从接近结尾跳回开头或变成 0/0）
    3. 立即播放下一曲
    """

    def __init__(self, poll_interval: float = 3.0):
        """初始化播放监控器
        
        Args:
            poll_interval: 轮询间隔（秒），默认 3.0 秒
        """
        self.poll_interval = poll_interval
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._state_service = get_state_service()
        
        # 记录每个设备的上次播放状态
        # device_id -> {"status": "playing"|"paused"|"stopped", "audio_id": str, ...}
        self._last_status: Dict[str, dict] = {}
        
        # 记录每个设备是否正在切换下一曲（防止重复触发）
        # device_id -> bool
        self._switching: Dict[str, bool] = {}

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
                            "检测到设备 %s 正在播放音乐，尝试恢复监听状态",
                            device_id
                        )
                        
                        # 检查是否有保存的播放状态（尝试两种 key）
                        current_playlist_id = (
                            self._state_service.get(f"current_playlist_{device_id}") or
                            self._state_service.get("current_playlist_default")
                        )
                        
                        if current_playlist_id:
                            _log.info(
                                "设备 %s 的播放状态已存在: %s，将恢复监听",
                                device_id,
                                current_playlist_id
                            )
                            has_active_playback = True
                        else:
                            _log.warning(
                                "设备 %s 正在播放但没有保存的播放状态，无法自动恢复自动播放下一曲功能",
                                device_id
                            )
                            _log.info(
                                "提示：如果需要自动播放下一曲，请通过 API 重新开始播放播单"
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
                if not current_playlist_id:
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
        playlist_id: str,
    ):
        """检查单个设备的播放状态
        
        Args:
            client: XiaoAI 客户端
            device_id: 设备 ID
            playlist_id: 当前播放的播单 ID
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
            
            _log.info(
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
            
            # 更新当前状态
            self._last_status[device_id] = {
                "status": play_status,
                "audio_id": audio_id,
                "position": position,
                "duration": duration,
                "media_type": media_type,
            }
            
            # 如果检测到 position 回退，说明歌曲播放完成，立即播放下一曲
            if position_rollback:
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
                
                return
            
            # 如果播放已停止且没有播放进度，清除播放状态
            if play_status == "stopped" and duration == 0 and position == 0:
                _log.info("设备 %s 播放已停止，清除播放状态", device_id)
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
