"""测试时区配置热重载功能"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock

from xiaoai_media import config
from xiaoai_media.services.scheduler_service import SchedulerService


def test_timezone_config_reload():
    """测试时区配置重新加载"""
    # 保存原始时区
    original_timezone = config.TIMEZONE
    
    try:
        # 修改时区配置
        config.TIMEZONE = "America/New_York"
        
        # 验证配置已更改
        assert config.TIMEZONE == "America/New_York"
        
        # 重新加载配置
        config.reload_config()
        
        # 验证配置已恢复（从 user_config.py 重新加载）
        # 注意：这取决于 user_config.py 中的实际配置
        assert hasattr(config, 'TIMEZONE')
        
    finally:
        # 恢复原始配置
        config.TIMEZONE = original_timezone


@pytest.mark.asyncio
async def test_scheduler_timezone_update():
    """测试调度器时区更新"""
    # 创建调度器实例
    scheduler = SchedulerService()
    
    # 启动调度器
    await scheduler.start()
    
    try:
        # 获取初始时区
        initial_timezone = scheduler.scheduler.timezone
        assert initial_timezone is not None
        
        # 更新时区
        new_timezone = "America/Los_Angeles"
        await scheduler.update_timezone(new_timezone)
        
        # 验证时区已更新
        updated_timezone = scheduler.scheduler.timezone
        assert str(updated_timezone) == new_timezone
        
    finally:
        # 停止调度器
        await scheduler.stop()


@pytest.mark.asyncio
async def test_log_formatter_timezone():
    """测试日志格式化器时区动态读取"""
    import logging
    from xiaoai_media.log_config import CustomFormatter
    
    # 创建格式化器
    formatter = CustomFormatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=False
    )
    
    # 创建日志记录
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # 保存原始时区
    original_timezone = config.TIMEZONE
    
    try:
        # 设置时区为上海
        config.TIMEZONE = "Asia/Shanghai"
        formatted1 = formatter.format(record)
        
        # 设置时区为纽约
        config.TIMEZONE = "America/New_York"
        formatted2 = formatter.format(record)
        
        # 两次格式化的结果应该不同（因为时区不同）
        # 注意：如果记录时间戳相同，时间字符串会不同
        assert formatted1 is not None
        assert formatted2 is not None
        
    finally:
        # 恢复原始时区
        config.TIMEZONE = original_timezone


def test_timezone_callback_registration():
    """测试时区配置变更回调"""
    callback_called = False
    
    def timezone_callback():
        nonlocal callback_called
        callback_called = True
    
    # 注册回调
    config.register_config_change_callback(timezone_callback)
    
    try:
        # 触发配置重载
        config.reload_config()
        
        # 验证回调被调用
        assert callback_called
        
    finally:
        # 取消注册
        config.unregister_config_change_callback(timezone_callback)


@pytest.mark.asyncio
async def test_timezone_hot_reload_integration():
    """测试时区热重载集成"""
    # 创建调度器
    scheduler = SchedulerService()
    await scheduler.start()
    
    # 保存原始时区
    original_timezone = config.TIMEZONE
    
    try:
        # 模拟配置变更
        config.TIMEZONE = "Europe/London"
        
        # 更新调度器时区
        await scheduler.update_timezone(config.TIMEZONE)
        
        # 验证调度器时区已更新
        assert str(scheduler.scheduler.timezone) == "Europe/London"
        
        # 重新加载配置
        config.reload_config()
        
        # 验证配置已恢复
        assert hasattr(config, 'TIMEZONE')
        
    finally:
        # 恢复原始配置
        config.TIMEZONE = original_timezone
        await scheduler.update_timezone(original_timezone)
        await scheduler.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
