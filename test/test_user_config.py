#!/usr/bin/env python3
"""测试用户配置系统"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "backend" / "src"))

from xiaoai_media import config


def test_config_loading():
    """测试配置加载"""
    print("=" * 60)
    print("配置加载测试")
    print("=" * 60)
    
    print(f"\n小米账号配置:")
    print(f"  MI_USER: {config.MI_USER}")
    print(f"  MI_PASS: {'*' * len(config.MI_PASS) if config.MI_PASS else '(未设置)'}")
    print(f"  MI_DID: {config.MI_DID or '(未设置)'}")
    print(f"  MI_REGION: {config.MI_REGION}")
    
    print(f"\n音乐服务配置:")
    print(f"  MUSIC_API_BASE_URL: {config.MUSIC_API_BASE_URL}")
    print(f"  MUSIC_DEFAULT_PLATFORM: {config.MUSIC_DEFAULT_PLATFORM}")
    
    print(f"\n对话监听配置:")
    print(f"  ENABLE_CONVERSATION_POLLING: {config.ENABLE_CONVERSATION_POLLING}")
    print(f"  CONVERSATION_POLL_INTERVAL: {config.CONVERSATION_POLL_INTERVAL}")
    
    print(f"\n唤醒词配置:")
    print(f"  WAKE_WORDS: {config.WAKE_WORDS}")
    print(f"  ENABLE_WAKE_WORD_FILTER: {config.ENABLE_WAKE_WORD_FILTER}")


def test_wake_word_filter():
    """测试唤醒词过滤"""
    print("\n" + "=" * 60)
    print("唤醒词过滤测试")
    print("=" * 60)
    
    test_cases = [
        "小爱同学，播放周杰伦的晴天",
        "小爱，播放音乐",
        "播放周杰伦的晴天",  # 没有唤醒词
        "小爱同学，调大音量",
        "关灯",  # 没有唤醒词
    ]
    
    for query in test_cases:
        should_handle = config.should_handle_command(query)
        processed = config.preprocess_command(query) if should_handle else "(未处理)"
        
        print(f"\n原始指令: {query}")
        print(f"  是否处理: {should_handle}")
        print(f"  预处理后: {processed}")


def test_custom_functions():
    """测试自定义函数"""
    print("\n" + "=" * 60)
    print("自定义函数测试")
    print("=" * 60)
    
    # 检查是否有用户配置
    if config._user_config is None:
        print("\n未找到 user_config.py，使用默认逻辑")
    else:
        print("\n已加载 user_config.py")
        
        # 检查自定义函数
        has_custom_should_handle = hasattr(config._user_config, "should_handle_command")
        has_custom_preprocess = hasattr(config._user_config, "preprocess_command")
        
        print(f"  自定义 should_handle_command: {has_custom_should_handle}")
        print(f"  自定义 preprocess_command: {has_custom_preprocess}")


def main():
    """主函数"""
    try:
        test_config_loading()
        test_wake_word_filter()
        test_custom_functions()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
