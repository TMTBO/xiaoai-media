#!/usr/bin/env python3
"""测试对话拦截播放功能"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src'))

from xiaoai_media.command_handler import CommandHandler
from xiaoai_media.client import XiaoAiClient


async def test_play_interception():
    """测试播放指令拦截"""
    print("=" * 60)
    print("测试对话拦截播放功能")
    print("=" * 60)
    
    # Get device
    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        if not devices:
            print("错误: 没有找到设备")
            return
        
        device = devices[0]
        device_id = device["deviceID"]
        device_name = device.get("name", "")
        hardware = device.get("hardware", "")
        
        print(f"\n设备信息:")
        print(f"  名称: {device_name}")
        print(f"  ID: {device_id}")
        print(f"  硬件: {hardware}")
        print()
    
    # Test play command
    handler = CommandHandler()
    
    test_queries = [
        "播放周杰伦的稻香",
        "播放晴天",
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"测试指令: {query}")
        print(f"{'=' * 60}")
        
        try:
            await handler.handle_command(device_id, query)
            print(f"\n✓ 指令处理完成")
            
            # Wait a bit to see if music plays
            print("\n等待 10 秒观察播放效果...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            import traceback
            traceback.print_exc()
        
        # Ask user to confirm
        print("\n" + "=" * 60)
        response = input("音乐是否正常播放？(y/n，或按 Ctrl+C 退出): ")
        if response.lower() != 'y':
            print("播放异常，请检查日志")
            break
        else:
            print("播放正常，继续测试下一个")


if __name__ == "__main__":
    try:
        asyncio.run(test_play_interception())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
