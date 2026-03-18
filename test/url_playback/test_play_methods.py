#!/usr/bin/env python3
"""Test different methods to play URL on Xiaomi speaker"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config

TEST_URL = "http://wx.music.tc.qq.com/M5000020wJDo3cx0j3.mp3?guid=History&vkey=B44C493B6996D3787D254E950DFD29E6E1F3C86B871FB366FAC5328F776C806DACBE34772A8AA3948C800D4FE5830897790EB852E701E864__v21e297a10&uin=871058163&fromtag=api.ikunshare.com"

async def test_methods():
    """Test different play methods"""
    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        device = devices[0]
        did = device["deviceID"]
        miot_did = device.get("miotDID")
        hardware = device.get("hardware")
        
        print(f"Device: {device['name']}")
        print(f"DeviceID: {did}")
        print(f"MiotDID: {miot_did}")
        print(f"Hardware: {hardware}")
        print("=" * 60)
        
        # Method 1: player_play_url with type=1
        print("\n[Method 1] player_play_url with type=1")
        try:
            result = await client._na_service.ubus_request(
                did, "player_play_url", "mediaplayer", {"url": TEST_URL, "type": 1}
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(2)
        
        # Method 2: player_play_url without type
        print("\n[Method 2] player_play_url without type")
        try:
            result = await client._na_service.ubus_request(
                did, "player_play_url", "mediaplayer", {"url": TEST_URL}
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(2)
        
        # Method 3: player_play_music
        print("\n[Method 3] player_play_music")
        try:
            result = await client._na_service.ubus_request(
                did, "player_play_music", "mediaplayer", {"url": TEST_URL}
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(2)
        
        # Method 4: player_play_operation with url
        print("\n[Method 4] player_play_operation")
        try:
            result = await client._na_service.ubus_request(
                did, "player_play_operation", "mediaplayer", {"url": TEST_URL, "type": "url"}
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_methods())
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
