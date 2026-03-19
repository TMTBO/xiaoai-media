#!/usr/bin/env python3
"""测试对话轮询器"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from xiaoai_media.conversation import ConversationPoller
from xiaoai_media.command_handler import CommandHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """测试轮询器"""
    _log.info("=" * 60)
    _log.info("测试对话轮询器")
    _log.info("=" * 60)
    
    # 创建轮询器和命令处理器
    poller = ConversationPoller(poll_interval=2.0)
    handler = CommandHandler()
    poller.set_command_callback(handler.handle_command)
    
    # 启动轮询
    await poller.start()
    
    # 运行 10 秒
    _log.info("轮询器运行中，将运行 10 秒...")
    _log.info("请在音箱上说：'小爱同学，播放周杰伦的晴天'")
    await asyncio.sleep(10)
    
    # 停止轮询
    await poller.stop()
    _log.info("测试完成")


if __name__ == "__main__":
    asyncio.run(main())
