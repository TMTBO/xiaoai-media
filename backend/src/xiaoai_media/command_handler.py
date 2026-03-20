"""Command handler for processing voice commands from speakers."""

import logging
import re

import aiohttp

from xiaoai_media import config
from xiaoai_media.client import XiaoAiClient

_log = logging.getLogger(__name__)


class CommandHandler:
    """Handles voice commands detected from speaker conversations."""

    def __init__(self, music_api_base_url: str | None = None):
        """Initialize command handler.
        
        Args:
            music_api_base_url: Base URL for music API (defaults to config)
        """
        self.music_api_base_url = (
            music_api_base_url or config.MUSIC_API_BASE_URL
        ).rstrip("/")

    async def handle_command(self, device_id: str, query: str):
        """Handle a voice command from a speaker.
        
        Args:
            device_id: Device ID that issued the command
            query: Voice command text
        """
        _log.info("收到设备 %s 的指令: %s", device_id, query)
        
        # 检查是否应该处理该指令（唤醒词过滤）
        if not config.should_handle_command(query):
            _log.debug("指令未包含唤醒词，忽略: %s", query)
            return
        
        # 预处理指令（移除唤醒词等）
        processed_query = config.preprocess_command(query)
        _log.debug("预处理后的指令: %s", processed_query)
        
        # Parse play command
        play_info = self._parse_play_command(processed_query)
        if play_info:
            _log.info("检测到播放指令: %s", play_info["query"])
            await self._handle_play_command(device_id, play_info["query"])
            return
        
        _log.debug("未匹配到播放指令: %s", processed_query)

    def _parse_play_command(self, query: str) -> dict | None:
        """Parse a play command from natural language query.
        
        Detects patterns like:
        - "播放周杰伦的晴天"
        - "播放晴天"
        - "播放歌曲晴天"
        - "打开周杰伦的歌"
        
        Returns:
            dict with 'action' and 'query' keys, or None if not a play command
        """
        query = query.strip()
        
        # Pattern: 播放/打开 [歌曲] 内容
        play_patterns = [
            r"^(?:播放|打开)(?:歌曲)?(.+)$",
        ]
        
        for pattern in play_patterns:
            match = re.match(pattern, query)
            if match:
                content = match.group(1).strip()
                # Filter out common non-music commands
                if content and not any(
                    x in content for x in ["音量", "暂停", "继续", "停止", "下一首", "上一首"]
                ):
                    return {
                        "action": "play",
                        "query": content,
                    }
        
        return None

    async def _handle_play_command(self, device_id: str, search_query: str):
        """Handle a play command by searching and playing music.

        Args:
            device_id: Device ID to play on
            search_query: Search query (e.g., "周杰伦的晴天" or "晴天")
        """
        import time
        start_time = time.time()
        _log.info("处理播放指令: 在设备 %s 上搜索并播放 '%s'", device_id, search_query)

        try:
            # Step 1: Search for music
            search_start = time.time()
            search_results = await self._search_music(search_query)
            search_time = time.time() - search_start
            _log.info("搜索耗时: %.2f 秒", search_time)

            if not search_results:
                _log.warning("搜索无结果: %s", search_query)
                async with XiaoAiClient() as client:
                    await client.text_to_speech(f"搜索失败，没有找到{search_query}", device_id)
                return

            # Get the first result
            songs = search_results.get("data", {}).get("list", [])
            if not songs:
                _log.warning("搜索返回空列表: %s", search_query)
                async with XiaoAiClient() as client:
                    await client.text_to_speech(f"搜索失败，列表为空", device_id)
                return

            first_song = songs[0]
            song_name = first_song.get("name", "")
            singer = first_song.get("singer", "")
            _log.info(
                "找到歌曲: %s - %s",
                singer,
                song_name,
            )

            # Step 2: Send silent TTS to occupy XiaoAi's response channel
            # This prevents XiaoAi from interrupting the music playback
            async with XiaoAiClient() as client:
                await client.text_to_speech(".", device_id)
                _log.info("已发送静默 TTS 占位")

            # Step 3: Create playlist with search results
            await self._sync_playlist(device_id, songs)

            # Step 4: Play the first song
            play_start = time.time()
            play_result = await self._play_song(device_id, 0)
            play_time = time.time() - play_start

            # Log result without additional TTS (to avoid interrupting playback)
            total_time = time.time() - start_time
            _log.info("播放完成 (总耗时: %.2f 秒)", total_time)
            _log.info("播放结果: %s", play_result)

            if not play_result or not play_result.get("result"):
                _log.warning("播放可能失败，返回结果: %s", play_result)

        except Exception as e:
            _log.error("播放指令处理失败: %s", e, exc_info=True)
            try:
                async with XiaoAiClient() as client:
                    await client.text_to_speech(f"播放出错", device_id)
            except:
                pass

    async def _search_music(self, query: str, platform: str | None = None) -> dict:
        """Search for music via the music API.
        
        Args:
            query: Search query
            platform: Music platform (defaults to config default)
            
        Returns:
            Search results from music API
        """
        plat = platform or config.MUSIC_DEFAULT_PLATFORM
        url = f"{self.music_api_base_url}/api/v3/search"
        
        _log.info("搜索音乐: query=%s platform=%s", query, plat)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"platform": plat, "query": query, "page": 1, "limit": 20},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    data = await resp.json(content_type=None)
                    _log.info("搜索结果 code: %s", data.get("code"))
                    return data
        except Exception as e:
            _log.error("音乐搜索失败: %s", e, exc_info=True)
            raise

    async def _sync_playlist(self, device_id: str, songs: list[dict]):
        """Sync playlist to the music API's internal state.
        
        Args:
            device_id: Device ID
            songs: List of song dictionaries
        """
        # Import here to avoid circular dependency
        from xiaoai_media.api.routes.music import _playlists, SongItem
        
        def parse_interval(interval) -> int:
            """Convert interval from string (MM:SS) or int (seconds) to int seconds."""
            if isinstance(interval, int):
                return interval
            if isinstance(interval, str):
                try:
                    # Parse "MM:SS" format
                    parts = interval.split(":")
                    if len(parts) == 2:
                        minutes, seconds = map(int, parts)
                        return minutes * 60 + seconds
                    # Try direct int conversion
                    return int(interval)
                except (ValueError, AttributeError):
                    return 0
            return 0
        
        song_items = []
        for s in songs:
            try:
                # Ensure platform is set (use default if missing)
                platform = s.get("platform") or config.MUSIC_DEFAULT_PLATFORM
                
                song_items.append(
                    SongItem(
                        id=str(s.get("id", "")),
                        name=str(s.get("name", "")),
                        singer=str(s.get("singer", "")),
                        platform=platform,
                        qualities=s.get("qualities", []),
                        interval=parse_interval(s.get("interval", 0)),
                        meta=s.get("meta", {}),
                    )
                )
            except Exception as e:
                _log.warning("解析歌曲失败: %s", e)
                continue
        
        if song_items:
            _playlists[device_id] = {
                "songs": [s.model_dump() for s in song_items],
                "current": 0,
                "device_id": device_id,
            }
            _log.info("已同步播放列表到设备 %s: %d 首歌曲", device_id, len(song_items))

    async def _play_song(self, device_id: str, index: int) -> dict | None:
        """Play a song from the synced playlist.

        Args:
            device_id: Device ID
            index: Song index in playlist

        Returns:
            Play result dict or None if failed
        """
        # Import here to avoid circular dependency
        from xiaoai_media.api.routes.music import _playlists, _get_play_url_with_fallback

        pl = _playlists.get(device_id)
        if not pl or not pl.get("songs"):
            _log.error("设备 %s 没有播放列表", device_id)
            return None

        songs = pl["songs"]
        if not (0 <= index < len(songs)):
            _log.error("歌曲索引 %d 超出范围（设备 %s）", index, device_id)
            return None

        song = songs[index]
        _log.info(
            "正在获取歌曲 URL: %s - %s (平台: %s)",
            song.get("singer"),
            song.get("name"),
            song.get("platform"),
        )

        try:
            play_info = await _get_play_url_with_fallback(song)
            if not play_info:
                _log.error("无法获取播放 URL: %s", song.get("name"))
                return None

            original_url = play_info["url"]
            _log.info("获取到播放 URL (音质=%s)", play_info["quality"])
            _log.debug("原始 URL: %s", original_url)
            
            # Convert to proxy URL so the speaker can access it
            from xiaoai_media.api.routes.music import _make_proxy_url
            url = _make_proxy_url(original_url)

            # Play the URL on the device
            async with XiaoAiClient() as client:
                result = await client.play_url(url, device_id, _type=1)

            _log.info("播放接口返回: %s", result)

            pl["current"] = index
            _log.info(
                "正在播放 (设备 %s): 第 %d/%d 首 - %s",
                device_id,
                index + 1,
                len(songs),
                song.get("name"),
            )

            return result

        except Exception as e:
            _log.error("播放歌曲失败: %s", e, exc_info=True)
            return None
