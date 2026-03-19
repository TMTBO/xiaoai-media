#!/usr/bin/env python3
"""
TTS功能测试脚本 (TTS Function Test Script)

测试text_to_speech方法是否能通过miot_action正常调用。
Tests if text_to_speech method works correctly via miot_action.

使用方法 (Usage):
    python3 test/test_tts.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_tts():
    """Test TTS functionality with multiple test cases."""
    print("=" * 60)
    print("TTS功能测试 (TTS Function Test)")
    print("=" * 60)
    
    async with XiaoAiClient() as client:
        # List devices
        print("\n1. 获取设备列表 (Getting device list)...")
        devices = await client.list_devices()
        
        if not devices:
            print("❌ 未找到设备 (No devices found)!")
            return False
        
        print(f"✓ 找到 {len(devices)} 个设备 (Found {len(devices)} device(s))")
        
        # Show device info
        for i, device in enumerate(devices, 1):
            print(f"\n设备 {i} (Device {i}):")
            print(f"  名称 (Name): {device.get('name')}")
            print(f"  ID: {device.get('deviceID')}")
            print(f"  硬件 (Hardware): {device.get('hardware')}")
            print(f"  型号 (Model): {device.get('model')}")
            print(f"  MiotDID: {device.get('miotDID')}")
            print(f"  在线 (Online): {device.get('isOnline')}")
        
        # Test on first device
        device_id = devices[0]["deviceID"]
        device_name = devices[0].get("name", "Unknown")
        hardware = devices[0].get("hardware")
        
        print(f"\n2. 测试TTS播报功能 (Testing TTS broadcast on: {device_name})...")
        print(f"   Device ID: {device_id}")
        print(f"   Hardware: {hardware}")
        
        # TTS broadcast test cases (播报)
        tts_cases = [
            ("你好", "Simple greeting"),
            ("测试成功", "Test success message"),
        ]
        
        all_passed = True
        for i, (text, description) in enumerate(tts_cases, 1):
            print(f"\nTTS测试 {i} (TTS Test {i}): {description}")
            print(f"   文本 (Text): {text}")
            
            try:
                result = await client.text_to_speech(text, device_id)
                method = result.get("method")
                status = result.get("result")
                
                # Check success
                if method == "miot_action" and status == 0:
                    print(f"   ✓ 成功 (Success) - via miot_action (TTS broadcast)")
                elif method == "mina_service" and status is True:
                    print(f"   ✓ 成功 (Success) - via MiNAService (fallback)")
                else:
                    print(f"   ❌ 失败 (Failed): {result}")
                    all_passed = False
                
                await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"   ❌ 异常 (Exception): {e}")
                all_passed = False
        
        print(f"\n3. 测试命令执行功能 (Testing command execution on: {device_name})...")
        
        # Command execution test cases (执行文本)
        command_cases = [
            ("现在几点了", "Time query with response", False),
            ("查询天气", "Weather query with response", False),
            ("关灯", "Silent command (no response)", True),
        ]
        
        for i, (text, description, silent) in enumerate(command_cases, 1):
            print(f"\n命令测试 {i} (Command Test {i}): {description}")
            print(f"   文本 (Text): {text}")
            print(f"   静默模式 (Silent): {silent}")
            
            try:
                result = await client.send_command(text, device_id, silent)
                method = result.get("method")
                status = result.get("result")
                
                # Check success
                if method == "miot_action_execute" and status == 0:
                    mode = "静默" if silent else "语音回应"
                    print(f"   ✓ 成功 (Success) - via miot_action execute ({mode})")
                elif method == "miot_action" and status == 0:
                    print(f"   ✓ 成功 (Success) - via miot_action (TTS fallback)")
                elif method == "mina_service" and status is True:
                    print(f"   ✓ 成功 (Success) - via MiNAService (fallback)")
                else:
                    print(f"   ❌ 失败 (Failed): {result}")
                    all_passed = False
                
                await asyncio.sleep(3)
                    
            except Exception as e:
                print(f"   ❌ 异常 (Exception): {e}")
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✓ 所有测试通过 (All tests passed)!")
        else:
            print("❌ 部分测试失败 (Some tests failed)!")
        print("=" * 60)
        
        return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(test_tts())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试中断 (Test interrupted)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试失败 (Test failed): {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
