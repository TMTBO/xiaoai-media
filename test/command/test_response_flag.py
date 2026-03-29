#!/usr/bin/env python3
"""测试 execute_text_command 的 response_flag 参数"""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def test_response_flag():
    """测试不同 response_flag 值的效果"""
    _log.info("=" * 60)
    _log.info("测试 execute_text_command 的 response_flag 参数")
    _log.info("=" * 60)

    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        if not devices:
            _log.error("没有找到设备")
            return

        device = devices[0]
        device_id = device["deviceID"]
        device_name = device.get("name", "未知")
        miot_did = device.get("miotDID")
        hardware = device.get("hardware")

        _log.info("测试设备: %s (%s)", device_name, device_id)
        _log.info("Hardware: %s, MiotDID: %s", hardware, miot_did)
        _log.info("-" * 60)

        # 测试 1: response_flag=1 (当前默认值，期望有语音回应)
        _log.info("\n测试 1: response_flag=1 (当前默认，silent=False)")
        _log.info("发送命令: 现在几点")
        _log.info("注意观察音箱是否有语音回应...")

        result1 = await client.execute_text_command("现在几点", device_id, silent=False)
        _log.info("返回结果: %s", result1)

        # 等待 3 秒，观察音箱反应
        await asyncio.sleep(3)

        # 获取会话历史，查看是否有 answer
        conversations1 = await client.get_latest_ask(device_id, limit=2)
        _log.info("会话历史:")
        for conv in conversations1:
            _log.info("  问题: %s", conv.get("query", ""))
            _log.info("  回答: %s", conv.get("answer", "") or "(无)")
            _log.info("")

        _log.info("-" * 60)
        await asyncio.sleep(2)

        # 测试 2: response_flag=0 (当前 silent=True，期望静默执行)
        _log.info("\n测试 2: response_flag=0 (当前 silent=True)")
        _log.info("发送命令: 今天天气")
        _log.info("注意观察音箱是否有语音回应...")

        result2 = await client.execute_text_command("今天天气", device_id, silent=True)
        _log.info("返回结果: %s", result2)

        # 等待 3 秒，观察音箱反应
        await asyncio.sleep(3)

        # 获取会话历史，查看是否有 answer
        conversations2 = await client.get_latest_ask(device_id, limit=2)
        _log.info("会话历史:")
        for conv in conversations2:
            _log.info("  问题: %s", conv.get("query", ""))
            _log.info("  回答: %s", conv.get("answer", "") or "(无)")
            _log.info("")

        _log.info("=" * 60)
        _log.info("\n总结:")
        _log.info("1. 如果 response_flag=1 时音箱有语音回应，说明参数正确")
        _log.info("2. 如果 response_flag=1 时音箱没有语音回应，说明参数可能反了")
        _log.info("3. 同时查看会话历史中的 answer 字段是否有值")
        _log.info("")
        _log.info("注意：某些命令可能天然不会有详细回答，只会说'好的'")


if __name__ == "__main__":
    asyncio.run(test_response_flag())
