#!/usr/bin/env python3
"""测试播放拦截 - 模拟完整流程"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media.command_handler import CommandHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """测试播放拦截"""
    _log.info("=" * 60)
    _log.info("测试播放拦截流程")
    _log.info("=" * 60)
    
    # 模拟检测到播放指令
    device_id = "e01467de-11ff-4fb0-b76b-51cde0bc3b19"
    query = "播放周杰伦的稻香"
    
    _log.info("模拟检测到指令: %s", query)
    _log.info("")
    
    # 创建命令处理器
    handler = CommandHandler()
    
    # 处理播放指令
    await handler.handle_command(device_id, query)
    
    _log.info("")
    _log.info("=" * 60)
    _log.info("测试完成，请检查音箱是否正常播放")
    _log.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
