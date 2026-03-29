"""FastAPI dependencies for dependency injection."""

from fastapi import HTTPException, Header
from xiaoai_media.client import XiaoAiClient

# Global XiaoAiClient instance (shared across all requests)
_global_client: XiaoAiClient | None = None


def set_global_client(client: XiaoAiClient) -> None:
    """Set the global XiaoAiClient instance (called at startup)."""
    global _global_client
    _global_client = client


async def get_client() -> XiaoAiClient:
    """Dependency to get the global XiaoAiClient instance.
    
    This is used as a FastAPI dependency for route handlers.
    """
    global _global_client
    if _global_client is None:
        raise RuntimeError("XiaoAiClient not initialized")
    return _global_client


def get_client_sync() -> XiaoAiClient:
    """Get the global XiaoAiClient instance synchronously.
    
    This is used by service classes that need access to the client
    outside of FastAPI route handlers.
    """
    global _global_client
    if _global_client is None:
        raise RuntimeError("XiaoAiClient not initialized")
    return _global_client


def get_current_user(authorization: str = Header(None)) -> dict:
    """从请求头获取当前用户（用于登录态校验）"""
    from xiaoai_media.services.user_service import get_user_service
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")
    
    token = authorization.replace("Bearer ", "")
    user_service = get_user_service()
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    return payload


