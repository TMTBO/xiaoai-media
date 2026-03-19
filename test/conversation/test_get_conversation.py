#!/usr/bin/env python3
"""测试获取对话记录功能

这个脚本测试 get_latest_ask() 方法是否能正确获取对话记录。
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """测试获取对话记录"""
    _log.info("=" * 60)
    _log.info("测试获取对话记录功能")
    _log.info("=" * 60)
    
    try:
        async with XiaoAiClient() as client:
            # 获取设备列表
            devices = await client.list_devices()
            if not devices:
                _log.error("没有找到设备")
                return
            
            _log.info("找到 %d 个设备", len(devices))
            
            # 测试第一个设备
            device = devices[0]
            device_id = device["deviceID"]
            device_name = device.get("name", "未知")
            
            _log.info("测试设备: %s (%s)", device_name, device_id)
            _log.info("-" * 60)
            
            # 获取对话记录
            conversations = await client.get_latest_ask(device_id)
            
            if not conversations:
                _log.info("暂无对话记录")
            else:
                _log.info("获取到 %d 条对话记录:", len(conversations))
                for i, conv in enumerate(conversations, 1):
                    _log.info("")
                    _log.info("对话 %d:", i)
                    _log.info("  时间: %d", conv["time"])
                    _log.info("  问题: %s", conv["query"])
                    _log.info("  回答: %s", conv["answer"])
            
            _log.info("-" * 60)
            _log.info("测试完成！")
            
    except Exception as e:
        _log.error("测试失败: %s", e, exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
