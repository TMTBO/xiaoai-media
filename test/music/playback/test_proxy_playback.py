#!/usr/bin/env python3
"""测试使用代理URL播放音乐"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config


async def test_proxy_playback():
    """测试通过代理URL播放音乐"""
    print(f"音乐API地址: {config.MUSIC_API_BASE_URL}")
    print(f"设备ID: {config.MI_DID}")
    
    async with XiaoAiClient() as client:
        # 1. 获取设备列表
        devices = await client.list_devices()
        print(f"\n找到 {len(devices)} 个设备")
        
        device_id = config.MI_DID or devices[0]["deviceID"]
        device = next((d for d in devices if d["deviceID"] == device_id), None)
        print(f"使用设备: {device['name']} ({device_id})")
        
        # 2. 测试播放一个代理URL
        # 这里使用一个示例URL，实际应该从音乐API获取
        test_music_url = "https://example.com/music.mp3"  # 替换为实际URL
        
        from urllib.parse import quote
        proxy_url = f"{config.MUSIC_API_BASE_URL}/main/proxy?url={quote(test_music_url)}"
        
        print(f"\n原始URL: {test_music_url}")
        print(f"代理URL: {proxy_url}")
        
        # 3. 先停止当前播放
        try:
            print("\n停止当前播放...")
            await client.player_stop(device_id)
            await asyncio.sleep(0.5)
            print("停止成功")
        except Exception as e:
            print(f"停止失败（可能没有在播放）: {e}")
        
        # 4. 播放代理URL
        print("\n开始播放...")
        result = await client.play_url(proxy_url, device_id, _type=1)
        print(f"播放结果: {result}")
        
        if result.get("result"):
            print("\n✅ 播放成功！")
        else:
            print("\n❌ 播放失败")
            print(f"详细结果: {result.get('raw_result')}")


if __name__ == "__main__":
    asyncio.run(test_proxy_playback())
