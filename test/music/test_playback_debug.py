#!/usr/bin/env python3
"""Debug script for testing playback with detailed logging."""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

from xiaoai_media.client import XiaoAiClient


async def test_playback_step_by_step():
    """Test playback with detailed step-by-step logging."""
    print("=" * 60)
    print("播放功能调试测试")
    print("=" * 60)
    
    async with XiaoAiClient() as client:
        # Step 1: List devices
        print("\n[步骤 1] 获取设备列表...")
        devices = await client.list_devices()
        if not devices:
            print("❌ 没有找到设备！")
            return
        
        device = devices[0]
        device_id = device["deviceID"]
        device_name = device.get("name", "Unknown")
        hardware = device.get("hardware", "Unknown")
        print(f"✓ 使用设备: {device_name}")
        print(f"  - Device ID: {device_id}")
        print(f"  - Hardware: {hardware}")
        
        # Step 2: Check current status
        print("\n[步骤 2] 检查当前播放状态...")
        try:
            status = await client.player_get_status(device_id)
            print(f"✓ 当前状态: {status}")
        except Exception as e:
            print(f"⚠ 无法获取状态: {e}")
        
        # Step 3: Stop any current playback
        print("\n[步骤 3] 停止当前播放...")
        try:
            stop_result = await client.player_stop(device_id)
            print(f"✓ 停止结果: {stop_result}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"⚠ 停止失败（可能没有在播放）: {e}")
        
        # Step 4: Test TTS (to verify device connectivity)
        print("\n[步骤 4] 测试 TTS（验证设备连接）...")
        try:
            tts_result = await client.text_to_speech("测试连接", device_id)
            print(f"✓ TTS 结果: {tts_result}")
            print("  如果听到'测试连接'，说明设备连接正常")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"❌ TTS 失败: {e}")
            return
        
        # Step 5: Set loop mode
        print("\n[步骤 5] 设置循环模式...")
        try:
            loop_result = await client.player_set_loop(device_id, loop_type=1)
            print(f"✓ 循环模式设置结果: {loop_result}")
        except Exception as e:
            print(f"⚠ 设置循环模式失败: {e}")
        
        # Step 6: Test play URL
        print("\n[步骤 6] 测试播放 URL...")
        test_urls = [
            "http://music.163.com/song/media/outer/url?id=447925558.mp3",  # 网易云测试
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n  测试 URL {i}: {url[:60]}...")
            try:
                play_result = await client.play_url(url, device_id, _type=1)
                print(f"  ✓ 播放结果: {play_result}")
                
                # Wait and check status
                print("  等待 3 秒后检查状态...")
                await asyncio.sleep(3)
                
                try:
                    status = await client.player_get_status(device_id)
                    print(f"  ✓ 播放状态: {status}")
                except Exception as e:
                    print(f"  ⚠ 无法获取状态: {e}")
                
                # Test pause
                print("  测试暂停...")
                try:
                    pause_result = await client.player_pause(device_id)
                    print(f"  ✓ 暂停结果: {pause_result}")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"  ⚠ 暂停失败: {e}")
                
                # Test resume
                print("  测试恢复...")
                try:
                    resume_result = await client.player_play(device_id)
                    print(f"  ✓ 恢复结果: {resume_result}")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"  ⚠ 恢复失败: {e}")
                
                # Stop
                print("  停止播放...")
                try:
                    stop_result = await client.player_stop(device_id)
                    print(f"  ✓ 停止结果: {stop_result}")
                except Exception as e:
                    print(f"  ⚠ 停止失败: {e}")
                
            except Exception as e:
                print(f"  ❌ 播放失败: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n如果音箱没有播放，请检查：")
        print("1. 音箱是否在线（小米音箱 App）")
        print("2. URL 是否可以直接访问")
        print("3. 音箱网络是否正常")
        print("4. 尝试使用语音命令播放看是否正常")


if __name__ == "__main__":
    asyncio.run(test_playback_step_by_step())
