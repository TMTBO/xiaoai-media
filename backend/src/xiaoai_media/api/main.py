from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

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
    auth,
)
from xiaoai_media.conversation import ConversationPoller
from xiaoai_media.command_handler import CommandHandler
from xiaoai_media.playback_monitor import get_monitor
from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import set_global_client
from xiaoai_media import config as app_config
from xiaoai_media.services.scheduler_service import get_scheduler_service, TaskType
from xiaoai_media.scheduler_executor import get_scheduler_executor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    logger = logging.getLogger(__name__)
    
    # Startup
    logger.info("应用启动中...")
    
    # Reset monitor instance to ensure clean state after reload
    from xiaoai_media.playback_monitor import reset_monitor
    reset_monitor()
    
    # Initialize global XiaoAiClient
    client = XiaoAiClient()
    await client.connect()
    set_global_client(client)
    logger.info("XiaoAiClient 已初始化")
    
    if app_config.ENABLE_CONVERSATION_POLLING:
        await conversation_poller.start()
        logger.info("对话监听已启用")
    else:
        logger.info("对话监听已禁用")
    
    # Check and resume playback monitoring if needed
    if app_config.ENABLE_PLAYBACK_MONITOR:
        logger.info("播放监控已启用，检查是否需要恢复监听...")
        monitor = get_monitor()
        await monitor.check_and_resume()
    else:
        logger.info("播放监控已禁用")
    
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
    logger.info("定时任务调度器已启动")
    
    logger.info("应用启动完成")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("开始关闭应用...")
    
    try:
        await asyncio.wait_for(conversation_poller.stop(), timeout=1.0)
        logger.info("对话监听已停止")
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning("停止对话监听失败: %s", e)
    
    try:
        monitor = get_monitor()
        await asyncio.wait_for(monitor.stop(), timeout=1.0)
        logger.info("播放监控器已停止")
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning("停止播放监控器失败: %s", e)
    
    try:
        scheduler_service = get_scheduler_service()
        await asyncio.wait_for(scheduler_service.stop(), timeout=1.0)
        logger.info("定时任务调度器已停止")
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning("停止定时任务调度器失败: %s", e)
    
    logger.info("应用已关闭")


app = FastAPI(
    title="XiaoAI Media API",
    description="Manage Xiaomi AI speakers via MiService",
    version="0.1.0",
    lifespan=lifespan,
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

# API routes
# 登录路由不需要认证
app.include_router(auth.router, prefix="/api")

# 其他所有路由都需要登录态校验
from xiaoai_media.api.dependencies import get_current_user
from fastapi import Depends

app.include_router(devices.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(tts.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(volume.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(command.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(config.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(music.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(playlist.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(proxy.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(scheduler.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(state.router, prefix="/api", dependencies=[Depends(get_current_user)])

# Serve frontend static files in production (built by Docker)
_static_dir = Path(__file__).resolve().parents[4] / "static"
if _static_dir.is_dir():
    # Mount assets directory for JS/CSS bundles
    app.mount(
        "/assets", StaticFiles(directory=str(_static_dir / "assets")), name="assets"
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Check if the requested file exists in static directory (e.g., logo.svg, favicon.ico)
        file_path = _static_dir / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        
        # Otherwise, serve the SPA index.html for client-side routing
        index = _static_dir / "index.html"
        return FileResponse(str(index))
