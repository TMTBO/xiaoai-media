#!/usr/bin/env python3
"""Test script for play_url functionality"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config

async def test_play_url():
    """Test playing a URL directly"""
    print(f"Testing play_url with device: {config.MI_DID}")
    
    # Test URL (a sample audio file)
    test_url = "http://music.163.com/song/media/outer/url?id=1901371647.mp3"
    
    try:
        async with XiaoAiClient() as client:
            print(f"Playing URL: {test_url}")
            result = await client.play_url(test_url, config.MI_DID)
            print(f"Result: {result}")
            return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_play_url())
    if result:
        print("\n✓ Test passed!")
    else:
        print("\n✗ Test failed!")
        sys.exit(1)
