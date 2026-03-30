#!/usr/bin/env python3
"""验证配置热重载功能"""
import sys
sys.path.insert(0, "src")

from xiaoai_media import config

print("=" * 60)
print("验证配置热重载功能")
print("=" * 60)

# 测试1: 基本回调机制
print("\n测试1: 基本回调机制")
callback_called = []

def test_callback():
    callback_called.append(True)
    print("  ✓ 回调函数被调用")

config.register_config_change_callback(test_callback)
print("  已注册回调函数")

config.reload_config()
print("  已触发配置重载")

assert len(callback_called) == 1, "回调应该被调用一次"
print("  ✓ 测试通过")

# 测试2: 取消注册
print("\n测试2: 取消注册回调")
config.unregister_config_change_callback(test_callback)
print("  已取消注册回调函数")

config.reload_config()
print("  再次触发配置重载")

assert len(callback_called) == 1, "回调不应该再被调用"
print("  ✓ 测试通过")

# 测试3: 多个回调
print("\n测试3: 多个回调函数")
results = []

def callback1():
    results.append("callback1")
    print("  ✓ callback1 被调用")

def callback2():
    results.append("callback2")
    print("  ✓ callback2 被调用")

config.register_config_change_callback(callback1)
config.register_config_change_callback(callback2)
print("  已注册两个回调函数")

config.reload_config()
print("  已触发配置重载")

assert "callback1" in results, "callback1 应该被调用"
assert "callback2" in results, "callback2 应该被调用"
print("  ✓ 测试通过")

# 清理
config.unregister_config_change_callback(callback1)
config.unregister_config_change_callback(callback2)

# 测试4: 异常处理
print("\n测试4: 回调异常处理")
success_called = []

def failing_callback():
    print("  ✗ failing_callback 抛出异常")
    raise Exception("Test exception")

def success_callback():
    success_called.append(True)
    print("  ✓ success_callback 被调用")

config.register_config_change_callback(failing_callback)
config.register_config_change_callback(success_callback)
print("  已注册两个回调函数（一个会失败）")

config.reload_config()
print("  已触发配置重载")

assert len(success_called) == 1, "成功的回调应该被调用"
print("  ✓ 测试通过（异常被正确处理）")

# 清理
config.unregister_config_change_callback(failing_callback)
config.unregister_config_change_callback(success_callback)

print("\n" + "=" * 60)
print("所有测试通过！✓")
print("=" * 60)
