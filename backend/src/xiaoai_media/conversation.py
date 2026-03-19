"""Conversation monitoring module for XiaoAI speakers.

This module polls conversation history from speakers and triggers
music playback when play commands are detected.
"""

import asyncio
import logging
import re
import time
from typing import Callable

from xiaoai_media.client import XiaoAiClient

_log = logging.getLogger(__name__)


class ConversationPoller:
    """Polls conversation history from XiaoAI speakers and processes commands."""

    def __init__(self, poll_interval: float = 2.0):
        """Initialize the conversation poller.
        
        Args:
            poll_interval: Seconds between polling attempts (default: 2.0)
        """
        self.poll_interval = poll_interval
        self.last_timestamp: dict[str, int] = {}  # device_id -> last timestamp
        self.running = False
        self._task: asyncio.Task | None = None
        self._command_callback: Callable | None = None

    def set_command_callback(self, callback: Callable):
        """Set the callback function to handle detected commands.
        
        Args:
            callback: async function(device_id: str, query: str) -> None
        """
        self._command_callback = callback

    async def start(self):
        """Start the conversation polling loop."""
        if self.running:
            _log.warning("对话轮询器已在运行")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._poll_loop())
        _log.info("对话轮询器已启动 (轮询间隔: %.1f秒)", self.poll_interval)

    async def stop(self):
        """Stop the conversation polling loop."""
        if not self.running:
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        _log.info("对话轮询器已停止")

    async def _poll_loop(self):
        """Main polling loop that fetches conversations from all devices."""
        try:
            while self.running:
                try:
                    await self._poll_conversations()
                except Exception as e:
                    _log.error("对话轮询出错: %s", e, exc_info=True)
                
                await asyncio.sleep(self.poll_interval)
        except asyncio.CancelledError:
            _log.info("对话轮询已取消")
            raise

    async def _poll_conversations(self):
        """Poll conversations from all available devices."""
        try:
            async with XiaoAiClient() as client:
                devices = await client.list_devices()
                _log.debug("轮询 %d 个设备的对话记录", len(devices))
                
                for device in devices:
                    device_id = device.get("deviceID")
                    device_name = device.get("name", "未知设备")
                    if not device_id:
                        continue
                    
                    # Initialize timestamp for new devices (start from 0 to catch recent conversations)
                    if device_id not in self.last_timestamp:
                        self.last_timestamp[device_id] = 0
                        _log.debug("初始化设备 %s (%s) 的时间戳: 0", device_name, device_id)
                    
                    try:
                        conversations = await client.get_latest_ask(device_id, limit=2)
                        _log.debug("设备 %s 获取到 %d 条对话记录", device_name, len(conversations))
                        await self._process_conversations(device_id, conversations)
                    except Exception as e:
                        _log.warning(
                            "获取设备 %s 的对话记录失败: %s",
                            device_id,
                            e,
                        )
        except Exception as e:
            _log.error("轮询对话记录失败: %s", e, exc_info=True)

    async def _process_conversations(self, device_id: str, conversations: list[dict]):
        """Process conversation records and trigger commands for new ones.
        
        Args:
            device_id: Device ID
            conversations: List of conversation records
        """
        if not conversations:
            _log.debug("设备 %s 没有对话记录", device_id)
            return
        
        _log.debug("处理设备 %s 的 %d 条对话记录", device_id, len(conversations))
        
        for record in conversations:
            timestamp = record.get("time", 0)
            query = record.get("query", "").strip()
            answer = record.get("answer", "").strip()
            
            _log.debug("对话记录: 时间戳=%d, 查询=%s, 回答=%s, 上次时间戳=%d", 
                      timestamp, query, answer, self.last_timestamp.get(device_id, 0))
            
            # Skip if we've already processed this conversation
            if timestamp <= self.last_timestamp.get(device_id, 0):
                _log.debug("跳过已处理的对话 (时间戳: %d)", timestamp)
                continue
            
            # Update last timestamp
            self.last_timestamp[device_id] = timestamp
            
            # Skip empty queries
            if not query:
                _log.debug("跳过空查询")
                continue
            
            # Check if XiaoAi already responded
            # Note: XiaoAi's "播放失败" voice response may not be recorded in answer field
            if answer:
                _log.debug("对话已有回复: %s", answer)
            
            _log.info(
                "检测到新对话 (设备 %s): %s (时间戳: %d)",
                device_id,
                query,
                timestamp,
            )
            
            # Trigger command callback if set
            if self._command_callback:
                try:
                    await self._command_callback(device_id, query)
                except Exception as e:
                    _log.error(
                        "命令回调处理失败 (指令: '%s'): %s",
                        query,
                        e,
                        exc_info=True,
                    )


def parse_play_command(query: str) -> dict | None:
    """Parse a play command from natural language query.
    
    Detects patterns like:
    - "播放周杰伦的晴天"
    - "播放晴天"
    - "播放歌曲晴天"
    - "打开周杰伦的歌"
    
    Returns:
        dict with 'action' and 'query' keys, or None if not a play command
    """
    query = query.strip()
    
    # Pattern: 播放/打开 [歌手的] 歌曲名
    play_patterns = [
        r"^(?:播放|打开)(?:歌曲)?(.+)$",
    ]
    
    for pattern in play_patterns:
        match = re.match(pattern, query)
        if match:
            content = match.group(1).strip()
            if content:
                return {
                    "action": "play",
                    "query": content,
                }
    
    return None
