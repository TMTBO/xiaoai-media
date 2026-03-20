"""Command handler for processing voice commands from speakers."""

import logging
import re

import aiohttp

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient

_log = logging.getLogger(__name__)


class CommandHandler:
    """Handles voice commands detected from speaker conversations."""

    def __init__(self, music_api_base_url: str | None = None):
        """Initialize command handler.

        Args:
            music_api_base_url: Base URL for music API (defaults to config)
        """
        self.music_api_base_url = (
            music_api_base_url or config.MUSIC_API_BASE_URL
        ).rstrip("/")

    async def handle_command(self, device_id: str, query: str):
        """Handle a voice command from a speaker.

        Args:
            device_id: Device ID that issued the command
            query: Voice command text
        """
        _log.info("收到设备 %s 的指令: %s", device_id, query)

        # 检查是否应该处理该指令（唤醒词过滤）
        if not config.should_handle_command(query):
            _log.debug("指令未包含唤醒词，忽略: %s", query)
            return

        # 预处理指令（移除唤醒词等）
        processed_query = config.preprocess_command(query)
        _log.debug("预处理后的指令: %s", processed_query)

        # Use the unified voice-command endpoint from music.py
        # This handles playlists, charts, search, and other commands
        try:
            url = f"{self.music_api_base_url}/api/music/voice-command"

            _log.info("调用统一语音命令端点: %s", url)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"text": processed_query, "device_id": device_id},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        _log.error(
                            "语音命令 API 返回错误: status=%d, body=%s",
                            resp.status,
                            error_text,
                        )

                        # Send error feedback to speaker
                        async with XiaoAiClient() as client:
                            if resp.status == 404:
                                await client.text_to_speech(
                                    "没有找到匹配的内容", device_id
                                )
                            else:
                                await client.text_to_speech("命令处理失败", device_id)
                        return

                    result = await resp.json(content_type=None)
                    _log.info("语音命令处理成功: action=%s", result.get("action"))

        except Exception as e:
            _log.error("语音命令处理失败: %s", e, exc_info=True)
            try:
                async with XiaoAiClient() as client:
                    await client.text_to_speech("命令处理出错", device_id)
            except:
                pass
