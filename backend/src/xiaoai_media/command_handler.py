"""Command handler for processing voice commands from speakers."""

import logging
import re

from xiaoai_media import config
from xiaoai_media.api.dependencies import get_client_sync
from xiaoai_media.services.voice_command_service import VoiceCommandService

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

        # 直接调用 VoiceCommandService 处理命令
        try:
            result = await VoiceCommandService.execute_command(
                text=processed_query,
                device_id=device_id
            )
            _log.info("语音命令处理成功: action=%s", result.get("action"))

        except Exception as e:
            _log.error("语音命令处理失败: %s", e, exc_info=True)
            try:
                client = get_client_sync()
                await client.text_to_speech("命令处理出错", device_id)
            except:
                pass
