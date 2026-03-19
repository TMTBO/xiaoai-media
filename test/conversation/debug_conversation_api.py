#!/usr/bin/env python3
"""调试对话 API 调用

这个脚本帮助调试对话 API 的认证和请求问题。
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend" / "src"))

from aiohttp import ClientSession
from xiaoai_media.client import XiaoAiClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_log = logging.getLogger(__name__)


async def test_conversation_api():
    """测试对话 API"""
    _log.info("=" * 60)
    _log.info("调试对话 API")
    _log.info("=" * 60)
    
    # 1. 读取 token 文件
    token_file = Path(__file__).resolve().parents[1] / ".mi.token"
    _log.info("Token 文件路径: %s", token_file)
    _log.info("Token 文件存在: %s", token_file.exists())
    
    if token_file.exists():
        with open(token_file, "r") as f:
            token_data = json.load(f)
            user_id = token_data.get("userId")
            micoapi = token_data.get("micoapi", [])
            service_token = micoapi[1] if len(micoapi) > 1 else None
            
            _log.info("UserId: %s", user_id)
            _log.info("ServiceToken 长度: %s", len(service_token) if service_token else 0)
            _log.info("ServiceToken 前20字符: %s...", service_token[:20] if service_token else "None")
    else:
        _log.error("Token 文件不存在！")
        return
    
    # 2. 获取设备信息
    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        if not devices:
            _log.error("没有找到设备")
            return
        
        device = devices[0]
        device_id = device["deviceID"]
        hardware = device.get("hardware", "LX06")
        device_name = device.get("name", "未知")
        
        _log.info("-" * 60)
        _log.info("设备信息:")
        _log.info("  名称: %s", device_name)
        _log.info("  DeviceID: %s", device_id)
        _log.info("  Hardware: %s", hardware)
        
        # 3. 构建请求
        timestamp = int(time.time() * 1000)
        url = f"https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
        
        _log.info("-" * 60)
        _log.info("API 请求:")
        _log.info("  URL: %s", url)
        
        # 4. 测试不同的 cookie 组合
        cookie_combinations = [
            # 组合1: 只有 deviceId
            {"deviceId": device_id},
            # 组合2: deviceId + serviceToken
            {"deviceId": device_id, "serviceToken": service_token} if service_token else None,
            # 组合3: 完整 cookies
            {"deviceId": device_id, "serviceToken": service_token, "userId": str(user_id)} if service_token and user_id else None,
        ]
        
        for i, cookies in enumerate(cookie_combinations, 1):
            if cookies is None:
                continue
                
            _log.info("-" * 60)
            _log.info("测试组合 %d: %s", i, list(cookies.keys()))
            
            try:
                async with ClientSession() as session:
                    async with session.get(url, cookies=cookies, timeout=15) as resp:
                        _log.info("  响应状态: %d", resp.status)
                        
                        if resp.status == 200:
                            data = await resp.json()
                            _log.info("  响应 code: %s", data.get("code"))
                            
                            if d := data.get("data"):
                                records = json.loads(d).get("records", [])
                                _log.info("  对话记录数: %d", len(records))
                                
                                for j, record in enumerate(records, 1):
                                    _log.info("  对话 %d:", j)
                                    _log.info("    时间: %d", record.get("time", 0))
                                    _log.info("    问题: %s", record.get("query", ""))
                            else:
                                _log.warning("  响应中没有 data 字段")
                            
                            _log.info("✅ 组合 %d 成功！", i)
                            break
                        else:
                            text = await resp.text()
                            _log.warning("  响应内容: %s", text[:200])
                            
            except Exception as e:
                _log.error("  请求失败: %s", e)
        
        _log.info("=" * 60)
        _log.info("测试完成")


if __name__ == "__main__":
    asyncio.run(test_conversation_api())
