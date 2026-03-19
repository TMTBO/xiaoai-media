#!/usr/bin/env python3
"""测试对话监听功能

这个脚本会启动对话监听，并在检测到播放指令时输出日志。
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend" / "src"))

from xiaoai_media.conversation import ConversationPoller
from xiaoai_media.command_handler import CommandHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """运行对话监听测试"""
    _log.info("=" * 60)
    _log.info("对话监听功能测试")
    _log.info("=" * 60)
    _log.info("请对音箱说话，例如：'小爱同学，播放周杰伦的晴天'")
    _log.info("按 Ctrl+C 停止测试")
    _log.info("=" * 60)
    
    # 创建对话轮询器和命令处理器
    poller = ConversationPoller(poll_interval=2.0)
    handler = CommandHandler()
    poller.set_command_callback(handler.handle_command)
    
    try:
        # 启动轮询
        await poller.start()
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        _log.info("\n收到停止信号，正在关闭...")
    finally:
        await poller.stop()
        _log.info("测试结束")


if __name__ == "__main__":
    asyncio.run(main())
