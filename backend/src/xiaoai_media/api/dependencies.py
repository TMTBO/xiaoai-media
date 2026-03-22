"""FastAPI dependencies for dependency injection."""

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

