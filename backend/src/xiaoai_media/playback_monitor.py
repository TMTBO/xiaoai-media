"""播放监控模块

监控设备播放状态，在歌曲播放完成时自动播放下一曲。
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
    
    定期检查设备播放状态，当检测到歌曲播放完成时自动播放下一曲。
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
        # device_id -> {"status": "playing"|"paused"|"stopped", "media_id": str}
        self._last_status: Dict[str, dict] = {}

    async def start(self):
        """启动播放监控"""
        if self.running:
            _log.warning("播放监控器已在运行")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._monitor_loop())
        _log.info("播放监控器已启动 (轮询间隔: %.1f秒)", self.poll_interval)

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
        """检查所有设备的播放状态"""
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
                
                try:
                    await self._check_device_status(client, device_id, current_playlist_id)
                except Exception as e:
                    _log.debug(
                        "检查设备 %s 播放状态失败: %s",
                        device_id,
                        e,
                    )
        except Exception as e:
            _log.error("检查设备播放状态失败: %s", e, exc_info=True)

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
            
            # 解析状态数据结构
            # status_result = {
            #     'device': 'Xiaomi 智能音箱 Pro(...)',
            #     'status': {
            #         'code': 0,
            #         'message': '...',
            #         'data': {
            #             'code': 0,
            #             'info': '{ "status": 1, "volume": 6, ... }'  # JSON 字符串
            #         }
            #     }
            # }
            
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
            volume = info.get("volume", 0)
            loop_type = info.get("loop_type", 0)
            media_type = info.get("media_type", 0)
            
            # 播放详情
            play_song_detail = info.get("play_song_detail", {})
            audio_id = play_song_detail.get("audio_id", "")
            position = play_song_detail.get("position", 0)  # 当前播放位置（毫秒）
            duration = play_song_detail.get("duration", 0)  # 总时长（毫秒）
            
            # 转换状态码为字符串
            play_status = {0: "stopped", 1: "playing", 2: "paused"}.get(status_code, "unknown")
            
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
            last_play_status = last_status.get("status")
            last_audio_id = last_status.get("audio_id", "")
            
            # 更新当前状态
            self._last_status[device_id] = {
                "status": play_status,
                "audio_id": audio_id,
                "position": position,
                "duration": duration,
            }
            
            # 检测播放完成的条件：
            # 1. 从 playing 变为 stopped（歌曲播放完成）
            # 2. 或者接近结尾时（最后 2 秒内）从 playing 变为 paused
            is_near_end = duration > 0 and position >= duration - 2000

            # _log.info("last_status: %s, current_status: %s, %s", last_play_status, play_status, is_near_end)
            
            if last_play_status == "playing":
                if play_status == "playing" and duration == 0 and position == 0:
                    _log.info(
                        "检测到设备 %s 自然播放完成，准备播放下一曲",
                        device_id,
                    )
                    await self._play_next(device_id, playlist_id)
                elif play_status == "stopped":
                    _log.info(
                        "检测到设备 %s 播放完成 (playing -> stopped)，准备播放下一曲",
                        device_id,
                    )
                    await self._play_next(device_id, playlist_id)
                    
                elif play_status == "paused" and is_near_end:
                    _log.info(
                        "检测到设备 %s 接近播放结束 (position=%d/%d)，准备播放下一曲",
                        device_id,
                        position,
                        duration,
                    )
                    await self._play_next(device_id, playlist_id)
            
        except Exception as e:
            _log.debug("获取设备 %s 播放状态失败: %s", device_id, e)
    
    async def _play_next(self, device_id: str, playlist_id: str):
        """播放下一曲
        
        Args:
            device_id: 设备 ID
            playlist_id: 播单 ID
        """
        try:
            # 等待一小段时间，确保设备已经完全停止
            await asyncio.sleep(0.5)
            
            # 播放下一曲
            result = await PlaylistService.play_next_in_playlist(
                playlist_id,
                device_id,
            )
            _log.info(
                "自动播放下一曲成功: %s",
                result.get("item", {}).get("title", ""),
            )
        except Exception as e:
            _log.error("自动播放下一曲失败: %s, 自动跳过", e, exc_info=True)
            self._play_next(device_id, playlist_id)
            # 如果播放失败，清除当前播单状态
            self._state_service.set(f"current_playlist_{device_id}", None)
