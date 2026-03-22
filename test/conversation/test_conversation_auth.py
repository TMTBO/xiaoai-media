#!/usr/bin/env python3
"""
Diagnostic script for conversation API authentication issues.
"""

import asyncio
import logging
import sys

# Setup logging to see all debug output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


async def test_conversation_api():
    """Test conversation API and diagnose authentication."""
    from xiaoai_media.client import XiaoAiClient

    print("\n=== Testing Conversation API Authentication ===\n")

    async with XiaoAiClient() as client:
        # Step 1: Check if we can get devices (this triggers login)
        print("Step 1: Fetching device list...")
        devices = await client.list_devices()

        if not devices:
            print("❌ No devices found. Check your credentials.")
            return False

        print(f"✓ Found {len(devices)} device(s)")
        for dev in devices:
            print(
                f"  - {dev.get('name', 'Unknown')} ({dev.get('hardware', 'Unknown')})"
            )

        # Step 2: Check token state
        print("\nStep 2: Checking authentication token...")
        if client._account and client._account.token:
            token_data = client._account.token
            print("Token fields present:")
            for key in token_data.keys():
                if key in ("serviceToken", "passToken"):
                    value = "***" if token_data[key] else "(empty)"
                else:
                    value = str(token_data[key])[:50]
                print(f"  - {key}: {value}")
        else:
            print("❌ No token data available")
            return False

        # Step 3: Try to get conversation
        print("\nStep 3: Fetching conversation history...")
        device_id = devices[0]["deviceID"]
        print(f"Using device: {devices[0].get('name', 'Unknown')} (ID: {device_id})")

        conversations = await client.get_latest_ask(device_id=device_id, limit=2)

        if conversations:
            print(f"✓ Successfully retrieved {len(conversations)} conversation(s):")
            for conv in conversations:
                print(f"\n  Query: {conv.get('query', 'N/A')}")
                print(f"  Answer: {conv.get('answer', 'N/A')}")
                print(f"  Time: {conv.get('time', 'N/A')}")
            return True
        else:
            print("❌ Failed to retrieve conversations (check logs above for details)")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_conversation_api())
    sys.exit(0 if result else 1)
