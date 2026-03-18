#!/usr/bin/env python3
"""Test playlist control: play -> next -> prev"""
import asyncio
import aiohttp
import sys

BACKEND_API = "http://localhost:8000"
DEVICE_ID = "e01467de-11ff-4fb0-b76b-51cde0bc3b19"

async def test_playlist_control():
    """Test playlist navigation"""
    print("=" * 60)
    print("Testing Playlist Control")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Create a playlist with 3 songs
        songs = [
            {"id": "003aAYrm3GE0Ac", "name": "稻香", "singer": "周杰伦", "platform": "tx"},
            {"id": "004Z8Ihr0JIu5s", "name": "青花瓷", "singer": "周杰伦", "platform": "tx"},
            {"id": "002bHE0l16imOO", "name": "晴天", "singer": "周杰伦", "platform": "tx"}
        ]
        
        # Step 1: Play first song
        print("\n[Step 1] Playing first song...")
        async with session.post(
            f"{BACKEND_API}/api/music/play",
            json={"songs": songs, "index": 0, "device_id": DEVICE_ID}
        ) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✓ Playing: {result['current']['name']}")
                print(f"  URL: {result['url'][:60]}...")
            else:
                print(f"✗ Failed: {result}")
                return False
        
        await asyncio.sleep(2)
        
        # Step 2: Next song
        print("\n[Step 2] Playing next song...")
        async with session.post(
            f"{BACKEND_API}/api/music/next",
            json={"device_id": DEVICE_ID}
        ) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✓ Playing: {result['current']['name']}")
                print(f"  Index: {result['index']}/{result['total']}")
                print(f"  URL: {result['url'][:60]}...")
            else:
                print(f"✗ Failed: {result}")
                return False
        
        await asyncio.sleep(2)
        
        # Step 3: Previous song
        print("\n[Step 3] Playing previous song...")
        async with session.post(
            f"{BACKEND_API}/api/music/prev",
            json={"device_id": DEVICE_ID}
        ) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✓ Playing: {result['current']['name']}")
                print(f"  Index: {result['index']}/{result['total']}")
                print(f"  URL: {result['url'][:60]}...")
            else:
                print(f"✗ Failed: {result}")
                return False
        
        print("\n" + "=" * 60)
        print("✓ All playlist controls working!")
        print("=" * 60)
        return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_playlist_control())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
