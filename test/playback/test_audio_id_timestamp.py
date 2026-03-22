#!/usr/bin/env python3
"""
测试基于时间戳的 audio_id 生成

测试场景：
1. 连续播放多首歌曲
2. 观察每次生成的 audio_id 是否唯一
3. 验证播放是否正常完成
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend" / "src"))

from xiaoai_media.client import XiaoAiClient


async def test_timestamp_audio_id():
    """测试时间戳生成的 audio_id"""
    
    print("=" * 60)
    print("测试基于时间戳的 audio_id 生成")
    print("=" * 60)
    
    # 测试用的音频 URL（使用公开的测试音频）
    test_urls = [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    ]
    
    async with XiaoAiClient() as client:
        try:
            # 连接到小米服务
            await client.connect()
            print("✅ 已连接到小米服务\n")
            
            # 获取设备列表
            devices = await client.list_devices()
            if not devices:
                print("❌ 未找到设备")
                return
            
            device = devices[0]
            device_id = device["deviceID"]
            device_name = device.get("name", "Unknown")
            print(f"📱 使用设备: {device_name} ({device_id})\n")
            
            # 连续播放测试
            audio_ids = []
            for i, url in enumerate(test_urls, 1):
                print(f"\n--- 测试 {i}/{len(test_urls)} ---")
                print(f"URL: {url}")
                
                try:
                    # 播放音频
                    result = await client.play_url(url, device_id)
                    
                    # 记录 audio_id
                    audio_id = result.get("audio_id", "N/A")
                    audio_ids.append(audio_id)
                    
                    print(f"audio_id: {audio_id}")
                    print(f"播放结果: {'✅ 成功' if result.get('result') else '❌ 失败'}")
                    print(f"原始结果: {result.get('raw_result')}")
                    
                    # 等待一小段时间再播放下一首
                    if i < len(test_urls):
                        print("等待 2 秒...")
                        await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"❌ 播放失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 验证 audio_id 唯一性
            print("\n" + "=" * 60)
            print("audio_id 唯一性检查")
            print("=" * 60)
            print(f"生成的 audio_id 列表:")
            for i, aid in enumerate(audio_ids, 1):
                print(f"  {i}. {aid}")
            
            unique_ids = set(audio_ids)
            print(f"\n总数: {len(audio_ids)}")
            print(f"唯一数: {len(unique_ids)}")
            
            if len(unique_ids) == len(audio_ids):
                print("✅ 所有 audio_id 都是唯一的")
            else:
                print("⚠️  存在重复的 audio_id")
                
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()


async def test_audio_id_generation():
    """测试 audio_id 生成逻辑"""
    import time
    
    print("\n" + "=" * 60)
    print("测试 audio_id 生成逻辑")
    print("=" * 60)
    
    # 生成多个 audio_id
    ids = []
    for i in range(5):
        audio_id = str(int(time.time() * 1000000))
        ids.append(audio_id)
        print(f"{i+1}. {audio_id}")
        await asyncio.sleep(0.001)  # 等待 1 毫秒
    
    # 检查唯一性
    unique_ids = set(ids)
    print(f"\n生成 {len(ids)} 个 ID，其中 {len(unique_ids)} 个唯一")
    
    if len(unique_ids) == len(ids):
        print("✅ 生成逻辑正常，所有 ID 都是唯一的")
    else:
        print("⚠️  生成逻辑可能有问题，存在重复 ID")


async def main():
    """主函数"""
    print("\n🎵 audio_id 时间戳生成测试\n")
    
    # 先测试生成逻辑
    await test_audio_id_generation()
    
    # 询问是否进行实际播放测试
    print("\n" + "=" * 60)
    response = input("\n是否进行实际播放测试？(y/n): ").strip().lower()
    
    if response == 'y':
        await test_timestamp_audio_id()
    else:
        print("跳过实际播放测试")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
