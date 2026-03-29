"""
测试播放列表管理功能

这个脚本测试从不同来源加载播放列表的功能：
1. 从搜索结果加载
2. 从排行榜加载
3. 从保存的播单加载
"""

import asyncio
import logging

import aiohttp

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

# 配置
BASE_URL = "http://localhost:8000"
DEVICE_ID = None  # 设置为你的设备 ID，或使用 None 让系统自动选择


async def test_load_from_search():
    """测试从搜索结果加载播放列表"""
    _log.info("=" * 60)
    _log.info("测试 1: 从搜索结果加载播放列表")
    _log.info("=" * 60)

    url = f"{BASE_URL}/api/music/load-from-search"
    payload = {
        "query": "周杰伦",
        "device_id": DEVICE_ID,
        "platform": "tx",
        "auto_play": False,  # 不自动播放，只加载
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            _log.info("响应状态: %d", resp.status)
            _log.info("响应内容: %s", result)

            if resp.status == 200:
                _log.info("✓ 成功加载 %d 首歌曲", result.get("total", 0))
                _log.info("预览:")
                for i, song in enumerate(result.get("songs", [])[:5], 1):
                    _log.info("  %d. %s - %s", i, song.get("singer"), song.get("name"))
                return True
            else:
                _log.error("✗ 加载失败")
                return False


async def test_load_from_chart():
    """测试从排行榜加载播放列表"""
    _log.info("=" * 60)
    _log.info("测试 2: 从排行榜加载播放列表")
    _log.info("=" * 60)

    url = f"{BASE_URL}/api/music/load-from-chart"
    payload = {
        "chart_keyword": "热歌榜",
        "device_id": DEVICE_ID,
        "platform": "tx",
        "auto_play": False,  # 不自动播放，只加载
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            _log.info("响应状态: %d", resp.status)
            _log.info("响应内容: %s", result)

            if resp.status == 200:
                _log.info("✓ 成功加载排行榜: %s", result.get("chart_name"))
                _log.info("总共 %d 首歌曲", result.get("total", 0))
                _log.info("预览:")
                for i, song in enumerate(result.get("songs", [])[:5], 1):
                    _log.info("  %d. %s - %s", i, song.get("singer"), song.get("name"))
                return True
            else:
                _log.error("✗ 加载失败")
                return False


async def test_voice_command_playlist():
    """测试语音命令 - 播单"""
    _log.info("=" * 60)
    _log.info("测试 3: 语音命令 - 播单")
    _log.info("=" * 60)

    url = f"{BASE_URL}/api/music/voice-command"
    payload = {
        "text": "播放音乐播单",
        "device_id": DEVICE_ID,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            _log.info("响应状态: %d", resp.status)
            _log.info("响应内容: %s", result)

            if resp.status == 200:
                action = result.get("action")
                _log.info("✓ 命令处理成功，动作: %s", action)
                return True
            elif resp.status == 404:
                _log.warning("⚠ 没有找到匹配的播单（这是正常的，如果你还没创建播单）")
                return True
            else:
                _log.error("✗ 命令处理失败")
                return False


async def test_voice_command_chart():
    """测试语音命令 - 排行榜"""
    _log.info("=" * 60)
    _log.info("测试 4: 语音命令 - 排行榜")
    _log.info("=" * 60)

    url = f"{BASE_URL}/api/music/voice-command"
    payload = {
        "text": "播放腾讯热歌榜",
        "device_id": DEVICE_ID,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            _log.info("响应状态: %d", resp.status)
            _log.info("响应内容: %s", result)

            if resp.status == 200:
                action = result.get("action")
                chart_name = result.get("result", {}).get("chart_name")
                _log.info("✓ 命令处理成功，动作: %s", action)
                _log.info("  排行榜: %s", chart_name)
                return True
            else:
                _log.error("✗ 命令处理失败")
                return False


async def test_voice_command_search():
    """测试语音命令 - 搜索"""
    _log.info("=" * 60)
    _log.info("测试 5: 语音命令 - 搜索")
    _log.info("=" * 60)

    url = f"{BASE_URL}/api/music/voice-command"
    payload = {
        "text": "搜索周杰伦",
        "device_id": DEVICE_ID,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            _log.info("响应状态: %d", resp.status)
            _log.info("响应内容: %s", result)

            if resp.status == 200:
                action = result.get("action")
                query = result.get("query")
                total = result.get("result", {}).get("total", 0)
                _log.info("✓ 命令处理成功，动作: %s", action)
                _log.info("  搜索关键词: %s", query)
                _log.info("  找到歌曲: %d 首", total)
                return True
            else:
                _log.error("✗ 命令处理失败")
                return False


async def test_playback_control():
    """测试播放控制"""
    _log.info("=" * 60)
    _log.info("测试 6: 播放控制 (下一首/上一首)")
    _log.info("=" * 60)

    # 首先加载一个播放列表
    _log.info("先加载播放列表...")
    load_url = f"{BASE_URL}/api/music/load-from-search"
    payload = {
        "query": "周杰伦",
        "device_id": DEVICE_ID,
        "platform": "tx",
        "auto_play": False,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(load_url, json=payload) as resp:
            if resp.status != 200:
                _log.error("✗ 无法加载播放列表")
                return False

        # 测试播放索引 0
        _log.info("播放第一首...")
        play_url = f"{BASE_URL}/api/music/play"
        play_payload = {"index": 0, "device_id": DEVICE_ID}
        async with session.post(play_url, json=play_payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                current = result.get("current", {})
                _log.info(
                    "✓ 正在播放: %s - %s", current.get("singer"), current.get("name")
                )
            else:
                _log.error("✗ 播放失败")
                return False

        # 测试下一首
        await asyncio.sleep(1)
        _log.info("切换到下一首...")
        next_url = f"{BASE_URL}/api/music/next"
        next_payload = {"device_id": DEVICE_ID}
        async with session.post(next_url, json=next_payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                current = result.get("current", {})
                _log.info(
                    "✓ 正在播放: %s - %s", current.get("singer"), current.get("name")
                )
            else:
                _log.error("✗ 切换失败")
                return False

        # 测试上一首
        await asyncio.sleep(1)
        _log.info("切换到上一首...")
        prev_url = f"{BASE_URL}/api/music/prev"
        prev_payload = {"device_id": DEVICE_ID}
        async with session.post(prev_url, json=prev_payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                current = result.get("current", {})
                _log.info(
                    "✓ 正在播放: %s - %s", current.get("singer"), current.get("name")
                )
                return True
            else:
                _log.error("✗ 切换失败")
                return False


async def main():
    """运行所有测试"""
    _log.info("\n" + "=" * 60)
    _log.info("播放列表管理功能测试")
    _log.info("=" * 60 + "\n")

    tests = [
        ("从搜索结果加载", test_load_from_search),
        ("从排行榜加载", test_load_from_chart),
        ("语音命令-播单", test_voice_command_playlist),
        ("语音命令-排行榜", test_voice_command_chart),
        ("语音命令-搜索", test_voice_command_search),
        ("播放控制", test_playback_control),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            _log.error("测试 '%s' 出错: %s", name, e, exc_info=True)
            results.append((name, False))

        await asyncio.sleep(1)  # 测试之间等待1秒

    # 输出总结
    _log.info("\n" + "=" * 60)
    _log.info("测试总结")
    _log.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        _log.info("%s: %s", name, status)

    _log.info("\n总计: %d/%d 测试通过", passed, total)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
