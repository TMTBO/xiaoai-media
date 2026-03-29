#!/usr/bin/env python3
"""Test command blocking when device is playing."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from xiaoai_media.client import XiaoAiClient


async def test_command_blocking():
    """Test that commands are blocked when device is playing."""
    async with XiaoAiClient() as client:
        # Get device list
        devices = await client.list_devices()
        if not devices:
            print("❌ No devices found")
            return
        
        device_id = devices[0]["deviceID"]
        device_name = devices[0].get("name", "Unknown")
        print(f"📱 Testing with device: {device_name} ({device_id})")
        
        # Check current player status
        print("\n1️⃣ Checking player status...")
        status = await client.player_get_status(device_id)
        print(f"   Status: {status}")
        
        play_status = status.get("status", {})
        if isinstance(play_status, dict):
            is_playing = play_status.get("status") == 1
        else:
            is_playing = play_status == 1
        
        print(f"   Is playing: {is_playing}")
        
        # Try to send a command
        print("\n2️⃣ Sending test command...")
        result = await client.send_command("今天天气怎么样", device_id)
        print(f"   Result: {result}")
        
        if result.get("blocked"):
            print(f"   ✅ Command was blocked: {result.get('error')}")
        else:
            print(f"   ℹ️  Command was executed (device not playing)")


if __name__ == "__main__":
    asyncio.run(test_command_blocking())
