"""播放控制器测试

测试基于定时器的播放控制器功能。
"""

import asyncio
import pytest
from xiaoai_media.playback_controller import PlaybackController


@pytest.mark.asyncio
async def test_controller_start_stop():
    """测试控制器启动和停止"""
    controller = PlaybackController()
    
    # 启动控制器
    await controller.start()
    assert controller.running is True
    
    # 停止控制器
    await controller.stop()
    assert controller.running is False


@pytest.mark.asyncio
async def test_timer_callback():
    """测试定时器回调"""
    controller = PlaybackController(buffer_time=0.5)
    await controller.start()
    
    # 模拟播放开始，设置一个短时间的定时器
    device_id = "test_device"
    duration = 2000  # 2秒
    position = 0
    
    # 记录是否触发了下一曲
    triggered = []
    
    # 模拟 _play_next 方法
    async def mock_play_next(dev_id: str, playlist_id: str):
        triggered.append(dev_id)
    
    controller._play_next = mock_play_next
    
    # 设置播放状态（需要先设置播单ID）
    from xiaoai_media.services.state_service import get_state_service
    state_service = get_state_service()
    state_service.set(f"current_playlist_{device_id}", "test_playlist")
    
    # 开始播放
    await controller.on_play_started(device_id, duration, position)
    
    # 等待定时器触发（2秒 - 0.5秒缓冲 = 1.5秒）
    await asyncio.sleep(2.0)
    
    # 验证定时器触发了
    assert device_id in triggered
    
    await controller.stop()


@pytest.mark.asyncio
async def test_pause_resume():
    """测试暂停和继续播放"""
    controller = PlaybackController()
    await controller.start()
    
    device_id = "test_device"
    duration = 10000  # 10秒
    
    # 开始播放
    await controller.on_play_started(device_id, duration, 0)
    assert device_id in controller._timers
    
    # 暂停播放
    await controller.on_play_paused(device_id)
    assert device_id not in controller._timers
    
    await controller.stop()


@pytest.mark.asyncio
async def test_stop_playback():
    """测试停止播放"""
    controller = PlaybackController()
    await controller.start()
    
    device_id = "test_device"
    duration = 10000  # 10秒
    
    # 开始播放
    await controller.on_play_started(device_id, duration, 0)
    assert device_id in controller._timers
    
    # 停止播放
    await controller.on_play_stopped(device_id)
    assert device_id not in controller._timers
    assert device_id not in controller._device_status
    
    await controller.stop()


@pytest.mark.asyncio
async def test_status_callback():
    """测试状态变化回调"""
    controller = PlaybackController()
    await controller.start()
    
    # 记录回调触发
    callback_data = []
    
    async def test_callback(device_id: str, status: dict):
        callback_data.append((device_id, status))
    
    # 注册回调
    controller.add_status_callback(test_callback)
    
    # 触发播放
    device_id = "test_device"
    duration = 5000
    await controller.on_play_started(device_id, duration, 0)
    
    # 等待回调触发
    await asyncio.sleep(0.1)
    
    # 验证回调被触发
    assert len(callback_data) > 0
    assert callback_data[0][0] == device_id
    
    # 移除回调
    controller.remove_status_callback(test_callback)
    
    await controller.stop()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_controller_start_stop())
    asyncio.run(test_timer_callback())
    asyncio.run(test_pause_resume())
    asyncio.run(test_stop_playback())
    asyncio.run(test_status_callback())
    print("所有测试通过！")
