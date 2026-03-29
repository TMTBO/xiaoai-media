"""
音乐 URL 提供者模块（模板文件）

此模块负责从音乐 API 获取播放 URL，支持音质降级重试。
同时提供音乐搜索、排行榜等接口的实现，方便用户自定义。

使用方法：
1. 将此文件复制为 music_provider.py
2. 确保 music_provider.py 与 user_config.py 在同一目录
3. 根据需要自定义音乐 API 调用逻辑

可自定义的接口：
- search_music(): 搜索音乐
- get_ranks(): 获取排行榜列表
- get_rank_songs(): 获取排行榜歌曲
- get_music_url(): 获取播放 URL
"""

import logging
from typing import Any

import aiohttp

_log = logging.getLogger(__name__)


def _parse_size(size) -> int:
    """解析文件大小为字节数
    
    支持多种格式：
    - 整数：直接返回
    - 字符串：'9.15M', '3.2K', '27.3MB', '1.5G' 等
    
    Args:
        size: 文件大小
        
    Returns:
        字节数
    """
    if isinstance(size, int):
        return size
    s = str(size).strip().upper().rstrip("B")
    try:
        if s.endswith("G"):
            return int(float(s[:-1]) * 1024**3)
        if s.endswith("M"):
            return int(float(s[:-1]) * 1024**2)
        if s.endswith("K"):
            return int(float(s[:-1]) * 1024)
        return int(float(s))
    except ValueError:
        return 0


# ============================================================================
# 音乐搜索、排行榜接口
# ============================================================================


async def search_music(
    query: str,
    platform: str,
    page: int,
    limit: int,
    music_api_base_url: str,
    timeout: int = 10,
) -> dict:
    """搜索音乐
    
    用户可以自定义此函数来实现自己的音乐搜索逻辑。
    例如：添加缓存、聚合多个音乐源、实现自己的搜索算法等。
    
    Args:
        query: 搜索关键词
        platform: 平台代码 (tx, wy, kg, kw, mg)
        page: 页码
        limit: 每页数量
        music_api_base_url: 音乐 API 基础 URL
        timeout: 请求超时时间（秒）
        
    Returns:
        搜索结果字典，格式：
        {
            "code": 0,
            "data": {
                "list": [
                    {
                        "id": "歌曲ID",
                        "name": "歌曲名",
                        "singer": "歌手",
                        "album": "专辑",
                        "pic_url": "封面URL",
                        "interval": 时长（秒）,
                        "qualities": [...],
                        ...
                    }
                ]
            }
        }
        
    示例：
        >>> result = await search_music(
        ...     query="周杰伦",
        ...     platform="tx",
        ...     page=1,
        ...     limit=20,
        ...     music_api_base_url="http://localhost:5050"
        ... )
    """
    url = f"{music_api_base_url.rstrip('/')}/api/v3/search"
    _log.info("Searching music: query=%s platform=%s page=%d limit=%d", query, platform, page, limit)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"platform": platform, "query": query, "page": page, "limit": limit},
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            data = await resp.json(content_type=None)
            _log.info("Search response: code=%s status=%d", data.get("code"), resp.status)
            return data


async def get_ranks(
    platform: str,
    music_api_base_url: str,
    timeout: int = 10,
) -> dict:
    """获取平台的排行榜列表
    
    用户可以自定义此函数来实现自己的排行榜获取逻辑。
    例如：添加缓存、过滤特定排行榜、添加自定义排行榜等。
    
    Args:
        platform: 平台代码 (tx, wy, kg, kw, mg)
        music_api_base_url: 音乐 API 基础 URL
        timeout: 请求超时时间（秒）
        
    Returns:
        排行榜列表字典，格式：
        {
            "code": 0,
            "data": {
                "list": [
                    {
                        "id": "排行榜ID",
                        "name": "排行榜名称",
                        ...
                    }
                ]
            }
        }
        
    示例：
        >>> result = await get_ranks(
        ...     platform="tx",
        ...     music_api_base_url="http://localhost:5050"
        ... )
    """
    url = f"{music_api_base_url.rstrip('/')}/api/v3/{platform}/ranks"
    _log.info("Getting ranks: platform=%s", platform)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            data = await resp.json(content_type=None)
            _log.info("Ranks response: code=%s status=%d", data.get("code"), resp.status)
            return data


async def get_rank_songs(
    rank_id: str,
    platform: str,
    page: int,
    limit: int,
    music_api_base_url: str,
    timeout: int = 10,
) -> dict:
    """获取指定排行榜的歌曲列表
    
    用户可以自定义此函数来实现自己的排行榜歌曲获取逻辑。
    例如：添加缓存、过滤特定歌曲、重新排序等。
    
    Args:
        rank_id: 排行榜ID
        platform: 平台代码 (tx, wy, kg, kw, mg)
        page: 页码
        limit: 每页数量
        music_api_base_url: 音乐 API 基础 URL
        timeout: 请求超时时间（秒）
        
    Returns:
        歌曲列表字典，格式同 search_music
        
    示例：
        >>> result = await get_rank_songs(
        ...     rank_id="26",
        ...     platform="tx",
        ...     page=1,
        ...     limit=50,
        ...     music_api_base_url="http://localhost:5050"
        ... )
    """
    url = f"{music_api_base_url.rstrip('/')}/api/v3/{platform}/rank/{rank_id}"
    _log.info("Getting rank songs: rank_id=%s platform=%s page=%d limit=%d", rank_id, platform, page, limit)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            params={"page": page, "limit": limit},
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            data = await resp.json(content_type=None)
            _log.info("Rank songs response: code=%s status=%d", data.get("code"), resp.status)
            return data


# ============================================================================
# 音乐播放 URL 获取接口
# ============================================================================


async def get_music_url(custom_params: dict, music_api_base_url: str) -> str:
    """获取音乐播放 URL，带音质降级重试
    
    此函数会按照音质从高到低的顺序尝试获取播放 URL，
    直到成功或所有音质都失败。
    
    Args:
        custom_params: 音乐参数字典，包含：
            通用字段（来自 PlaylistItem）：
            - title: 歌曲名/标题
            - artist: 艺术家/歌手
            - album: 专辑名
            - audio_id: 音频ID
            
            音乐特定字段（来自 custom_params）：
            - type: 类型（通常为 "music"）
            - platform: 平台代码，如 tx, wy, kg 等（必需）
            - id/song_id: 歌曲ID（必需）
            - name: 歌曲名称（可选，用于日志，可能与 title 重复）
            - singer: 歌手名称（可选，用于日志，可能与 artist 重复）
            - qualities: 音质列表（可选，格式见下方）
            - meta: 元数据字典（可选）
                - albumName: 专辑名称
                - picUrl: 封面图片 URL
                - songId: 平台歌曲 ID
        
        music_api_base_url: 音乐 API 基础 URL
            例如：http://192.168.1.111:5050
    
    音质列表格式：
        [
            {"type": "flac", "format": "flac", "size": "27.3M"},
            {"type": "320k", "format": "mp3", "size": "9.15M"},
            {"type": "128k", "format": "mp3", "size": "3.2M"}
        ]
    
    Returns:
        播放 URL（原始 URL，不需要包装为代理 URL）
        
    Raises:
        ValueError: 所有音质都获取失败
    
    示例：
        >>> params = {
        ...     "title": "歌曲名",
        ...     "artist": "歌手名",
        ...     "id": "001ABC",
        ...     "platform": "tx",
        ...     "qualities": [
        ...         {"type": "320k", "format": "mp3", "size": "9.15M"}
        ...     ]
        ... }
        >>> url = await get_music_url(params, "http://localhost:5050")
    """
    import aiohttp

    # 提取参数
    song_id = custom_params.get("id") or custom_params.get("song_id", "")
    platform = custom_params.get("platform", "tx")
    name = custom_params.get("name", "")
    singer = custom_params.get("singer", "")
    interval = custom_params.get("interval", 0)
    meta = custom_params.get("meta") or {}
    album_name = meta.get("albumName", "") if isinstance(meta, dict) else ""
    pic_url = meta.get("picUrl", "") if isinstance(meta, dict) else ""
    song_platform_id = meta.get("songId", 0) if isinstance(meta, dict) else 0
    qualities_raw: list[dict] = custom_params.get("qualities") or []

    # 如果没有音质列表，使用默认音质
    qualities = (
        qualities_raw
        if qualities_raw
        else [{"type": "128k", "format": "mp3", "size": 0}]
    )

    # 按文件大小降序排序 - 优先高音质
    qualities_sorted = sorted(
        qualities, key=lambda q: _parse_size(q.get("size", 0)), reverse=True
    )

    # 逐个尝试每个音质，直到成功
    # 注意：这里不使用完全并发，而是按优先级顺序尝试，避免浪费 API 调用
    last_error = None
    async with aiohttp.ClientSession() as session:
        for q in qualities_sorted:
            quality_type = q.get("type", "128k")
            quality_format = q.get("format", "mp3")
            
            try:
                # 调用音乐 API 的 /api/v3/play 端点
                # 注意：这里使用的是特定的 API 格式，您可能需要根据实际 API 调整
                async with session.post(
                    f"{music_api_base_url}/api/v3/play",
                    json={
                        "songId": song_id,
                        "platform": platform,
                        "quality": quality_type,
                        "format": quality_format,
                        "name": name,
                        "singer": singer,
                        "interval": interval,
                        "size": q.get("size", 0),
                        "albumName": album_name,
                        "picUrl": pic_url,
                        "song_platform_id": song_platform_id,
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            url = data.get("data", {}).get("url")
                            if url:
                                print(f"Successfully got URL with quality={quality_type}")
                                return url
                            else:
                                print(f"Quality {quality_type} returned no URL (code={data.get('code')})")
                        else:
                            print(f"Quality {quality_type} failed with code={data.get('code')}")
                    else:
                        print(f"Quality {quality_type} request failed with status={response.status}")

            except Exception as e:
                last_error = e
                print(f"Quality {quality_type} request error: {e}")
                continue

    # 所有音质都失败
    error_msg = f"Failed to get music URL for {singer} - {name}: all qualities failed"
    if last_error:
        error_msg += f" (last error: {last_error})"
    raise ValueError(error_msg)
