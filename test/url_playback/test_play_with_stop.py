#!/usr/bin/env python3
"""Test play URL with stop first"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config

# Try a simple, publicly accessible MP3
TEST_URL = "http://music.163.com/song/media/outer/url?id=1901371647.mp3"

async def test_play_with_stop():
    """Test playing URL after stopping current playback"""
    async with XiaoAiClient() as client:
        did = config.MI_DID
        
        print("=" * 60)
        print("Testing Play URL with Stop First")
        print("=" * 60)
        
        # Step 1: Stop current playback
        print("\n[Step 1] Stopping current playback...")
        try:
            result = await client.send_command("停止播放", did)
            print(f"Stop result: {result}")
        except Exception as e:
            print(f"Stop error: {e}")
        
        await asyncio.sleep(2)
        
        # Step 2: Try to play URL
        print(f"\n[Step 2] Playing URL: {TEST_URL}")
        try:
            result = await client._na_service.ubus_request(
                did, "player_play_url", "mediaplayer", {"url": TEST_URL, "type": 1}
            )
            print(f"Play result: {result}")
        except Exception as e:
            print(f"Play error: {e}")
        
        await asyncio.sleep(3)
        
        # Step 3: Check player status
        print("\n[Step 3] Checking player status...")
        try:
            result = await client._na_service.ubus_request(
                did, "player_get_play_status", "mediaplayer", {}
            )
            print(f"Status: {result}")
        except Exception as e:
            print(f"Status error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_play_with_stop())
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
