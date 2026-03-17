from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from xiaoai_media.api.routes import devices, tts, volume, command, config, music

app = FastAPI(
    title="XiaoAI Media API",
    description="Manage Xiaomi AI speakers via MiService",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(devices.router, prefix="/api")
app.include_router(tts.router, prefix="/api")
app.include_router(volume.router, prefix="/api")
app.include_router(command.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(music.router, prefix="/api")

# Serve frontend static files in production (built by Docker)
_static_dir = Path(__file__).resolve().parents[5] / "static"
if _static_dir.is_dir():
    app.mount(
        "/assets", StaticFiles(directory=str(_static_dir / "assets")), name="assets"
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index = _static_dir / "index.html"
        return FileResponse(str(index))
