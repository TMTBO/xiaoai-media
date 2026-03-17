from fastapi import APIRouter, HTTPException

from xiaoai_media.client import XiaoAiClient

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
async def list_devices():
    """List all connected Xiaomi AI speaker devices."""
    try:
        async with XiaoAiClient() as client:
            devices = await client.list_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
