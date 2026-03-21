"""配置API路由

处理配置相关的HTTP请求，业务逻辑已移至services层。
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from xiaoai_media.services import ConfigService

router = APIRouter(prefix="/config", tags=["config"])


class ConfigUpdate(BaseModel):
    """配置更新请求模型"""
    MI_USER: str | None = None
    MI_PASS: str | None = None
    MI_PASS_TOKEN: str | None = None
    MI_DID: str | None = None
    MI_REGION: str | None = None
    MUSIC_API_BASE_URL: str | None = None
    MUSIC_DEFAULT_PLATFORM: str | None = None
    SERVER_BASE_URL: str | None = None
    ENABLE_CONVERSATION_POLLING: bool | None = None
    CONVERSATION_POLL_INTERVAL: float | None = Field(None, ge=0.1, le=60)
    ENABLE_WAKE_WORD_FILTER: bool | None = None
    WAKE_WORDS: list[str] | None = None
    LOG_LEVEL: str | None = Field(None, pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    VERBOSE_PLAYBACK_LOG: bool | None = None


@router.get("")
async def get_config():
    """获取当前配置（敏感字段会被掩码）"""
    return ConfigService.get_current_config()


@router.put("")
async def update_config(body: ConfigUpdate):
    """更新user_config.py配置并重新加载"""
    updates = body.model_dump(exclude_none=True)

    # 过滤掉值为 "***" 的敏感字段（表示不更改）
    updates = ConfigService.filter_sensitive_fields(updates)

    if not updates:
        raise HTTPException(status_code=422, detail="No valid updates provided")

    # 验证配置项
    ConfigService.validate_config_keys(updates)

    # 写入配置文件
    ConfigService.write_user_config(updates)

    # 重新加载配置模块
    ConfigService.reload_config_module()

    return {"message": "Configuration updated successfully"}
