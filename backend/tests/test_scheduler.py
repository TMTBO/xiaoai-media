"""定时任务服务测试"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import pytest

from xiaoai_media.services.scheduler_service import (
    SchedulerService,
    TaskType,
)


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
async def scheduler(temp_dir):
    """创建测试用的调度器实例"""
    service = SchedulerService(data_dir=temp_dir)
    await service.start()
    yield service
    await service.stop()


@pytest.mark.asyncio
async def test_create_cron_task(scheduler):
    """测试创建 Cron 定时任务"""
    task = await scheduler.add_cron_task(
        task_id="test-cron-1",
        task_type=TaskType.PLAY_MUSIC,
        name="每天早上7点播放音乐",
        cron_expression="0 7 * * *",
        params={"song_name": "晴天", "artist": "周杰伦"},
        enabled=True
    )
    
    assert task["task_id"] == "test-cron-1"
    assert task["task_type"] == "play_music"
    assert task["name"] == "每天早上7点播放音乐"
    assert task["cron_expression"] == "0 7 * * *"
    assert task["enabled"] is True


@pytest.mark.asyncio
async def test_create_date_task(scheduler):
    """测试创建一次性定时任务"""
    run_date = datetime.now() + timedelta(hours=1)
    
    task = await scheduler.add_date_task(
        task_id="test-date-1",
        task_type=TaskType.REMINDER,
        name="1小时后提醒",
        run_date=run_date,
        params={"message": "该休息了"},
        enabled=True
    )
    
    assert task["task_id"] == "test-date-1"
    assert task["task_type"] == "reminder"
    assert task["trigger_type"] == "date"
    assert task["enabled"] is True


@pytest.mark.asyncio
async def test_list_tasks(scheduler):
    """测试列出任务"""
    # 创建多个任务
    await scheduler.add_cron_task(
        task_id="task-1",
        task_type=TaskType.PLAY_MUSIC,
        name="任务1",
        cron_expression="0 7 * * *",
        params={}
    )
    
    await scheduler.add_cron_task(
        task_id="task-2",
        task_type=TaskType.PLAY_PLAYLIST,
        name="任务2",
        cron_expression="0 8 * * *",
        params={}
    )
    
    # 列出所有任务
    tasks = scheduler.list_tasks()
    assert len(tasks) == 2
    
    # 按类型过滤
    music_tasks = scheduler.list_tasks(task_type=TaskType.PLAY_MUSIC)
    assert len(music_tasks) == 1
    assert music_tasks[0]["task_type"] == "play_music"


@pytest.mark.asyncio
async def test_get_task(scheduler):
    """测试获取任务详情"""
    await scheduler.add_cron_task(
        task_id="task-get",
        task_type=TaskType.PLAY_MUSIC,
        name="测试任务",
        cron_expression="0 7 * * *",
        params={"song_name": "测试歌曲"}
    )
    
    task = scheduler.get_task("task-get")
    assert task is not None
    assert task["task_id"] == "task-get"
    assert task["name"] == "测试任务"
    
    # 获取不存在的任务
    task = scheduler.get_task("non-existent")
    assert task is None


@pytest.mark.asyncio
async def test_update_task(scheduler):
    """测试更新任务"""
    await scheduler.add_cron_task(
        task_id="task-update",
        task_type=TaskType.PLAY_MUSIC,
        name="原始名称",
        cron_expression="0 7 * * *",
        params={"song_name": "原始歌曲"}
    )
    
    # 更新任务
    updated = await scheduler.update_task(
        task_id="task-update",
        name="新名称",
        cron_expression="0 8 * * *",
        params={"song_name": "新歌曲"}
    )
    
    assert updated["name"] == "新名称"
    assert updated["cron_expression"] == "0 8 * * *"
    assert updated["params"]["song_name"] == "新歌曲"


@pytest.mark.asyncio
async def test_delete_task(scheduler):
    """测试删除任务"""
    await scheduler.add_cron_task(
        task_id="task-delete",
        task_type=TaskType.PLAY_MUSIC,
        name="待删除任务",
        cron_expression="0 7 * * *",
        params={}
    )
    
    # 确认任务存在
    task = scheduler.get_task("task-delete")
    assert task is not None
    
    # 删除任务
    await scheduler.delete_task("task-delete")
    
    # 确认任务已删除
    task = scheduler.get_task("task-delete")
    assert task is None


@pytest.mark.asyncio
async def test_task_persistence(temp_dir):
    """测试任务持久化"""
    # 创建调度器并添加任务
    scheduler1 = SchedulerService(data_dir=temp_dir)
    await scheduler1.start()
    
    await scheduler1.add_cron_task(
        task_id="persist-task",
        task_type=TaskType.PLAY_MUSIC,
        name="持久化任务",
        cron_expression="0 7 * * *",
        params={"song_name": "测试"}
    )
    
    await scheduler1.stop()
    
    # 创建新的调度器实例，应该能恢复任务
    scheduler2 = SchedulerService(data_dir=temp_dir)
    await scheduler2.start()
    
    task = scheduler2.get_task("persist-task")
    assert task is not None
    assert task["name"] == "持久化任务"
    
    await scheduler2.stop()


@pytest.mark.asyncio
async def test_expired_task_cleanup(temp_dir):
    """测试过期任务清理"""
    scheduler = SchedulerService(data_dir=temp_dir)
    await scheduler.start()
    
    # 手动创建一个过期的任务配置
    expired_task = {
        "task_id": "expired-task",
        "task_type": "reminder",
        "name": "过期任务",
        "trigger_type": "date",
        "run_date": (datetime.now() - timedelta(hours=1)).isoformat(),
        "params": {"message": "测试"},
        "enabled": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    scheduler._tasks_metadata["expired-task"] = expired_task
    scheduler._save_tasks()
    
    await scheduler.stop()
    
    # 重新启动，过期任务应该被清理
    scheduler2 = SchedulerService(data_dir=temp_dir)
    await scheduler2.start()
    
    task = scheduler2.get_task("expired-task")
    assert task is None
    
    await scheduler2.stop()


@pytest.mark.asyncio
async def test_task_callback_registration(scheduler):
    """测试任务回调注册"""
    executed_tasks = []
    
    async def test_callback(task_id: str, params: dict):
        executed_tasks.append(task_id)
    
    # 注册回调
    scheduler.register_callback(TaskType.PLAY_MUSIC, test_callback)
    
    # 创建任务并立即执行
    await scheduler.add_date_task(
        task_id="callback-test",
        task_type=TaskType.PLAY_MUSIC,
        name="回调测试",
        run_date=datetime.now() + timedelta(seconds=1),
        params={}
    )
    
    # 等待任务执行
    await asyncio.sleep(2)
    
    # 验证回调被调用
    assert "callback-test" in executed_tasks


@pytest.mark.asyncio
async def test_invalid_cron_expression(scheduler):
    """测试无效的 Cron 表达式"""
    with pytest.raises(ValueError):
        await scheduler.add_cron_task(
            task_id="invalid-cron",
            task_type=TaskType.PLAY_MUSIC,
            name="无效任务",
            cron_expression="invalid",  # 无效的表达式
            params={}
        )


@pytest.mark.asyncio
async def test_expired_date_task(scheduler):
    """测试创建已过期的一次性任务"""
    past_date = datetime.now() - timedelta(hours=1)
    
    with pytest.raises(ValueError):
        await scheduler.add_date_task(
            task_id="expired",
            task_type=TaskType.REMINDER,
            name="过期任务",
            run_date=past_date,
            params={}
        )


@pytest.mark.asyncio
async def test_disable_task(scheduler):
    """测试禁用任务"""
    # 创建启用的任务
    await scheduler.add_cron_task(
        task_id="disable-test",
        task_type=TaskType.PLAY_MUSIC,
        name="禁用测试",
        cron_expression="0 7 * * *",
        params={},
        enabled=True
    )
    
    # 禁用任务
    await scheduler.update_task(
        task_id="disable-test",
        enabled=False
    )
    
    task = scheduler.get_task("disable-test")
    assert task["enabled"] is False
    
    # 调度器中不应该有这个任务
    job = scheduler.scheduler.get_job("disable-test")
    assert job is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
