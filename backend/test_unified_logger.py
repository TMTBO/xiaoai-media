#!/usr/bin/env python3
"""测试统一 logger 功能"""
import sys
sys.path.insert(0, "src")

from xiaoai_media.logger import get_logger, set_log_level, get_log_level

print("=" * 60)
print("测试统一 Logger")
print("=" * 60)

# 测试1: 获取 logger
print("\n测试1: 获取 logger")
logger = get_logger()
print(f"  Logger 名称: {logger.name}")
print(f"  当前级别: {get_log_level()}")

# 测试2: 基本日志输出
print("\n测试2: 基本日志输出 (INFO 级别)")
set_log_level("INFO")
logger.info("这是 INFO 日志")
logger.debug("这是 DEBUG 日志（不应该显示）")
logger.warning("这是 WARNING 日志")

# 测试3: 切换到 DEBUG 级别
print("\n测试3: 切换到 DEBUG 级别")
set_log_level("DEBUG")
print(f"  当前级别: {get_log_level()}")
logger.debug("现在可以看到 DEBUG 日志了")
logger.info("INFO 日志仍然可见")

# 测试4: 切换回 INFO 级别
print("\n测试4: 切换回 INFO 级别")
set_log_level("INFO")
print(f"  当前级别: {get_log_level()}")
logger.debug("DEBUG 日志又不显示了")
logger.info("只有 INFO 及以上级别可见")

# 测试5: 多次获取 logger（应该是同一个实例）
print("\n测试5: Logger 单例测试")
logger1 = get_logger()
logger2 = get_logger()
print(f"  logger1 is logger2: {logger1 is logger2}")
print(f"  ✓ 确认是同一个实例" if logger1 is logger2 else "  ✗ 不是同一个实例")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
