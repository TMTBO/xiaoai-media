#!/usr/bin/env python3
"""测试小米账号认证"""

import asyncio
import sys
from pathlib import Path

# Add backend src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient


async def main():
    print("Testing Xiaomi account authentication...")
    print("=" * 60)

    try:
        async with XiaoAiClient() as client:
            print("✓ Client connected successfully")

            # Test device list
            print("\nFetching device list...")
            devices = await client.list_devices(force_refresh=True)

            if devices:
                print(f"✓ Found {len(devices)} device(s):")
                for i, dev in enumerate(devices, 1):
                    name = dev.get("name", "Unknown")
                    hardware = dev.get("hardware", "Unknown")
                    device_id = dev.get("deviceID", "Unknown")
                    print(f"  {i}. {name} ({hardware}) - {device_id}")
            else:
                print("✗ No devices found (may indicate auth issue)")

    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("✓ Authentication test completed")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
