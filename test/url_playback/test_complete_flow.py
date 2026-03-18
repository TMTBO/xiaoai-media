#!/usr/bin/env python3
"""Complete test: search -> get URL -> play on speaker"""
import asyncio
import aiohttp
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config

MUSIC_API_BASE = "http://localhost:5050"

async def test_complete_flow():
    """Test complete music play flow"""
    print("=" * 60)
    print("Complete Music Play Flow Test")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Search
        print("\n[Step 1] Searching for '稻香'...")
        search_url = f"{MUSIC_API_BASE}/api/v3/search"
        async with session.post(
            search_url,
            json={"platform": "tx", "query": "稻香", "page": 1, "limit": 1}
        ) as resp:
            search_data = await resp.json()
            if not search_data.get("data", {}).get("list"):
                print("✗ No songs found")
                return False
            
            song = search_data["data"]["list"][0]
            print(f"✓ Found: {song['name']} - {song['singer']}")
            print(f"  Song ID: {song['id']}")
            
        # Step 2: Get playback URL
        print("\n[Step 2] Getting playback URL...")
        song_id = song["id"]
        platform = song["source"]
        
        play_url_endpoint = f"{MUSIC_API_BASE}/api/v3/play"
        async with session.post(
            play_url_endpoint,
            json={"songId": song_id, "platform": platform, "quality": "128k"}
        ) as resp:
            url_data = await resp.json()
            play_url = url_data.get("data", {}).get("url")
            
            if not play_url:
                print(f"✗ Failed to get URL: {url_data}")
                return False
            print(f"✓ Got URL: {play_url[:80]}...")
            
        # Step 3: Play on speaker
        print(f"\n[Step 3] Playing on device {config.MI_DID}...")
        async with XiaoAiClient() as client:
            result = await client.play_url(play_url, config.MI_DID)
            print(f"✓ Play result: {result}")
            
            if result.get("result") == True:
                print("\n" + "=" * 60)
                print("✓ SUCCESS! Song is now playing on your speaker!")
                print("=" * 60)
                return True
            else:
                print("\n✗ Play command returned False")
                return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_complete_flow())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
