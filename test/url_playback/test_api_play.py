#!/usr/bin/env python3
"""Test the /api/music/play endpoint"""
import asyncio
import aiohttp
import sys

BACKEND_API = "http://localhost:8000"
DEVICE_ID = "e01467de-11ff-4fb0-b76b-51cde0bc3b19"

async def test_api_play():
    """Test playing music through the API"""
    print("=" * 60)
    print("Testing /api/music/play endpoint")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Prepare test data
        songs = [
            {
                "id": "003aAYrm3GE0Ac",
                "name": "稻香",
                "singer": "周杰伦",
                "platform": "tx"
            }
        ]
        
        play_data = {
            "songs": songs,
            "index": 0,
            "device_id": DEVICE_ID
        }
        
        print(f"\nSending play request for: {songs[0]['name']} - {songs[0]['singer']}")
        print(f"Device: {DEVICE_ID}")
        
        async with session.post(
            f"{BACKEND_API}/api/music/play",
            json=play_data
        ) as resp:
            result = await resp.json()
            print(f"\nResponse status: {resp.status}")
            print(f"Response: {result}")
            
            if resp.status == 200 and result.get("url"):
                print("\n" + "=" * 60)
                print("✓ SUCCESS! Music is playing via URL!")
                print(f"  URL: {result['url'][:80]}...")
                print(f"  Method: {result.get('method', 'N/A')}")
                print("=" * 60)
                return True
            else:
                print("\n✗ Failed to play music")
                return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_api_play())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
