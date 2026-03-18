#!/usr/bin/env python3
"""Test complete music play flow: search -> get URL -> play"""
import asyncio
import aiohttp
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config

MUSIC_API_BASE = "http://localhost:5050"

async def test_music_flow():
    """Test: search song -> get URL -> play"""
    print("Step 1: Search for a song")
    async with aiohttp.ClientSession() as session:
        # Search
        search_url = f"{MUSIC_API_BASE}/api/v3/search"
        async with session.post(
            search_url,
            json={"platform": "tx", "query": "稻香", "page": 1, "limit": 1}
        ) as resp:
            search_data = await resp.json()
            if not search_data.get("data", {}).get("list"):
                print("No songs found")
                return False
            
            song = search_data["data"]["list"][0]
            print(f"Found: {song['name']} - {song['singer']}")
            
        # Get URL
        print("\nStep 2: Get playback URL")
        song_id = song["id"]
        url_endpoint = f"{MUSIC_API_BASE}/api/v3/tx/url/{song_id}"
        async with session.get(url_endpoint) as resp:
            url_data = await resp.json()
            play_url = url_data.get("data", {}).get("url")
            
            if not play_url:
                print("Failed to get URL")
                return False
            print(f"Got URL: {play_url[:80]}...")
            
        # Play
        print("\nStep 3: Play the URL")
        async with XiaoAiClient() as client:
            result = await client.play_url(play_url, config.MI_DID)
            print(f"Play result: {result}")
            return result.get("result") == True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_music_flow())
        if success:
            print("\n✓ Complete flow test passed!")
        else:
            print("\n✗ Flow test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
