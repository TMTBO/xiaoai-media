from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends

from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import get_client

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str
    device_id: str | None = None


@router.post("")
async def text_to_speech(req: TTSRequest, client: XiaoAiClient = Depends(get_client)):
    """Send text-to-speech to a speaker."""
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")
    try:
        result = await client.text_to_speech(req.text, req.device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
