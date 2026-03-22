from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends

from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import get_client

router = APIRouter(prefix="/volume", tags=["volume"])


class VolumeRequest(BaseModel):
    volume: int = Field(..., ge=0, le=100, description="Volume level 0-100")
    device_id: str | None = None


@router.post("")
async def set_volume(req: VolumeRequest, client: XiaoAiClient = Depends(get_client)):
    """Set speaker volume (0-100)."""
    try:
        result = await client.set_volume(req.volume, req.device_id)
        return result
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Volume API error: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=f"Failed to set volume: {str(e)}")


@router.get("")
async def get_volume(device_id: str | None = None, client: XiaoAiClient = Depends(get_client)):
    """Get current speaker volume."""
    try:
        result = await client.get_volume(device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

