"""定时任务调度服务

基于 APScheduler 实现的定时任务管理系统，支持：
- 定时播放音乐
- 定时播放播放列表
- 定时提醒
- 任务持久化到 Home 目录
"""

import json
import logging
from xiaoai_media.logger import get_logger
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job

_log = get_logger()


class TaskType(str, Enum):
    """任务类型"""
    PLAY_MUSIC = "play_music"  # 播放音乐
    PLAY_PLAYLIST = "play_playlist"  # 播放播放列表
    REMINDER = "reminder"  # 提醒
    COMMAND = "command"  # 执行语音指令


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self, data_dir: Path | None = None):
        """初始化调度服务
        
        Args:
            data_dir: 数据存储目录，默认为 ~/.xiaoai_media/scheduler
        """
        if data_dir is None:
            data_dir = Path.home() / ".xiaoai_media" / "scheduler"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._tasks_file = self.data_dir / "tasks.json"
        
        # 从配置获取时区
        from xiaoai_media import config
        timezone = getattr(config, 'TIMEZONE', 'Asia/Shanghai')
        
        # 配置调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': True,  # 合并错过的任务
            'max_instances': 3  # 最大并发实例数
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=timezone
        )
        
        # 任务回调函数
        self._task_callbacks: dict[TaskType, Callable] = {}
        
        # 任务元数据（用于持久化）
        self._tasks_metadata: dict[str, dict[str, Any]] = {}
        
        self._load_tasks()
    
    async def update_timezone(self, timezone: str):
        """更新调度器时区
        
        Args:
            timezone: 新的时区标识符
        """
        try:
            was_running = self.scheduler.running
            
            # 如果调度器正在运行，需要先完全停止
            if was_running:
                self.scheduler.shutdown(wait=True)
                _log.info("调度器已停止以更新时区")
            
            # 重新创建调度器实例（使用新时区）
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.jobstores.memory import MemoryJobStore
            from apscheduler.executors.asyncio import AsyncIOExecutor
            
            jobstores = {
                'default': MemoryJobStore()
            }
            executors = {
                'default': AsyncIOExecutor()
            }
            job_defaults = {
                'coalesce': True,
                'max_instances': 3
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone=timezone
            )
            
            _log.info("调度器时区已更新为: %s", timezone)
            
            # 如果之前在运行，重新启动并恢复任务
            if was_running:
                await self.start()
        except Exception as e:
            _log.error("更新调度器时区失败: %s", e, exc_info=True)
    
    def _load_tasks(self):
        """从磁盘加载任务元数据"""
        if self._tasks_file.exists():
            try:
                with open(self._tasks_file, "r", encoding="utf-8") as f:
                    self._tasks_metadata = json.load(f)
                _log.info("已加载 %d 个任务配置", len(self._tasks_metadata))
            except Exception as e:
                _log.error("加载任务配置失败: %s", e)
                self._tasks_metadata = {}
        else:
            _log.info("任务配置文件不存在，将创建新文件")
            self._tasks_metadata = {}
    
    def _save_tasks(self):
        """保存任务元数据到磁盘"""
        try:
            with open(self._tasks_file, "w", encoding="utf-8") as f:
                json.dump(self._tasks_metadata, f, indent=2, ensure_ascii=False)
            _log.debug("已保存任务配置到: %s", self._tasks_file)
        except Exception as e:
            _log.error("保存任务配置失败: %s", e)
    
    def register_callback(self, task_type: TaskType, callback: Callable):
        """注册任务类型的回调函数
        
        Args:
            task_type: 任务类型
            callback: 异步回调函数
        """
        self._task_callbacks[task_type] = callback
        _log.info("已注册任务类型 %s 的回调函数", task_type)
    
    async def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            _log.info("定时任务调度器已启动")
            
            # 恢复持久化的任务
            await self._restore_tasks()
    
    async def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            _log.info("定时任务调度器已停止")
    
    async def _restore_tasks(self):
        """恢复持久化的任务"""
        restored_count = 0
        expired_tasks = []
        
        for task_id, metadata in self._tasks_metadata.items():
            try:
                task_type = TaskType(metadata["task_type"])
                
                # 检查一次性任务是否已过期
                if metadata.get("trigger_type") == "date":
                    run_date = datetime.fromisoformat(metadata["run_date"])
                    if run_date < datetime.now():
                        _log.info("任务 %s 已过期，跳过恢复", task_id)
                        expired_tasks.append(task_id)
                        continue
                
                # 重新创建任务
                if metadata.get("trigger_type") == "cron":
                    await self.add_cron_task(
                        task_id=task_id,
                        task_type=task_type,
                        name=metadata["name"],
                        cron_expression=metadata["cron_expression"],
                        params=metadata.get("params", {}),
                        enabled=metadata.get("enabled", True),
                        restore=True  # 标记为恢复模式，不重复保存
                    )
                elif metadata.get("trigger_type") == "date":
                    await self.add_date_task(
                        task_id=task_id,
                        task_type=task_type,
                        name=metadata["name"],
                        run_date=datetime.fromisoformat(metadata["run_date"]),
                        params=metadata.get("params", {}),
                        enabled=metadata.get("enabled", True),
                        restore=True
                    )
                
                restored_count += 1
            except Exception as e:
                _log.error("恢复任务 %s 失败: %s", task_id, e)
        
        # 清理过期任务
        for task_id in expired_tasks:
            del self._tasks_metadata[task_id]
        
        if expired_tasks:
            self._save_tasks()
        
        _log.info("已恢复 %d 个定时任务", restored_count)
    
    async def _execute_task(self, task_id: str, task_type: TaskType, params: dict[str, Any]):
        """执行任务
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            params: 任务参数
        """
        _log.info("执行任务: %s (类型: %s)", task_id, task_type)
        
        try:
            callback = self._task_callbacks.get(task_type)
            if callback:
                await callback(task_id, params)
                _log.info("任务 %s 执行成功", task_id)
            else:
                _log.error("任务类型 %s 没有注册回调函数", task_type)
        except Exception as e:
            _log.error("任务 %s 执行失败: %s", task_id, e, exc_info=True)
        
        # 检查是否是一次性任务，如果是则删除
        if task_id in self._tasks_metadata:
            metadata = self._tasks_metadata[task_id]
            if metadata.get("trigger_type") == "date":
                _log.info("一次性任务 %s 已完成，删除任务", task_id)
                await self.delete_task(task_id)
    
    async def add_cron_task(
        self,
        task_id: str,
        task_type: TaskType,
        name: str,
        cron_expression: str,
        params: dict[str, Any] | None = None,
        enabled: bool = True,
        restore: bool = False
    ) -> dict[str, Any]:
        """添加 Cron 定时任务
        
        Args:
            task_id: 任务唯一标识
            task_type: 任务类型
            name: 任务名称
            cron_expression: Cron 表达式 (分 时 日 月 周)
            params: 任务参数
            enabled: 是否启用
            restore: 是否为恢复模式（不重复保存）
            
        Returns:
            任务信息
        """
        if params is None:
            params = {}
        
        # 解析 cron 表达式
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Cron 表达式格式错误，应为: 分 时 日 月 周")
        
        minute, hour, day, month, day_of_week = parts
        
        # 从配置获取时区
        from xiaoai_media import config
        timezone = getattr(config, 'TIMEZONE', 'Asia/Shanghai')
        
        # 创建触发器
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            timezone=timezone
        )
        
        # 添加任务到调度器
        if enabled:
            self.scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                id=task_id,
                name=name,
                args=[task_id, task_type, params],
                replace_existing=True
            )
        
        # 保存元数据
        metadata = {
            "task_id": task_id,
            "task_type": task_type.value,
            "name": name,
            "trigger_type": "cron",
            "cron_expression": cron_expression,
            "params": params,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._tasks_metadata[task_id] = metadata
        
        if not restore:
            self._save_tasks()
        
        _log.info("已添加 Cron 任务: %s (%s)", name, cron_expression)
        return metadata
    
    async def add_date_task(
        self,
        task_id: str,
        task_type: TaskType,
        name: str,
        run_date: datetime,
        params: dict[str, Any] | None = None,
        enabled: bool = True,
        restore: bool = False
    ) -> dict[str, Any]:
        """添加一次性定时任务
        
        Args:
            task_id: 任务唯一标识
            task_type: 任务类型
            name: 任务名称
            run_date: 执行时间
            params: 任务参数
            enabled: 是否启用
            restore: 是否为恢复模式
            
        Returns:
            任务信息
        """
        if params is None:
            params = {}
        
        # 检查时间是否已过期
        if run_date < datetime.now():
            raise ValueError("执行时间不能早于当前时间")
        
        # 从配置获取时区
        from xiaoai_media import config
        timezone = getattr(config, 'TIMEZONE', 'Asia/Shanghai')
        
        # 创建触发器
        trigger = DateTrigger(run_date=run_date, timezone=timezone)
        
        # 添加任务到调度器
        if enabled:
            self.scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                id=task_id,
                name=name,
                args=[task_id, task_type, params],
                replace_existing=True
            )
        
        # 保存元数据
        metadata = {
            "task_id": task_id,
            "task_type": task_type.value,
            "name": name,
            "trigger_type": "date",
            "run_date": run_date.isoformat(),
            "params": params,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._tasks_metadata[task_id] = metadata
        
        if not restore:
            self._save_tasks()
        
        _log.info("已添加一次性任务: %s (执行时间: %s)", name, run_date)
        return metadata
    
    async def delete_task(self, task_id: str):
        """删除任务
        
        Args:
            task_id: 任务ID
        """
        # 从调度器删除
        try:
            self.scheduler.remove_job(task_id)
        except Exception:
            pass  # 任务可能不在调度器中
        
        # 从元数据删除
        if task_id in self._tasks_metadata:
            del self._tasks_metadata[task_id]
            self._save_tasks()
            _log.info("已删除任务: %s", task_id)
    
    async def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        cron_expression: Optional[str] = None,
        run_date: Optional[datetime] = None,
        params: Optional[dict[str, Any]] = None,
        enabled: Optional[bool] = None
    ) -> dict[str, Any]:
        """更新任务
        
        Args:
            task_id: 任务ID
            name: 新的任务名称
            cron_expression: 新的 Cron 表达式
            run_date: 新的执行时间
            params: 新的任务参数
            enabled: 是否启用
            
        Returns:
            更新后的任务信息
        """
        if task_id not in self._tasks_metadata:
            raise ValueError(f"任务 {task_id} 不存在")
        
        metadata = self._tasks_metadata[task_id]
        task_type = TaskType(metadata["task_type"])
        
        # 更新字段
        if name is not None:
            metadata["name"] = name
        if params is not None:
            metadata["params"] = params
        if enabled is not None:
            metadata["enabled"] = enabled
        
        # 更新触发器
        if metadata["trigger_type"] == "cron" and cron_expression is not None:
            metadata["cron_expression"] = cron_expression
        elif metadata["trigger_type"] == "date" and run_date is not None:
            if run_date < datetime.now():
                raise ValueError("执行时间不能早于当前时间")
            metadata["run_date"] = run_date.isoformat()
        
        metadata["updated_at"] = datetime.now().isoformat()
        
        # 重新创建任务
        await self.delete_task(task_id)
        
        if metadata["trigger_type"] == "cron":
            await self.add_cron_task(
                task_id=task_id,
                task_type=task_type,
                name=metadata["name"],
                cron_expression=metadata["cron_expression"],
                params=metadata["params"],
                enabled=metadata["enabled"]
            )
        else:
            await self.add_date_task(
                task_id=task_id,
                task_type=task_type,
                name=metadata["name"],
                run_date=datetime.fromisoformat(metadata["run_date"]),
                params=metadata["params"],
                enabled=metadata["enabled"]
            )
        
        _log.info("已更新任务: %s", task_id)
        return metadata
    
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息，不存在则返回 None
        """
        metadata = self._tasks_metadata.get(task_id)
        if metadata:
            # 添加下次执行时间
            job = self.scheduler.get_job(task_id)
            if job and job.next_run_time:
                metadata["next_run_time"] = job.next_run_time.isoformat()
            else:
                metadata["next_run_time"] = None
        return metadata
    
    def list_tasks(self, task_type: Optional[TaskType] = None) -> list[dict[str, Any]]:
        """列出所有任务
        
        Args:
            task_type: 可选的任务类型过滤
            
        Returns:
            任务列表
        """
        tasks = []
        for task_id, metadata in self._tasks_metadata.items():
            if task_type is None or metadata["task_type"] == task_type.value:
                task_info = metadata.copy()
                
                # 添加下次执行时间
                job = self.scheduler.get_job(task_id)
                if job and job.next_run_time:
                    task_info["next_run_time"] = job.next_run_time.isoformat()
                else:
                    task_info["next_run_time"] = None
                
                tasks.append(task_info)
        
        return tasks


# 全局调度服务实例
_scheduler_service: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    """获取全局调度服务实例
    
    Returns:
        SchedulerService 实例
    """
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
