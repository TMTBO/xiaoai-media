"""播放列表加载服务

处理从不同来源（搜索、排行榜、保存的播放列表）加载播放列表的业务逻辑。
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel

from xiaoai_media.player import get_player
from .music_service import MusicService

_log = logging.getLogger(__name__)


class SongQuality(BaseModel):
    """歌曲音质信息"""
    type: str  # e.g. '128k', '320k', 'flac'
    format: str = "mp3"
    size: int | str = 0  # bytes or human-readable string, e.g. '9.15M'


class SongMeta(BaseModel):
    """歌曲元数据"""
    albumName: str = ""
    picUrl: str = ""
    songId: int | str = 0


class SongItem(BaseModel):
    """歌曲项"""
    id: str
    name: str
    singer: str
    platform: str
    qualities: list[SongQuality] = []
    interval: int = 0  # duration in seconds
    meta: SongMeta = SongMeta()


class PlaylistLoaderService:
    """播放列表加载服务类"""

    @staticmethod
    def parse_songs_from_api_response(songs_raw: list[dict], platform: str) -> list[SongItem]:
        """从API响应中解析歌曲列表
        
        Args:
            songs_raw: API返回的原始歌曲数据
            platform: 平台代码
            
        Returns:
            解析后的歌曲列表
        """
        songs = []
        for s in songs_raw:
            try:
                songs.append(
                    SongItem(
                        id=str(s.get("id", "")),
                        name=str(s.get("name", "")),
                        singer=str(s.get("singer", "")),
                        platform=platform,
                        qualities=s.get("qualities", []),
                        interval=s.get("interval", 0),
                        meta=s.get("meta", {}),
                    )
                )
            except Exception as e:
                _log.warning("Failed to parse song: %s", e)
                continue
        return songs

    @staticmethod
    async def load_from_search(
        query: str,
        device_id: str | None = None,
        platform: str | None = None,
        auto_play: bool = True,
    ) -> dict:
        """从搜索结果加载播放列表
        
        Args:
            query: 搜索关键词
            device_id: 设备ID
            platform: 平台代码
            auto_play: 是否自动播放
            
        Returns:
            加载结果
        """
        if not query.strip():
            raise HTTPException(status_code=422, detail="query must not be empty")

        plat = MusicService.validate_platform(platform)

        # 搜索音乐
        _log.info("Loading playlist from search: query=%s platform=%s", query, plat)
        search_data = await MusicService.search_music(query, plat, page=1, limit=50)

        songs_raw: list[dict] = search_data.get("data", {}).get("list", []) or []
        if not songs_raw:
            raise HTTPException(status_code=404, detail=f"没有找到歌曲: {query}")

        # 解析歌曲列表
        songs = PlaylistLoaderService.parse_songs_from_api_response(songs_raw, plat)
        if not songs:
            raise HTTPException(status_code=404, detail="Failed to parse search results")

        # 加载到播放列表
        player = get_player()
        player.set_playlist(
            device_id,
            [s.model_dump() for s in songs],
            current_index=0,
        )
        _log.info(
            "Loaded %d songs from search into playlist for device %s",
            len(songs),
            device_id,
        )

        result = {
            "action": "load_from_search",
            "query": query,
            "platform": plat,
            "device_id": device_id,
            "total": len(songs),
            "songs": [
                {"name": s.name, "singer": s.singer} for s in songs[:10]
            ],  # Preview first 10
        }

        # 自动播放
        if auto_play:
            _log.info("Auto-playing first song from search results")
            try:
                play_result = await player.play_at_index(
                    device_id, 0, stop_first=True, action_name="play"
                )
                result["play_result"] = play_result
            except Exception as e:
                _log.error("Auto-play failed: %s", e, exc_info=True)
                result["play_error"] = str(e)

        return result

    @staticmethod
    async def load_from_chart(
        chart_id: str | None = None,
        chart_keyword: str | None = None,
        device_id: str | None = None,
        platform: str | None = None,
        auto_play: bool = True,
    ) -> dict:
        """从排行榜加载播放列表
        
        Args:
            chart_id: 排行榜ID
            chart_keyword: 排行榜关键词
            device_id: 设备ID
            platform: 平台代码
            auto_play: 是否自动播放
            
        Returns:
            加载结果
        """
        if not chart_id and not chart_keyword:
            raise HTTPException(
                status_code=422,
                detail="Either chart_id or chart_keyword must be provided",
            )

        plat = MusicService.validate_platform(platform)

        # 获取排行榜列表
        _log.info("Loading playlist from chart: platform=%s", plat)
        charts_data = await MusicService.get_ranks(plat)
        chart_list: list[dict] = charts_data.get("data", {}).get("list", []) or []

        if not chart_list:
            raise HTTPException(
                status_code=404, detail=f"No charts available for platform {plat}"
            )

        # 查找排行榜
        matched_chart = None
        if chart_id:
            # 按ID查找
            for c in chart_list:
                if str(c.get("id", "")) == chart_id:
                    matched_chart = c
                    break
        else:
            # 按关键词查找
            matched_chart = MusicService.find_chart(chart_list, chart_keyword or "")

        if not matched_chart:
            raise HTTPException(
                status_code=404,
                detail=f"Chart not found: {chart_id or chart_keyword}",
            )

        rank_id = str(matched_chart.get("id", ""))
        chart_name = matched_chart.get("name", "")

        # 获取排行榜歌曲
        _log.info("Loading songs from chart: %s (id=%s)", chart_name, rank_id)
        songs_data = await MusicService.get_rank_songs(rank_id, plat, page=1, limit=50)

        songs_raw: list[dict] = songs_data.get("data", {}).get("list", []) or []
        if not songs_raw:
            raise HTTPException(status_code=404, detail=f"No songs in chart: {chart_name}")

        # 解析歌曲列表
        songs = PlaylistLoaderService.parse_songs_from_api_response(songs_raw, plat)
        if not songs:
            raise HTTPException(status_code=404, detail="Failed to parse chart songs")

        # 加载到播放列表
        player = get_player()
        player.set_playlist(
            device_id,
            [s.model_dump() for s in songs],
            current_index=0,
        )
        _log.info(
            "Loaded %d songs from chart '%s' into playlist for device %s",
            len(songs),
            chart_name,
            device_id,
        )

        result = {
            "action": "load_from_chart",
            "chart_name": chart_name,
            "chart_id": rank_id,
            "platform": plat,
            "device_id": device_id,
            "total": len(songs),
            "songs": [
                {"name": s.name, "singer": s.singer} for s in songs[:10]
            ],  # Preview first 10
        }

        # 自动播放
        if auto_play:
            _log.info("Auto-playing first song from chart")
            try:
                play_result = await player.play_at_index(
                    device_id, 0, stop_first=True, action_name="play"
                )
                result["play_result"] = play_result
            except Exception as e:
                _log.error("Auto-play failed: %s", e, exc_info=True)
                result["play_error"] = str(e)

        return result

    @staticmethod
    async def load_from_saved_playlist(
        playlist_id: str,
        device_id: str | None = None,
        auto_play: bool = True,
    ) -> dict:
        """从保存的播放列表加载
        
        Args:
            playlist_id: 播放列表ID
            device_id: 设备ID
            auto_play: 是否自动播放
            
        Returns:
            加载结果
        """
        # 导入播放列表加载函数
        from xiaoai_media.services.playlist_storage import PlaylistStorage

        index = PlaylistStorage.load_index()
        if playlist_id not in index:
            raise HTTPException(
                status_code=404,
                detail=f"Playlist not found: {playlist_id}",
            )

        # 加载完整的播放列表
        playlist = PlaylistStorage.load_playlist(playlist_id)

        if not playlist.items:
            raise HTTPException(
                status_code=400,
                detail=f"Playlist is empty: {playlist.name}",
            )

        _log.info(
            "Loading playlist '%s' with %d items for device %s",
            playlist.name,
            len(playlist.items),
            device_id,
        )

        # 将播放列表项转换为SongItem格式
        songs = []
        for item in playlist.items:
            try:
                songs.append(
                    SongItem(
                        id=item.url or f"playlist_{playlist.id}_{len(songs)}",
                        name=item.title,
                        singer=item.artist,
                        platform="custom",  # 标记为自定义来源
                        qualities=[],
                        interval=item.duration,
                        meta=SongMeta(albumName=item.album, picUrl=item.cover_url),
                    )
                )
            except Exception as e:
                _log.warning("Failed to convert playlist item to SongItem: %s", e)
                continue

        if not songs:
            raise HTTPException(
                status_code=400,
                detail="Failed to convert playlist items",
            )

        # 加载到播放列表
        player = get_player()
        player.set_playlist(
            device_id,
            [s.model_dump() for s in songs],
            current_index=0,
            source="playlist",
            source_id=playlist_id,
            source_name=playlist.name,
        )
        _log.info(
            "Loaded %d songs from playlist '%s' for device %s",
            len(songs),
            playlist.name,
            device_id,
        )

        result = {
            "action": "load_from_playlist",
            "playlist_name": playlist.name,
            "playlist_id": playlist_id,
            "device_id": device_id,
            "total": len(songs),
            "songs": [
                {"name": s.name, "singer": s.singer} for s in songs[:10]
            ],
        }

        # 自动播放
        if auto_play:
            _log.info("Auto-playing first item from playlist")
            try:
                play_result = await player.play_at_index(
                    device_id, 0, stop_first=True, action_name="play"
                )
                result["play_result"] = play_result
            except Exception as e:
                _log.error("Auto-play failed: %s", e, exc_info=True)
                result["play_error"] = str(e)
                result["play_error_note"] = (
                    "Playlist items may require custom URL resolution. "
                    "Please ensure playlist items have valid URLs or implement custom URL fetching."
                )

        return result
