#!/usr/bin/env python3
"""测试 MiAccount 的 serviceToken 获取"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def main():
    """测试 serviceToken 获取"""
    _log.info("=" * 60)
    _log.info("测试 MiAccount serviceToken 获取")
    _log.info("=" * 60)
    
    async with XiaoAiClient() as client:
        # 触发登录
        devices = await client.list_devices()
        _log.info("获取到 %d 个设备", len(devices))
        
        # 检查 token
        if client._account and client._account.token:
            token = client._account.token
            _log.info("Token 内容:")
            _log.info("  - userId: %s", token.get("userId"))
            _log.info("  - deviceId: %s", token.get("deviceId"))
            _log.info("  - passToken: %s", "存在" if token.get("passToken") else "不存在")
            _log.info("  - serviceToken: %s", "存在" if token.get("serviceToken") else "不存在")
            
            if token.get("serviceToken"):
                _log.info("  - serviceToken 前20字符: %s...", token["serviceToken"][:20])
        else:
            _log.error("MiAccount 没有 token！")
        
        # 测试获取对话记录
        if devices:
            device_id = devices[0]["deviceID"]
            _log.info("\n测试获取设备 %s 的对话记录...", device_id)
            conversations = await client.get_latest_ask(device_id, limit=2)
            _log.info("获取到 %d 条对话记录", len(conversations))
            for conv in conversations:
                _log.info("  - %s: %s", conv.get("time"), conv.get("query"))


if __name__ == "__main__":
    asyncio.run(main())
