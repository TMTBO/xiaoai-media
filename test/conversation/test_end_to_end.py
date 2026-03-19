#!/usr/bin/env python3
"""端到端测试：模拟对话监听到播放的完整流程"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media.command_handler import CommandHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """端到端测试"""
    _log.info("=" * 60)
    _log.info("端到端测试：对话监听 → 播放")
    _log.info("=" * 60)
    
    try:
        # 1. 获取设备和对话
        async with XiaoAiClient() as client:
            devices = await client.list_devices()
            if not devices:
                _log.error("没有找到设备")
                return
            
            device = devices[0]
            device_id = device["deviceID"]
            device_name = device.get("name", "未知")
            
            _log.info("测试设备: %s (%s)", device_name, device_id)
            _log.info("-" * 60)
            
            # 2. 获取最新对话
            _log.info("步骤 1: 获取对话记录")
            conversations = await client.get_latest_ask(device_id)
            
            if not conversations:
                _log.warning("暂无对话记录，请先对音箱说话")
                _log.info("例如：'小爱同学，播放周杰伦的晴天'")
                return
            
            _log.info("获取到 %d 条对话", len(conversations))
            latest = conversations[0]
            query = latest["query"]
            _log.info("最新对话: %s", query)
            _log.info("-" * 60)
            
            # 3. 测试命令处理
            _log.info("步骤 2: 处理播放指令")
            handler = CommandHandler()
            await handler.handle_command(device_id, query)
            
            _log.info("-" * 60)
            _log.info("✅ 测试完成！")
            _log.info("")
            _log.info("如果看到 '播放成功' 的日志，说明功能正常工作。")
            _log.info("现在可以启动完整服务，对话监听会自动拦截播放指令。")
            
    except Exception as e:
        _log.error("测试失败: %s", e, exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
