from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from xiaoai_media.client import XiaoAiClient

router = APIRouter(prefix="/volume", tags=["volume"])


class VolumeRequest(BaseModel):
    volume: int = Field(..., ge=0, le=100, description="Volume level 0-100")
    device_id: str | None = None


@router.post("")
async def set_volume(req: VolumeRequest):
    """Set speaker volume (0-100)."""
    try:
        async with XiaoAiClient() as client:
            result = await client.set_volume(req.volume, req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
