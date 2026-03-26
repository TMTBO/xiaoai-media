"""测试定时执行指令功能"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from xiaoai_media.services.scheduler_service import SchedulerService, TaskType
from xiaoai_media.scheduler_executor import SchedulerExecutor


@pytest.fixture
def scheduler():
    """创建测试用的 scheduler 实例"""
    service = SchedulerService()
    return service


@pytest.fixture
def executor():
    """创建测试用的 executor 实例"""
    return SchedulerExecutor()


@pytest.mark.asyncio
async def test_execute_command_with_device_id(executor):
    """测试执行指令（指定设备ID）"""
    # Mock CommandHandler
    executor.command_handler.handle_command = AsyncMock()
    
    task_id = "test_task_1"
    params = {
        "command": "播放周杰伦的歌",
        "device_id": "test_device_123"
    }
    
    await executor.execute_command(task_id, params)
    
    # 验证调用
    executor.command_handler.handle_command.assert_called_once_with(
        "test_device_123",
        "播放周杰伦的歌"
    )


@pytest.mark.asyncio
async def test_execute_command_without_device_id(executor):
    """测试执行指令（使用默认设备）"""
    # Mock CommandHandler 和 get_client
    executor.command_handler.handle_command = AsyncMock()
    
    with patch('xiaoai_media.scheduler_executor.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.device_id = "default_device"
        mock_get_client.return_value = mock_client
        
        task_id = "test_task_2"
        params = {
            "command": "播放轻音乐"
        }
        
        await executor.execute_command(task_id, params)
        
        # 验证调用
        executor.command_handler.handle_command.assert_called_once_with(
            "default_device",
            "播放轻音乐"
        )


@pytest.mark.asyncio
async def test_execute_command_missing_command(executor):
    """测试执行指令（缺少指令参数）"""
    executor.command_handler.handle_command = AsyncMock()
    
    task_id = "test_task_3"
    params = {}  # 缺少 command 参数
    
    await executor.execute_command(task_id, params)
    
    # 不应该调用 handle_command
    executor.command_handler.handle_command.assert_not_called()


@pytest.mark.asyncio
async def test_add_cron_command_task(scheduler, executor):
    """测试添加定时指令任务"""
    # 注册回调
    test_callback = AsyncMock()
    scheduler.register_callback(TaskType.COMMAND, test_callback)
    
    # 启动 scheduler
    await scheduler.start()
    
    try:
        # 创建任务
        task_id = "cron_command_task"
        result = await scheduler.add_cron_task(
            task_id=task_id,
            task_type=TaskType.COMMAND,
            name="每天早上播放音乐",
            cron_expression="0 7 * * *",
            params={
                "command": "播放周杰伦的歌",
                "device_id": "test_device"
            },
            enabled=True
        )
        
        # 验证任务创建
        assert result["task_id"] == task_id
        assert result["task_type"] == "command"
        assert result["name"] == "每天早上播放音乐"
        assert result["cron_expression"] == "0 7 * * *"
        assert result["params"]["command"] == "播放周杰伦的歌"
        assert result["enabled"] is True
        
        # 验证任务已保存
        task = scheduler.get_task(task_id)
        assert task is not None
        assert task["task_type"] == "command"
        
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_add_date_command_task(scheduler):
    """测试添加一次性指令任务"""
    # 注册回调
    test_callback = AsyncMock()
    scheduler.register_callback(TaskType.COMMAND, test_callback)
    
    # 启动 scheduler
    await scheduler.start()
    
    try:
        # 创建任务（10分钟后执行）
        task_id = "date_command_task"
        run_date = datetime.now() + timedelta(minutes=10)
        
        result = await scheduler.add_date_task(
            task_id=task_id,
            task_type=TaskType.COMMAND,
            name="10分钟后播放音乐",
            run_date=run_date,
            params={
                "command": "播放轻音乐"
            },
            enabled=True
        )
        
        # 验证任务创建
        assert result["task_id"] == task_id
        assert result["task_type"] == "command"
        assert result["name"] == "10分钟后播放音乐"
        assert result["params"]["command"] == "播放轻音乐"
        assert result["enabled"] is True
        
        # 验证任务已保存
        task = scheduler.get_task(task_id)
        assert task is not None
        assert task["task_type"] == "command"
        
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_command_task_execution(scheduler):
    """测试指令任务执行"""
    # 创建一个标志来跟踪回调是否被调用
    callback_called = False
    callback_params = None
    
    async def test_callback(task_id: str, params: dict):
        nonlocal callback_called, callback_params
        callback_called = True
        callback_params = params
    
    # 注册回调
    scheduler.register_callback(TaskType.COMMAND, test_callback)
    
    # 启动 scheduler
    await scheduler.start()
    
    try:
        # 创建一个立即执行的任务
        task_id = "immediate_command_task"
        run_date = datetime.now() + timedelta(seconds=2)
        
        await scheduler.add_date_task(
            task_id=task_id,
            task_type=TaskType.COMMAND,
            name="立即执行指令",
            run_date=run_date,
            params={
                "command": "测试指令",
                "device_id": "test_device"
            },
            enabled=True
        )
        
        # 等待任务执行
        await asyncio.sleep(3)
        
        # 验证回调被调用
        assert callback_called is True
        assert callback_params is not None
        assert callback_params["command"] == "测试指令"
        assert callback_params["device_id"] == "test_device"
        
    finally:
        await scheduler.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
