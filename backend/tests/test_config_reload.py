"""测试配置热重载功能"""
import pytest
from xiaoai_media import config


def test_config_reload_callback():
    """测试配置变更回调机制"""
    callback_called = []
    
    def test_callback():
        callback_called.append(True)
    
    # 注册回调
    config.register_config_change_callback(test_callback)
    
    # 触发配置重载
    config.reload_config()
    
    # 验证回调被调用
    assert len(callback_called) == 1
    
    # 取消注册
    config.unregister_config_change_callback(test_callback)
    
    # 再次触发，回调不应该被调用
    config.reload_config()
    assert len(callback_called) == 1


def test_multiple_callbacks():
    """测试多个回调函数"""
    results = []
    
    def callback1():
        results.append("callback1")
    
    def callback2():
        results.append("callback2")
    
    # 注册多个回调
    config.register_config_change_callback(callback1)
    config.register_config_change_callback(callback2)
    
    # 触发配置重载
    config.reload_config()
    
    # 验证所有回调都被调用
    assert "callback1" in results
    assert "callback2" in results
    
    # 清理
    config.unregister_config_change_callback(callback1)
    config.unregister_config_change_callback(callback2)


def test_callback_exception_handling():
    """测试回调函数异常处理"""
    success_called = []
    
    def failing_callback():
        raise Exception("Test exception")
    
    def success_callback():
        success_called.append(True)
    
    # 注册两个回调，一个会失败
    config.register_config_change_callback(failing_callback)
    config.register_config_change_callback(success_callback)
    
    # 触发配置重载，不应该因为一个回调失败而中断
    config.reload_config()
    
    # 验证成功的回调仍然被调用
    assert len(success_called) == 1
    
    # 清理
    config.unregister_config_change_callback(failing_callback)
    config.unregister_config_change_callback(success_callback)
