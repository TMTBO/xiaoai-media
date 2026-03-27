from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI

# 注意：日志配置由 run.py 中的 uvicorn.run(log_config=...) 统一管理
# 这里只设置特定库的日志级别
# miservice logs every HTTP request at INFO; suppress to WARNING to reduce noise
logging.getLogger("miservice").setLevel(logging.WARNING)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from xiaoai_media.api.routes import (
    devices,
    tts,
    volume,
    command,
    config,
    music,
    playlist,
    proxy,
    scheduler,
    state,
)
from xiaoai_media.conversation import ConversationPoller
from xiaoai_media.command_handler import CommandHandler
from xiaoai_media.playback_monitor import get_monitor
from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import set_global_client
from xiaoai_media import config as app_config
from xiaoai_media.services.scheduler_service import get_scheduler_service, TaskType
from xiaoai_media.scheduler_executor import get_scheduler_executor

app = FastAPI(
    title="XiaoAI Media API",
    description="Manage Xiaomi AI speakers via MiService",
    version="0.1.0",
)

# Initialize conversation poller and command handler
conversation_poller = ConversationPoller(
    poll_interval=app_config.CONVERSATION_POLL_INTERVAL
)
command_handler = CommandHandler()
conversation_poller.set_command_callback(command_handler.handle_command)

# Get global playback monitor instance (singleton)
playback_monitor = get_monitor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    # Initialize global XiaoAiClient
    client = XiaoAiClient()
    await client.connect()
    set_global_client(client)
    logging.getLogger(__name__).info("XiaoAiClient 已初始化")
    
    if app_config.ENABLE_CONVERSATION_POLLING:
        await conversation_poller.start()
        logging.getLogger(__name__).info("对话监听已启用")
    else:
        logging.getLogger(__name__).info("对话监听已禁用")
    
    # Check and resume playback monitoring if needed
    if app_config.ENABLE_PLAYBACK_MONITOR:
        logging.getLogger(__name__).info("播放监控已启用，检查是否需要恢复监听...")
        await playback_monitor.check_and_resume()
    else:
        logging.getLogger(__name__).info("播放监控已禁用")
    
    # Initialize scheduler service
    scheduler_service = get_scheduler_service()
    executor = get_scheduler_executor()
    
    # Register task callbacks
    scheduler_service.register_callback(TaskType.PLAY_MUSIC, executor.execute_play_music)
    scheduler_service.register_callback(TaskType.PLAY_PLAYLIST, executor.execute_play_playlist)
    scheduler_service.register_callback(TaskType.REMINDER, executor.execute_reminder)
    scheduler_service.register_callback(TaskType.COMMAND, executor.execute_command)
    
    # Start scheduler
    await scheduler_service.start()
    logging.getLogger(__name__).info("定时任务调度器已启动")
    
    logging.getLogger(__name__).info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown."""
    await conversation_poller.stop()
    await playback_monitor.stop()
    
    # Stop scheduler
    scheduler_service = get_scheduler_service()
    await scheduler_service.stop()
    logging.getLogger(__name__).info("定时任务调度器已停止")
    
    # Note: XiaoAiClient will be closed automatically when the app shuts down
    # No need to explicitly close it here as it's managed by the dependency system
    
    logging.getLogger(__name__).info("应用已关闭")


# API routes
app.include_router(devices.router, prefix="/api")
app.include_router(tts.router, prefix="/api")
app.include_router(volume.router, prefix="/api")
app.include_router(command.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(music.router, prefix="/api")
app.include_router(playlist.router, prefix="/api")
app.include_router(proxy.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(state.router, prefix="/api")

# Serve frontend static files in production (built by Docker)
_static_dir = Path(__file__).resolve().parents[4] / "static"
if _static_dir.is_dir():
    app.mount(
        "/assets", StaticFiles(directory=str(_static_dir / "assets")), name="assets"
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index = _static_dir / "index.html"
        return FileResponse(str(index))
