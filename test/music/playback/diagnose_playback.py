#!/usr/bin/env python3
"""诊断播放问题的脚本"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from xiaoai_media import config


def check_config():
    """检查配置是否正确"""
    print("=" * 60)
    print("配置检查")
    print("=" * 60)
    
    print(f"\n音乐API地址: {config.MUSIC_API_BASE_URL}")
    
    # 检查是否使用localhost
    if "localhost" in config.MUSIC_API_BASE_URL or "127.0.0.1" in config.MUSIC_API_BASE_URL:
        print("⚠️  警告: 使用了localhost地址")
        print("   音箱无法访问localhost，需要改为局域网IP")
        print("   例如: http://192.168.1.100:5050")
        return False
    else:
        print("✅ 使用了局域网IP地址")
        return True


async def test_music_api():
    """测试音乐API是否可访问"""
    print("\n" + "=" * 60)
    print("音乐API连接测试")
    print("=" * 60)
    
    import aiohttp
    
    try:
        url = f"{config.MUSIC_API_BASE_URL}/api/v3/search"
        print(f"\n测试URL: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params={"query": "测试", "platform": "tx", "limit": 1},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                data = await resp.json(content_type=None)
                print(f"响应状态: {resp.status}")
                print(f"响应代码: {data.get('code')}")
                
                if resp.status == 200 and data.get("code") == 0:
                    print("✅ 音乐API连接正常")
                    return True
                else:
                    print("❌ 音乐API返回错误")
                    return False
    except Exception as e:
        print(f"❌ 无法连接到音乐API: {e}")
        return False


async def test_proxy_endpoint():
    """测试代理端点是否可用"""
    print("\n" + "=" * 60)
    print("代理端点测试")
    print("=" * 60)
    
    import aiohttp
    from urllib.parse import quote
    
    try:
        # 测试一个简单的URL
        test_url = "https://www.baidu.com"
        proxy_url = f"{config.MUSIC_API_BASE_URL}/main/proxy?url={quote(test_url)}"
        print(f"\n测试代理URL: {proxy_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                proxy_url,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                print(f"响应状态: {resp.status}")
                
                if resp.status == 200:
                    print("✅ 代理端点工作正常")
                    return True
                else:
                    print(f"❌ 代理端点返回错误: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ 无法访问代理端点: {e}")
        print("   请确认music_download服务是否启动")
        print("   并且支持 /main/proxy?url= 接口")
        return False


async def main():
    """运行所有诊断"""
    print("\n🔍 开始诊断播放问题...\n")
    
    results = []
    
    # 1. 检查配置
    results.append(("配置检查", check_config()))
    
    # 2. 测试音乐API
    results.append(("音乐API", await test_music_api()))
    
    # 3. 测试代理端点
    results.append(("代理端点", await test_proxy_endpoint()))
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    all_passed = all(r[1] for r in results)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    if all_passed:
        print("\n🎉 所有检查通过！播放应该可以正常工作")
    else:
        print("\n⚠️  发现问题，请根据上述提示修复")
        print("\n常见解决方案：")
        print("1. 修改.env中的MUSIC_API_BASE_URL为局域网IP")
        print("2. 确保music_download服务正在运行")
        print("3. 确保music_download支持/main/proxy接口")


if __name__ == "__main__":
    asyncio.run(main())
