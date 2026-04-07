"""音乐服务层

处理音乐搜索、排行榜、播放列表加载等业务逻辑。
负责参数校验，实际的 API 调用委托给 music_provider。
"""

from __future__ import annotations

import re
import sys
from difflib import get_close_matches
from pathlib import Path

from fastapi import HTTPException

from xiaoai_media import config
from xiaoai_media.logger import get_logger

# 导入 music_provider 中的实现
try:
    from music_provider import (
        get_rank_songs as provider_get_rank_songs,
        get_ranks as provider_get_ranks,
        search_music as provider_search_music,
    )
except ImportError:
    # 如果 music_provider 不在路径中，尝试从根目录导入
    root_dir = Path(__file__).parent.parent.parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from music_provider import (
        get_rank_songs as provider_get_rank_songs,
        get_ranks as provider_get_ranks,
        search_music as provider_search_music,
    )

_log = get_logger()

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
    """音乐服务类，封装音乐API相关的业务逻辑

    此类负责参数校验和业务逻辑，实际的 API 调用委托给 music_provider。
    用户可以通过修改 music_provider.py 来自定义音乐源的实现。
    """

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

        Raises:
            HTTPException: 参数校验失败或 API 调用失败
        """
        # 参数校验
        if not query.strip():
            raise HTTPException(status_code=422, detail="query must not be empty")

        plat = MusicService.validate_platform(platform)

        # 调用 music_provider 实现
        try:
            return await provider_search_music(
                query=query.strip(),
                platform=plat,
                page=page,
                limit=limit,
                music_api_base_url=config.MUSIC_API_BASE_URL,
            )
        except HTTPException:
            raise
        except Exception as e:
            _log.error("Search music failed: %s", e, exc_info=True)
            raise HTTPException(
                status_code=502,
                detail=f"Failed to search music: {e}",
            )

    @staticmethod
    async def get_ranks(platform: str | None = None) -> dict:
        """获取平台的排行榜列表

        Args:
            platform: 平台代码

        Returns:
            排行榜列表

        Raises:
            HTTPException: 参数校验失败或 API 调用失败
        """
        # 参数校验
        plat = MusicService.validate_platform(platform)

        # 调用 music_provider 实现
        try:
            return await provider_get_ranks(
                platform=plat,
                music_api_base_url=config.MUSIC_API_BASE_URL,
            )
        except HTTPException:
            raise
        except Exception as e:
            _log.error("Get ranks failed: %s", e, exc_info=True)
            raise HTTPException(
                status_code=502,
                detail=f"Failed to get ranks: {e}",
            )

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

        Raises:
            HTTPException: 参数校验失败或 API 调用失败
        """
        # 参数校验
        plat = MusicService.validate_platform(platform)

        # 调用 music_provider 实现
        try:
            return await provider_get_rank_songs(
                rank_id=rank_id,
                platform=plat,
                page=page,
                limit=limit,
                music_api_base_url=config.MUSIC_API_BASE_URL,
            )
        except HTTPException:
            raise
        except Exception as e:
            _log.error("Get rank songs failed: %s", e, exc_info=True)
            raise HTTPException(
                status_code=502,
                detail=f"Failed to get rank songs: {e}",
            )
