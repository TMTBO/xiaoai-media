from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends

from xiaoai_media.client import XiaoAiClient
from xiaoai_media.api.dependencies import get_client

router = APIRouter(prefix="/command", tags=["command"])


class CommandRequest(BaseModel):
    text: str
    device_id: str | None = None
    silent: bool = False  # If True, execute without voice response


@router.post("")
async def send_command(req: CommandRequest, client: XiaoAiClient = Depends(get_client)):
    """Send a voice command to the speaker.

    Args:
        text: Command text
        device_id: Target device ID (optional)
        silent: If True, execute silently without voice response (default: False)
    """
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")
    try:
        result = await client.send_command(req.text, req.device_id, req.silent)
        return result
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(
            "Command endpoint error: %s", e, exc_info=True
        )
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/conversation")
async def get_conversation(
    device_id: str | None = None, client: XiaoAiClient = Depends(get_client)
):
    """Get latest conversation records from the speaker.

    Returns the most recent 20 conversation history including user questions
    and XiaoAi's responses.
    """
    try:
        result = await client.get_latest_ask(device_id, limit=20)

        # Transform to match frontend expected format
        conversations = [
            {
                "timestamp_ms": conv["time"],
                "question": conv["query"],
                "content": conv["answer"],
            }
            for conv in result
        ]

        return {"conversations": conversations}
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(
            "Get conversation error: %s", e, exc_info=True
        )
        raise HTTPException(status_code=502, detail=str(e))
