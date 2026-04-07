"""FastAPI dependencies for dependency injection."""

import ipaddress

from fastapi import Header, HTTPException, Request

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient, get_client_sync
from xiaoai_media.services.user_service import get_user_service


async def get_client() -> XiaoAiClient:
    """Dependency to get the global XiaoAiClient instance.

    This is used as a FastAPI dependency for route handlers.
    """
    return get_client_sync()


def get_current_user(authorization: str = Header(None)) -> dict:
    """从请求头获取当前用户（用于登录态校验）"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")

    token = authorization.replace("Bearer ", "")
    user_service = get_user_service()
    payload = user_service.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    return payload


def is_lan_ip(ip: str, lan_networks: list[str]) -> bool:
    """检查 IP 是否在局域网范围内

    Args:
        ip: 客户端 IP 地址
        lan_networks: 局域网 CIDR 列表

    Returns:
        True 表示是局域网 IP
    """
    try:
        client_ip = ipaddress.ip_address(ip)
        for network_str in lan_networks:
            network = ipaddress.ip_network(network_str, strict=False)
            if client_ip in network:
                return True
        return False
    except ValueError:
        return False


def get_current_user_or_skip_for_lan(
    request: Request, authorization: str = Header(None)
) -> dict | None:
    """从请求头获取当前用户，或在局域网访问时跳过校验

    用于 proxy 路由，允许局域网内的设备（如小爱音箱）无需认证访问
    """
    # 获取客户端 IP
    client_ip = request.client.host if request.client else None

    # 如果启用了局域网跳过认证，且客户端 IP 在局域网范围内
    if config.PROXY_SKIP_AUTH_FOR_LAN and client_ip:
        if is_lan_ip(client_ip, config.PROXY_LAN_NETWORKS):
            # 返回一个虚拟的系统用户标识
            return {"sub": "lan_device", "role": "system", "skip_auth": True}

    # 否则执行正常的身份校验
    return get_current_user(authorization)
