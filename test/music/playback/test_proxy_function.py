#!/usr/bin/env python3
"""测试代理URL函数"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from xiaoai_media.api.routes.music import _make_proxy_url
from xiaoai_media import config


def test_make_proxy_url():
    """测试_make_proxy_url函数"""
    print("=" * 60)
    print("测试代理URL函数")
    print("=" * 60)
    
    print(f"\n配置的音乐API地址: {config.MUSIC_API_BASE_URL}")
    
    # 测试用例
    test_cases = [
        "https://music.qq.com/song.mp3",
        "https://music.163.com/song/media/outer/url?id=123456.mp3",
        "http://example.com/music/test.flac",
        "https://isure.stream.qqmusic.qq.com/C400003mAan70zUy5O.m4a?guid=test&vkey=test",
    ]
    
    print("\n测试用例：")
    for i, original_url in enumerate(test_cases, 1):
        print(f"\n{i}. 原始URL:")
        print(f"   {original_url}")
        
        proxy_url = _make_proxy_url(original_url)
        print(f"   代理URL:")
        print(f"   {proxy_url}")
        
        # 验证代理URL格式
        assert proxy_url.startswith(config.MUSIC_API_BASE_URL), "代理URL应该以配置的基础URL开头"
        assert "/main/proxy?url=" in proxy_url, "代理URL应该包含/main/proxy?url="
        assert original_url not in proxy_url, "原始URL应该被URL编码"
        print(f"   ✅ 格式正确")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    test_make_proxy_url()
