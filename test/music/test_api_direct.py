#!/usr/bin/env python3
"""
直接测试音乐 API 接口
"""

import asyncio
import aiohttp
import json
import time


async def test_api_endpoint():
    """测试 /api/v3/play 接口"""
    
    url = "http://192.168.1.111:5050/api/v3/play"
    
    # 测试不同音质
    test_cases = [
        {
            "name": "128k MP3",
            "payload": {
                "songId": "004GEXe13HYtsE",
                "platform": "tx",
                "quality": "128k",
                "format": "mp3",
                "name": "雨过后的风景",
                "singer": "Dizzy Dizzo (蔡诗芸)",
                "interval": "04:03",
                "size": "3.7MB",
                "albumName": "黑色彩虹",
                "picUrl": "https://y.gtimg.cn/music/photo_new/T002R500x500M0000038xSkp1EcVBf.jpg",
                "song_platform_id": "004GEXe13HYtsE",
            }
        },
        {
            "name": "320k MP3",
            "payload": {
                "songId": "004GEXe13HYtsE",
                "platform": "tx",
                "quality": "320k",
                "format": "mp3",
                "name": "雨过后的风景",
                "singer": "Dizzy Dizzo (蔡诗芸)",
                "interval": "04:03",
                "size": "9.3MB",
                "albumName": "黑色彩虹",
                "picUrl": "https://y.gtimg.cn/music/photo_new/T002R500x500M0000038xSkp1EcVBf.jpg",
                "song_platform_id": "004GEXe13HYtsE",
            }
        },
        {
            "name": "FLAC",
            "payload": {
                "songId": "004GEXe13HYtsE",
                "platform": "tx",
                "quality": "flac",
                "format": "flac",
                "name": "雨过后的风景",
                "singer": "Dizzy Dizzo (蔡诗芸)",
                "interval": "04:03",
                "size": "26.0MB",
                "albumName": "黑色彩虹",
                "picUrl": "https://y.gtimg.cn/music/photo_new/T002R500x500M0000038xSkp1EcVBf.jpg",
                "song_platform_id": "004GEXe13HYtsE",
            }
        },
        {
            "name": "Master FLAC",
            "payload": {
                "songId": "004GEXe13HYtsE",
                "platform": "tx",
                "quality": "master",
                "format": "flac",
                "name": "雨过后的风景",
                "singer": "Dizzy Dizzo (蔡诗芸)",
                "interval": "04:03",
                "size": "155.1MB",
                "albumName": "黑色彩虹",
                "picUrl": "https://y.gtimg.cn/music/photo_new/T002R500x500M0000038xSkp1EcVBf.jpg",
                "song_platform_id": "004GEXe13HYtsE",
            }
        },
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print("=" * 70)
            print(f"测试: {test_case['name']}")
            print("=" * 70)
            print(f"请求 URL: {url}")
            print(f"请求参数: {json.dumps(test_case['payload'], ensure_ascii=False, indent=2)}")
            print()
            
            start_time = time.time()
            
            try:
                async with session.post(
                    url,
                    json=test_case['payload'],
                    timeout=aiohttp.ClientTimeout(total=60),  # 60秒超时
                ) as response:
                    elapsed = time.time() - start_time
                    
                    print(f"响应状态码: {response.status}")
                    print(f"响应时间: {elapsed:.2f} 秒")
                    print()
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"响应数据:")
                        print(json.dumps(data, ensure_ascii=False, indent=2))
                        
                        # 检查是否成功获取到 URL
                        if data.get("code") == 0:
                            music_url = data.get("data", {}).get("url")
                            if music_url:
                                print()
                                print(f"✅ 成功获取音乐 URL")
                                print(f"URL 长度: {len(music_url)} 字符")
                                print(f"URL 前缀: {music_url[:100]}...")
                            else:
                                print()
                                print(f"❌ 响应成功但没有 URL")
                        else:
                            print()
                            print(f"❌ API 返回错误码: {data.get('code')}")
                            print(f"错误信息: {data.get('message', 'N/A')}")
                    else:
                        response_text = await response.text()
                        print(f"响应内容: {response_text[:500]}")
                        print()
                        print(f"❌ HTTP 请求失败")
                        
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                print(f"❌ 请求超时 (耗时 {elapsed:.2f} 秒)")
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ 请求失败 (耗时 {elapsed:.2f} 秒)")
                print(f"错误: {e}")
                import traceback
                traceback.print_exc()
            
            print()
            print()


if __name__ == "__main__":
    asyncio.run(test_api_endpoint())
