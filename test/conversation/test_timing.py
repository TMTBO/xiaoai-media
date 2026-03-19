#!/usr/bin/env python3
"""测试对话拦截的时间线"""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """测试对话时间线"""
    _log.info("=" * 60)
    _log.info("测试对话拦截时间线")
    _log.info("=" * 60)
    _log.info("请在音箱上说：'小爱同学，播放周杰伦的晴天'")
    _log.info("然后观察对话记录中是否已经有 answer")
    _log.info("")
    
    await asyncio.sleep(3)
    
    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        if not devices:
            _log.error("没有找到设备")
            return
        
        device_id = devices[0]["deviceID"]
        device_name = devices[0].get("name", "")
        
        _log.info("监控设备: %s (%s)", device_name, device_id)
        _log.info("")
        
        # 持续监控 10 秒
        for i in range(20):
            conversations = await client.get_latest_ask(device_id, limit=2)
            
            if conversations:
                _log.info("--- 第 %d 次查询 (%.1f 秒) ---", i + 1, (i + 1) * 0.5)
                for conv in conversations:
                    timestamp = conv.get("time", 0)
                    query = conv.get("query", "")
                    answer = conv.get("answer", "")
                    
                    # 计算对话发生的时间
                    now_ms = int(time.time() * 1000)
                    age_ms = now_ms - timestamp
                    
                    _log.info("  时间戳: %d (%.1f 秒前)", timestamp, age_ms / 1000)
                    _log.info("  问题: %s", query)
                    _log.info("  回答: %s", answer if answer else "(无)")
                    _log.info("")
            
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
