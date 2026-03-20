"""音频流代理路由

为小爱音箱提供音频流代理，解决音乐平台的防盗链限制。
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import httpx

_log = logging.getLogger(__name__)
router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.get("/stream")
async def proxy_audio_stream(url: str = Query(..., description="原始音频URL")):
    """代理音频流，添加必要的请求头以绕过防盗链限制。

    Args:
        url: 音乐平台的原始音频URL

    Returns:
        StreamingResponse: 音频流响应

    Example:
        GET /api/proxy/stream?url=https://music.qq.com/xxx.mp3
    """
    if not url:
        raise HTTPException(status_code=422, detail="URL parameter is required")

    _log.info("Proxying audio stream from: %s", url[:100])

    try:
        # 使用 httpx 请求原始 URL，添加必要的请求头
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 添加通用请求头以绕过防盗链
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "identity",
                "Range": "bytes=0-",
            }

            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()

            # 返回流式响应
            async def stream_generator():
                """生成音频流数据块"""
                try:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk
                except Exception as e:
                    _log.error("Error streaming audio: %s", e)
                    raise

            # 构造响应头
            response_headers = {
                "Content-Type": response.headers.get("Content-Type", "audio/mpeg"),
                "Accept-Ranges": "bytes",
            }

            # 如果原始响应有 Content-Length，也传递给客户端
            if "Content-Length" in response.headers:
                response_headers["Content-Length"] = response.headers["Content-Length"]

            _log.debug("Streaming response headers: %s", response_headers)

            return StreamingResponse(
                stream_generator(),
                headers=response_headers,
                media_type=response.headers.get("Content-Type", "audio/mpeg"),
            )

    except httpx.HTTPStatusError as e:
        _log.error(
            "HTTP error while fetching audio: %s - %s",
            e.response.status_code,
            url[:100],
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch audio from source: {e.response.status_code}",
        )
    except httpx.RequestError as e:
        _log.error("Network error while fetching audio: %s - %s", e, url[:100])
        raise HTTPException(
            status_code=502, detail=f"Network error while fetching audio: {str(e)}"
        )
    except Exception as e:
        _log.error("Unexpected error in proxy: %s - %s", e, url[:100])
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")
