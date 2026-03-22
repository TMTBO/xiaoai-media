#!/usr/bin/env python3
"""
测试 music_provider.py 中的 get_music_url 函数
"""

import asyncio
from music_provider import get_music_url


async def test_get_music_url():
    """测试获取音乐 URL"""
    
    # 测试参数 - 使用你日志中的歌曲信息
    test_params = {
        'title': '雨过后的风景',
        'artist': 'Dizzy Dizzo (蔡诗芸)',
        'album': '黑色彩虹',
        'audio_id': '004GEXe13HYtsE',
        'interval': '04:03',
        'pic_url': 'https://y.gtimg.cn/music/photo_new/T002R500x500M0000038xSkp1EcVBf.jpg',
        'type': 'music',
        'platform': 'tx',
        'song_id': '004GEXe13HYtsE',
        'qualities': [
            {'type': '128k', 'format': 'mp3', 'size': '3.7MB'},
            {'type': '320k', 'format': 'mp3', 'size': '9.3MB'},
            {'type': 'flac', 'format': 'flac', 'size': '26.0MB'},
            {'type': 'master', 'format': 'flac', 'size': '155.1MB'},
            {'type': 'atmos', 'format': 'flac', 'size': '25.8MB'},
            {'type': 'atmos_plus', 'format': 'flac', 'size': '66.0MB'}
        ]
    }
    
    music_api_base_url = "http://192.168.1.111:5050"
    
    print("=" * 60)
    print("开始测试 get_music_url 函数")
    print("=" * 60)
    print(f"歌曲: {test_params['artist']} - {test_params['title']}")
    print(f"音乐 API: {music_api_base_url}")
    print("=" * 60)
    print()
    
    try:
        # 调用函数
        url = await get_music_url(test_params, music_api_base_url)
        
        print()
        print("=" * 60)
        print("✅ 测试成功！")
        print("=" * 60)
        print(f"获取到的代理 URL: {url}")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 测试失败！")
        print("=" * 60)
        print(f"错误信息: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


async def test_simple_song():
    """测试一首简单的歌曲（只有基础音质）"""
    
    test_params = {
        'title': '测试歌曲',
        'artist': '测试歌手',
        'album': '测试专辑',
        'audio_id': '004GEXe13HYtsE',  # 使用相同的 ID
        'interval': '04:03',
        'pic_url': '',
        'type': 'music',
        'platform': 'tx',
        'song_id': '004GEXe13HYtsE',
        'qualities': [
            {'type': '128k', 'format': 'mp3', 'size': '3.7MB'},
            {'type': '320k', 'format': 'mp3', 'size': '9.3MB'},
        ]
    }
    
    music_api_base_url = "http://192.168.1.111:5050"
    
    print("\n\n")
    print("=" * 60)
    print("测试简单歌曲（只有 MP3 音质）")
    print("=" * 60)
    
    try:
        url = await get_music_url(test_params, music_api_base_url)
        print()
        print("✅ 测试成功！")
        print(f"URL: {url}")
    except Exception as e:
        print()
        print("❌ 测试失败！")
        print(f"错误: {e}")


async def test_no_qualities():
    """测试没有音质列表的情况（使用默认音质）"""
    
    test_params = {
        'title': '测试歌曲',
        'artist': '测试歌手',
        'album': '测试专辑',
        'audio_id': '004GEXe13HYtsE',
        'interval': '04:03',
        'pic_url': '',
        'type': 'music',
        'platform': 'tx',
        'song_id': '004GEXe13HYtsE',
        # 没有 qualities 字段
    }
    
    music_api_base_url = "http://192.168.1.111:5050"
    
    print("\n\n")
    print("=" * 60)
    print("测试没有音质列表（使用默认 128k）")
    print("=" * 60)
    
    try:
        url = await get_music_url(test_params, music_api_base_url)
        print()
        print("✅ 测试成功！")
        print(f"URL: {url}")
    except Exception as e:
        print()
        print("❌ 测试失败！")
        print(f"错误: {e}")


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_get_music_url())
    asyncio.run(test_simple_song())
    asyncio.run(test_no_qualities())
