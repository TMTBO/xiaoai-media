#!/usr/bin/env python3
"""Test script for new miservice_fork API methods."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient


async def test_player_controls():
    """Test the new player control methods."""
    print("Testing new miservice_fork player control API...")
    
    async with XiaoAiClient() as client:
        # List devices
        print("\n1. Listing devices...")
        devices = await client.list_devices()
        if not devices:
            print("No devices found!")
            return
        
        device = devices[0]
        device_id = device["deviceID"]
        device_name = device.get("name", "Unknown")
        print(f"Using device: {device_name} ({device_id})")
        
        # Test play URL
        print("\n2. Testing play_url...")
        test_url = "http://music.163.com/song/media/outer/url?id=447925558.mp3"
        result = await client.play_url(test_url, device_id, _type=1)
        print(f"Play result: {result}")
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Test get status
        print("\n3. Testing player_get_status...")
        status = await client.player_get_status(device_id)
        print(f"Status: {status}")
        
        # Test pause
        print("\n4. Testing player_pause...")
        pause_result = await client.player_pause(device_id)
        print(f"Pause result: {pause_result}")
        
        await asyncio.sleep(2)
        
        # Test resume
        print("\n5. Testing player_play (resume)...")
        play_result = await client.player_play(device_id)
        print(f"Play result: {play_result}")
        
        await asyncio.sleep(2)
        
        # Test stop
        print("\n6. Testing player_stop...")
        stop_result = await client.player_stop(device_id)
        print(f"Stop result: {stop_result}")
        
        print("\n✓ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_player_controls())
