from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
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
)
from xiaoai_media.conversation import ConversationPoller
from xiaoai_media.command_handler import CommandHandler
from xiaoai_media.playback_monitor import PlaybackMonitor
from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import set_global_client
from xiaoai_media import config as app_config

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

# Initialize playback monitor for auto-play next track
playback_monitor = PlaybackMonitor(
    poll_interval=app_config.PLAYBACK_MONITOR_INTERVAL
)

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
    
    # Start playback monitor for auto-play next track
    if app_config.ENABLE_PLAYBACK_MONITOR:
        await playback_monitor.start()
        logging.getLogger(__name__).info("播放监控已启用")
    else:
        logging.getLogger(__name__).info("播放监控已禁用")
    
    logging.getLogger(__name__).info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown."""
    await conversation_poller.stop()
    await playback_monitor.stop()
    
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
