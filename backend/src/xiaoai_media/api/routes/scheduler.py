"""定时任务管理 API 路由"""

from xiaoai_media.logger import get_logger
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from xiaoai_media.services.scheduler_service import (
    get_scheduler_service,
    SchedulerService,
    TaskType,
)

_log = get_logger()

router = APIRouter(tags=["scheduler"])


# ============================================
# 请求/响应模型
# ============================================


class CronTaskCreate(BaseModel):
    """创建 Cron 定时任务请求"""

    task_type: TaskType = Field(..., description="任务类型")
    name: str = Field(..., description="任务名称")
    cron_expression: str = Field(..., description="Cron 表达式 (分 时 日 月 周)")
    params: dict = Field(default_factory=dict, description="任务参数")
    enabled: bool = Field(default=True, description="是否启用")


class DateTaskCreate(BaseModel):
    """创建一次性定时任务请求"""

    task_type: TaskType = Field(..., description="任务类型")
    name: str = Field(..., description="任务名称")
    run_date: datetime = Field(..., description="执行时间")
    params: dict = Field(default_factory=dict, description="任务参数")
    enabled: bool = Field(default=True, description="是否启用")


class DelayTaskCreate(BaseModel):
    """创建延迟任务请求（如：10分钟后提醒）"""

    task_type: TaskType = Field(..., description="任务类型")
    name: str = Field(..., description="任务名称")
    delay_minutes: int = Field(..., description="延迟分钟数", gt=0)
    params: dict = Field(default_factory=dict, description="任务参数")


class TaskUpdate(BaseModel):
    """更新任务请求"""

    name: Optional[str] = Field(None, description="任务名称")
    cron_expression: Optional[str] = Field(None, description="Cron 表达式")
    run_date: Optional[datetime] = Field(None, description="执行时间")
    params: Optional[dict] = Field(None, description="任务参数")
    enabled: Optional[bool] = Field(None, description="是否启用")


class TaskResponse(BaseModel):
    """任务响应"""

    task_id: str
    task_type: str
    name: str
    trigger_type: str
    cron_expression: Optional[str] = None
    run_date: Optional[str] = None
    params: dict
    enabled: bool
    next_run_time: Optional[str] = None
    created_at: str
    updated_at: str


class QuickReminderCreate(BaseModel):
    """快速提醒请求"""

    message: str = Field(..., description="提醒内容")
    delay_minutes: int = Field(..., description="延迟分钟数", gt=0, le=1440)


class QuickPlayMusicCreate(BaseModel):
    """快速播放音乐请求"""

    song_name: str = Field(..., description="歌曲名称")
    artist: Optional[str] = Field(None, description="歌手名称")
    cron_expression: str = Field(..., description="Cron 表达式")


class QuickPlayPlaylistCreate(BaseModel):
    """快速播放播放列表请求"""

    playlist_id: str = Field(..., description="播放列表ID")
    cron_expression: str = Field(..., description="Cron 表达式")


class QuickCommandCreate(BaseModel):
    """快速执行指令请求"""

    command: str = Field(..., description="语音指令文本")
    cron_expression: Optional[str] = Field(None, description="Cron 表达式（定时执行）")
    delay_minutes: Optional[int] = Field(
        None, description="延迟分钟数（延迟执行）", gt=0, le=1440
    )
    device_id: Optional[str] = Field(None, description="设备ID（可选）")


# ============================================
# API 端点
# ============================================


def get_scheduler() -> SchedulerService:
    """获取调度服务依赖"""
    return get_scheduler_service()


@router.post("/scheduler/tasks/cron", response_model=TaskResponse)
async def create_cron_task(
    task: CronTaskCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """创建 Cron 定时任务

    Cron 表达式格式: 分 时 日 月 周
    - 分: 0-59
    - 时: 0-23
    - 日: 1-31
    - 月: 1-12
    - 周: 0-6 (0=周日)

    示例:
    - "0 7 * * *" - 每天早上7点
    - "30 20 * * 1-5" - 周一到周五晚上8点30分
    - "0 */2 * * *" - 每2小时
    """
    try:
        task_id = str(uuid.uuid4())
        result = await scheduler.add_cron_task(
            task_id=task_id,
            task_type=task.task_type,
            name=task.name,
            cron_expression=task.cron_expression,
            params=task.params,
            enabled=task.enabled,
        )
        return TaskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _log.error("创建 Cron 任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/scheduler/tasks/date", response_model=TaskResponse)
async def create_date_task(
    task: DateTaskCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """创建一次性定时任务"""
    try:
        task_id = str(uuid.uuid4())
        result = await scheduler.add_date_task(
            task_id=task_id,
            task_type=task.task_type,
            name=task.name,
            run_date=task.run_date,
            params=task.params,
            enabled=task.enabled,
        )
        return TaskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _log.error("创建一次性任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/scheduler/tasks/delay", response_model=TaskResponse)
async def create_delay_task(
    task: DelayTaskCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """创建延迟任务（如：10分钟后提醒我）"""
    try:
        task_id = str(uuid.uuid4())
        run_date = datetime.now() + timedelta(minutes=task.delay_minutes)
        result = await scheduler.add_date_task(
            task_id=task_id,
            task_type=task.task_type,
            name=task.name,
            run_date=run_date,
            params=task.params,
            enabled=True,
        )
        return TaskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _log.error("创建延迟任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/scheduler/tasks", response_model=list[TaskResponse])
async def list_tasks(
    task_type: Optional[TaskType] = None,
    scheduler: SchedulerService = Depends(get_scheduler),
):
    """列出所有任务"""
    try:
        tasks = scheduler.list_tasks(task_type=task_type)
        return [TaskResponse(**task) for task in tasks]
    except Exception as e:
        _log.error("列出任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出任务失败: {str(e)}")


@router.get("/scheduler/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, scheduler: SchedulerService = Depends(get_scheduler)):
    """获取任务详情"""
    task = scheduler.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse(**task)


@router.put("/scheduler/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    scheduler: SchedulerService = Depends(get_scheduler),
):
    """更新任务"""
    try:
        result = await scheduler.update_task(
            task_id=task_id,
            name=task_update.name,
            cron_expression=task_update.cron_expression,
            run_date=task_update.run_date,
            params=task_update.params,
            enabled=task_update.enabled,
        )
        return TaskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _log.error("更新任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新任务失败: {str(e)}")


@router.delete("/scheduler/tasks/{task_id}")
async def delete_task(
    task_id: str, scheduler: SchedulerService = Depends(get_scheduler)
):
    """删除任务"""
    try:
        await scheduler.delete_task(task_id)
        return {"message": "任务已删除", "task_id": task_id}
    except Exception as e:
        _log.error("删除任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


# ============================================
# 快捷操作 API
# ============================================


@router.post("/scheduler/quick/reminder", response_model=TaskResponse)
async def quick_reminder(
    reminder: QuickReminderCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """快速创建提醒（如：10分钟后提醒我）"""
    try:
        task_id = str(uuid.uuid4())
        run_date = datetime.now() + timedelta(minutes=reminder.delay_minutes)

        result = await scheduler.add_date_task(
            task_id=task_id,
            task_type=TaskType.REMINDER,
            name=f"提醒: {reminder.message}",
            run_date=run_date,
            params={"message": reminder.message},
            enabled=True,
        )
        return TaskResponse(**result)
    except Exception as e:
        _log.error("创建快速提醒失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建提醒失败: {str(e)}")


@router.post("/scheduler/quick/play-music", response_model=TaskResponse)
async def quick_play_music(
    play: QuickPlayMusicCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """快速创建定时播放音乐任务"""
    try:
        task_id = str(uuid.uuid4())

        params = {"song_name": play.song_name}
        if play.artist:
            params["artist"] = play.artist

        result = await scheduler.add_cron_task(
            task_id=task_id,
            task_type=TaskType.PLAY_MUSIC,
            name=f"播放: {play.song_name}",
            cron_expression=play.cron_expression,
            params=params,
            enabled=True,
        )
        return TaskResponse(**result)
    except Exception as e:
        _log.error("创建定时播放音乐任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/scheduler/quick/play-playlist", response_model=TaskResponse)
async def quick_play_playlist(
    play: QuickPlayPlaylistCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """快速创建定时播放播放列表任务"""
    try:
        task_id = str(uuid.uuid4())

        result = await scheduler.add_cron_task(
            task_id=task_id,
            task_type=TaskType.PLAY_PLAYLIST,
            name=f"播放播放列表: {play.playlist_id}",
            cron_expression=play.cron_expression,
            params={"playlist_id": play.playlist_id},
            enabled=True,
        )
        return TaskResponse(**result)
    except Exception as e:
        _log.error("创建定时播放播放列表任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/scheduler/quick/command", response_model=TaskResponse)
async def quick_command(
    cmd: QuickCommandCreate, scheduler: SchedulerService = Depends(get_scheduler)
):
    """快速创建定时/延迟执行指令任务

    可以创建两种类型的任务：
    1. 定时执行：提供 cron_expression（如："0 7 * * *" 每天早上7点）
    2. 延迟执行：提供 delay_minutes（如：10 表示10分钟后执行）

    必须提供 cron_expression 或 delay_minutes 之一
    """
    try:
        # 验证参数
        if not cmd.cron_expression and not cmd.delay_minutes:
            raise HTTPException(
                status_code=400, detail="必须提供 cron_expression 或 delay_minutes 之一"
            )

        if cmd.cron_expression and cmd.delay_minutes:
            raise HTTPException(
                status_code=400, detail="不能同时提供 cron_expression 和 delay_minutes"
            )

        task_id = str(uuid.uuid4())
        params = {"command": cmd.command}
        if cmd.device_id:
            params["device_id"] = cmd.device_id

        # 定时执行
        if cmd.cron_expression:
            result = await scheduler.add_cron_task(
                task_id=task_id,
                task_type=TaskType.COMMAND,
                name=f"执行指令: {cmd.command}",
                cron_expression=cmd.cron_expression,
                params=params,
                enabled=True,
            )
        # 延迟执行
        else:
            run_date = datetime.now() + timedelta(minutes=cmd.delay_minutes)
            result = await scheduler.add_date_task(
                task_id=task_id,
                task_type=TaskType.COMMAND,
                name=f"执行指令: {cmd.command}",
                run_date=run_date,
                params=params,
                enabled=True,
            )

        return TaskResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        _log.error("创建定时执行指令任务失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")
