"""音乐服务层

处理音乐搜索、排行榜、播放列表加载等业务逻辑。
"""

from __future__ import annotations

import logging
import re
from difflib import get_close_matches
from typing import Any

import aiohttp
from fastapi import HTTPException

from xiaoai_media import config

_log = logging.getLogger(__name__)

# 支持的音乐平台
PLATFORMS = {"tx", "kw", "kg", "wy", "mg"}

# 平台关键词映射（用于自然语言命令解析）
PLATFORM_KEYWORDS: dict[str, str] = {
    "腾讯音乐": "tx",
    "腾讯": "tx",
    "qq音乐": "tx",
    "qq": "tx",
    "网易云音乐": "wy",
    "网易云": "wy",
    "网易": "wy",
    "酷我音乐": "kw",
    "酷我": "kw",
    "酷狗音乐": "kg",
    "酷狗": "kg",
    "咪咕音乐": "mg",
    "咪咕": "mg",
}


class MusicService:
    """音乐服务类，封装音乐API相关的业务逻辑"""

    @staticmethod
    async def proxy_request(method: str, path: str, **kwargs: Any) -> dict:
        """代理请求到音乐下载服务
        
        Args:
            method: HTTP方法 (GET, POST等)
            path: API路径
            **kwargs: 传递给aiohttp的额外参数
            
        Returns:
            API响应的JSON数据
            
        Raises:
            HTTPException: 当请求失败时
        """
        base = config.MUSIC_API_BASE_URL.rstrip("/")
        url = f"{base}{path}"
        _log.info("MusicAPI: %s %s", method.upper(), url)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, timeout=aiohttp.ClientTimeout(total=10), **kwargs
                ) as resp:
                    data: dict = await resp.json(content_type=None)
                    _log.info(
                        "MusicAPI: response code=%s status=%d",
                        data.get("code"),
                        resp.status,
                    )
                    if resp.status >= 500:
                        raise HTTPException(
                            status_code=502,
                            detail=f"Music API returned HTTP {resp.status}",
                        )
                    return data
        except aiohttp.ClientError as e:
            _log.error("MusicAPI connection error: %s", e)
            raise HTTPException(
                status_code=502,
                detail=f"Cannot connect to music service at {config.MUSIC_API_BASE_URL}: {e}",
            )

    @staticmethod
    def validate_platform(platform: str | None) -> str:
        """验证并返回有效的平台代码
        
        Args:
            platform: 平台代码，如果为None则使用默认平台
            
        Returns:
            有效的平台代码
            
        Raises:
            HTTPException: 当平台代码无效时
        """
        plat = platform or config.MUSIC_DEFAULT_PLATFORM
        if plat not in PLATFORMS:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid platform: {plat!r}. Must be one of: {', '.join(sorted(PLATFORMS))}",
            )
        return plat

    @staticmethod
    def parse_chart_command(text: str) -> tuple[str | None, str]:
        """解析排行榜播放命令
        
        处理类似 "播放腾讯热歌榜", "打开网易云飙升榜", "播放排行榜" 等命令
        
        Args:
            text: 用户输入的命令文本
            
        Returns:
            (平台代码|None, 排行榜关键词) 元组
        """
        text = re.sub(r"^(打开|播放)\s*", "", text.strip())
        platform: str | None = None
        
        # 按长度降序排序，优先匹配较长的关键词
        for keyword in sorted(PLATFORM_KEYWORDS, key=len, reverse=True):
            if keyword.lower() in text.lower():
                platform = PLATFORM_KEYWORDS[keyword]
                text = re.sub(re.escape(keyword), "", text, flags=re.IGNORECASE)
                break
        
        text = re.sub(r"^[的\s]+", "", text).strip()
        return platform, text

    @staticmethod
    def find_chart(chart_list: list[dict], keyword: str) -> dict | None:
        """根据关键词查找最匹配的排行榜
        
        匹配策略：子串匹配 → 模糊匹配(difflib) → 字符级部分匹配 → 返回第一个
        
        Args:
            chart_list: 排行榜列表
            keyword: 搜索关键词
            
        Returns:
            匹配的排行榜字典，如果没有找到则返回None或第一个
        """
        if not chart_list:
            return None
        if not keyword:
            return chart_list[0]
        
        kw = keyword.lower()
        
        # 精确子串匹配
        for c in chart_list:
            if kw in c.get("name", "").lower():
                return c
        
        # 模糊匹配（使用difflib）
        names = [c.get("name", "") for c in chart_list]
        matches = get_close_matches(keyword, names, n=1, cutoff=0.3)
        if matches:
            matched_name = matches[0]
            for c in chart_list:
                if c.get("name") == matched_name:
                    return c
        
        # 字符级部分匹配
        for c in chart_list:
            name = c.get("name", "").lower()
            if any(ch in name for ch in kw if ch.strip()):
                return c
        
        return chart_list[0]

    @staticmethod
    async def search_music(
        query: str,
        platform: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        """搜索音乐
        
        Args:
            query: 搜索关键词
            platform: 平台代码
            page: 页码
            limit: 每页数量
            
        Returns:
            搜索结果
        """
        if not query.strip():
            raise HTTPException(status_code=422, detail="query must not be empty")
        
        plat = MusicService.validate_platform(platform)
        return await MusicService.proxy_request(
            "POST",
            "/api/v3/search",
            json={"platform": plat, "query": query.strip(), "page": page, "limit": limit},
        )

    @staticmethod
    async def get_ranks(platform: str | None = None) -> dict:
        """获取平台的排行榜列表
        
        Args:
            platform: 平台代码
            
        Returns:
            排行榜列表
        """
        plat = MusicService.validate_platform(platform)
        return await MusicService.proxy_request("GET", f"/api/v3/{plat}/ranks")

    @staticmethod
    async def get_rank_songs(
        rank_id: str,
        platform: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> dict:
        """获取指定排行榜的歌曲列表
        
        Args:
            rank_id: 排行榜ID
            platform: 平台代码
            page: 页码
            limit: 每页数量
            
        Returns:
            歌曲列表
        """
        plat = MusicService.validate_platform(platform)
        return await MusicService.proxy_request(
            "GET",
            f"/api/v3/{plat}/rank/{rank_id}",
            params={"page": page, "limit": limit},
        )
