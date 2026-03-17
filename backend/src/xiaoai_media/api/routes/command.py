from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from xiaoai_media.client import XiaoAiClient

router = APIRouter(prefix="/command", tags=["command"])


class CommandRequest(BaseModel):
    text: str
    device_id: str | None = None


@router.post("")
async def send_command(req: CommandRequest):
    """Send a voice command to the speaker."""
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")
    try:
        async with XiaoAiClient() as client:
            result = await client.send_command(req.text, req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
