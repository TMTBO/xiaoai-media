from fastapi import APIRouter, HTTPException, Query, Depends

from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import get_client

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
async def list_devices(
    refresh: bool = Query(
        False, description="Force re-fetch from Xiaomi API, bypassing cache"
    ),
    client: XiaoAiClient = Depends(get_client),
):
    """List all connected Xiaomi AI speaker devices."""
    try:
        devices = await client.list_devices(force_refresh=refresh)
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
