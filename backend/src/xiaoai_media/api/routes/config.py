from __future__ import annotations

import os
import importlib
from pathlib import Path

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from xiaoai_media import config

router = APIRouter(prefix="/config", tags=["config"])

_ENV_PATH = Path(__file__).resolve().parents[5] / ".env"
_ALLOWED_KEYS = {
    "MI_USER",
    "MI_PASS",
    "MI_PASS_TOKEN",
    "MI_DID",
    "MI_REGION",
    "MUSIC_API_BASE_URL",
    "MUSIC_DEFAULT_PLATFORM",
}


def _read_env_file() -> dict[str, str]:
    result: dict[str, str] = {}
    if not _ENV_PATH.exists():
        return result
    for line in _ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        result[key.strip()] = val.strip()
    return result


def _write_env_file(data: dict[str, str]) -> None:
    lines = []
    for key, val in data.items():
        lines.append(f"{key}={val}")
    _ENV_PATH.write_text("\n".join(lines) + "\n")


@router.get("")
async def get_config():
    """Return current configuration (password is masked)."""
    return {
        "MI_USER": config.MI_USER,
        "MI_PASS": "***" if config.MI_PASS else "",
        "MI_PASS_TOKEN": "***" if config.MI_PASS_TOKEN else "",
        "MI_DID": config.MI_DID,
        "MI_REGION": config.MI_REGION,
        "MUSIC_API_BASE_URL": config.MUSIC_API_BASE_URL,
        "MUSIC_DEFAULT_PLATFORM": config.MUSIC_DEFAULT_PLATFORM,
    }


class ConfigUpdate(BaseModel):
    MI_USER: str | None = None
    MI_PASS: str | None = None
    MI_PASS_TOKEN: str | None = None
    MI_DID: str | None = None
    MI_REGION: str | None = None
    MUSIC_API_BASE_URL: str | None = None
    MUSIC_DEFAULT_PLATFORM: str | None = None


@router.put("")
async def update_config(body: ConfigUpdate):
    """Update .env configuration and reload."""
    env = _read_env_file()
    updates = body.model_dump(exclude_none=True)

    for key, val in updates.items():
        if key not in _ALLOWED_KEYS:
            raise HTTPException(status_code=422, detail=f"Unknown config key: {key}")
        env[key] = val

    _write_env_file(env)

    # Sync updated values into os.environ so load_dotenv(override=True) picks them up
    for key, val in env.items():
        os.environ[key] = val

    # Reload config module so next request picks up new values
    import xiaoai_media.config as cfg_module

    importlib.reload(cfg_module)

    return {"message": "Configuration updated successfully"}
