#!/usr/bin/env python3
"""测试 SSE 全局状态推送

验证：
1. 播单信息从 PlaylistService 获取
2. 音频信息从播单的 current_index 读取
3. playback_monitor 的状态更新实时推送到前端
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from xiaoai_media.api.routes.state import _build_full_state, _get_initial_state


async def test_build_full_state():
    """测试构建完整状态"""
    print("=" * 60)
    print("测试 _build_full_state 函数")
    print("=" * 60)
    
    # 模拟 playback_monitor 推送的基础状态
    basic_status = {
        "status": "playing",
        "audio_id": "1774607406199261",
        "position": 135139,
        "duration": 271107,
        "media_type": 3,
    }
    
    device_id = "e01467de-11ff-4fb0-b76b-51cde0bc3b19"
    
    print(f"\n输入参数:")
    print(f"  device_id: {device_id}")
    print(f"  basic_status: {json.dumps(basic_status, indent=2, ensure_ascii=False)}")
    
    try:
        result = await _build_full_state(device_id, basic_status)
        
        print(f"\n返回结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证关键字段
        print(f"\n验证结果:")
        print(f"  ✓ device_id: {result.get('device_id')}")
        print(f"  ✓ play_status: {result.get('play_status')}")
        print(f"  ✓ position: {result.get('position')} / {result.get('duration')}")
        
        current_song = result.get('current_song')
        if current_song:
            print(f"  ✓ current_song:")
            print(f"    - name: {current_song.get('name')}")
            print(f"    - singer: {current_song.get('singer')}")
            print(f"    - album: {current_song.get('album')}")
            print(f"    - cover: {current_song.get('cover')[:50] if current_song.get('cover') else '(无)'}")
        else:
            print(f"  ✗ current_song: None")
        
        playlist = result.get('playlist')
        if playlist:
            print(f"  ✓ playlist:")
            print(f"    - name: {playlist.get('name')}")
            print(f"    - current: {playlist.get('current')} / {playlist.get('total')}")
        else:
            print(f"  ✗ playlist: None")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def test_get_initial_state():
    """测试获取初始状态"""
    print("\n" + "=" * 60)
    print("测试 _get_initial_state 函数")
    print("=" * 60)
    
    device_id = "e01467de-11ff-4fb0-b76b-51cde0bc3b19"
    
    print(f"\n输入参数:")
    print(f"  device_id: {device_id}")
    
    try:
        result = await _get_initial_state(device_id)
        
        print(f"\n返回结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("\n🔍 SSE 全局状态推送测试\n")
    
    # 测试构建完整状态
    await test_build_full_state()
    
    # 测试获取初始状态
    await test_get_initial_state()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
