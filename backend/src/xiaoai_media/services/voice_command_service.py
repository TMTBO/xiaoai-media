"""语音命令服务

处理自然语言语音命令的解析和执行。
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from fastapi import HTTPException

from xiaoai_media import config
from xiaoai_media.client import get_client_sync
from xiaoai_media.logger import get_logger
from xiaoai_media.playback_controller import get_controller
from xiaoai_media.services.state_service import get_state_service
from .music_service import MusicService
from .playlist_models import (
    AddItemRequest,
    ContinuePlayRequest,
    CreatePlaylistRequest,
    PlaylistItem,
    PlayModeRequest,
    PlayPlaylistRequest,
)
from .playlist_service import PlaylistService
from .playlist_storage import PlaylistStorage

_log = get_logger()


def _parse_duration(duration_value: Any) -> int:
    """解析duration字段，支持整数和时间字符串格式
    
    Args:
        duration_value: duration值，可能是整数（秒）或字符串（如 "04:00"）
        
    Returns:
        duration的秒数（整数）
    """
    if isinstance(duration_value, int):
        return duration_value
    
    if isinstance(duration_value, str):
        # 尝试解析 "MM:SS" 或 "HH:MM:SS" 格式
        parts = duration_value.split(":")
        try:
            if len(parts) == 2:  # MM:SS
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except (ValueError, IndexError):
            pass
    
    # 默认返回0
    return 0


class VoiceCommandService:
    """语音命令服务类"""

    @staticmethod
    def _get_current_playlist_id(device_id: str | None) -> str | None:
        """获取当前播放的播单ID
        
        Args:
            device_id: 设备ID
            
        Returns:
            播单ID或None
        """
        state_service = get_state_service()
        return state_service.get(f"current_playlist_{device_id or 'default'}")
    
    @staticmethod
    async def _announce_tts(message: str, device_id: str | None):
        """播报TTS消息
        
        Args:
            message: 消息内容
            device_id: 设备ID
        """
        try:
            client = get_client_sync()
            await client.text_to_speech(message, device_id)
        except Exception as e:
            _log.warning("TTS播报失败: %s", e)

    @staticmethod
    async def execute_command(text: str, device_id: str | None = None) -> dict:
        """解析并执行自然语言语音命令
        
        支持的命令模式：
        - "播放/打开 [平台] [排行榜名称]" → 加载排行榜并播放
        - "播放 [播单名称]" → 加载保存的播放列表并播放
        - "继续播放" → 继续播放当前播单
        - "停止播放" → 停止播放
        - "下一首" → 播放下一首（根据播放模式）
        - "列表循环/单曲循环/随机播放" → 设置播放模式
        - "搜索 [关键词]" → 搜索并加载结果
        - 其他文本 → 作为原始语音命令转发给音箱
        
        Args:
            text: 用户输入的命令文本
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        text = text.strip()
        if not text:
            raise HTTPException(status_code=422, detail="text must not be empty")

        # 播放模式控制
        if "列表循环" in text or "循环播放" in text:
            return await VoiceCommandService._handle_play_mode_command("loop", device_id)
        if "单曲循环" in text:
            return await VoiceCommandService._handle_play_mode_command("single", device_id)
        if "随机播放" in text or "随机模式" in text:
            return await VoiceCommandService._handle_play_mode_command("random", device_id)

        # 播放控制
        if "继续播放" in text:
            return await VoiceCommandService._handle_continue_command(device_id)
        if "停止播放" in text or "暂停播放" in text:
            return await VoiceCommandService._handle_stop_command(device_id)
        if "下一首" in text:
            return await VoiceCommandService._handle_next_command(device_id)

        # 模式1: 播放列表 - 优先从所有播单的voice_keywords中匹配
        playlist_result = await VoiceCommandService._try_match_playlist(text, device_id)
        if playlist_result:
            return playlist_result

        # 模式2: 排行榜播放 - 包含"榜"或"排行"
        if re.search(r"(榜|排行)", text):
            return await VoiceCommandService._handle_chart_command(text, device_id)

        # 模式3: 搜索并播放 - "搜索周杰伦", "播放周杰伦的歌"
        search_match = re.match(r"^(搜索|查找)(.+)$", text)
        if search_match:
            return await VoiceCommandService._handle_search_command(
                search_match.group(2).strip(), device_id
            )

        # 回退: 作为原始语音命令转发给音箱
        return await VoiceCommandService._relay_raw_command(text, device_id)

    @staticmethod
    async def _try_match_playlist(text: str, device_id: str | None) -> dict | None:
        """尝试匹配播放列表（不抛出异常）
        
        优先从所有播单的voice_keywords中匹配，匹配到则返回结果，
        匹配不到返回None进入下一步
        
        Args:
            text: 命令文本
            device_id: 设备ID
            
        Returns:
            执行结果或None（未匹配到）
        """
        try:
            # 加载播放列表索引
            index = PlaylistStorage.load_index()
            matched_playlist_id = None

            # 优先从所有播单的voice_keywords中匹配
            for pid, playlist_idx in index.items():
                for vk in playlist_idx.voice_keywords:
                    if vk.lower() in text.lower():
                        matched_playlist_id = pid
                        _log.info("Matched playlist by voice_keyword: %r -> %s", vk, pid)
                        break
                if matched_playlist_id:
                    break

            # 如果没有匹配到，返回None进入下一步
            if not matched_playlist_id:
                _log.debug("No playlist matched by voice_keywords for text=%r", text)
                return None

            # 加载播单获取current_index
            playlist = PlaylistStorage.load_playlist(matched_playlist_id)
            start_index = playlist.current_index if playlist else 0

            # 通过 playlist_service 播放（从current_index开始）
            result = await PlaylistService.play_playlist(
                matched_playlist_id,
                PlayPlaylistRequest(device_id=device_id, start_index=start_index, announce=True)
            )

            _log.info(
                "VoiceCommand: playing playlist %r for device %s",
                result.get("playlist"),
                device_id,
            )

            return {
                "action": "play_playlist",
                "playlist_id": matched_playlist_id,
                "device_id": device_id,
                "result": result,
            }

        except Exception as e:
            _log.error("Failed to match/play playlist: %s", e, exc_info=True)
            return None

    @staticmethod
    async def _handle_playlist_command(text: str, device_id: str | None) -> dict:
        """处理播放列表命令（按名称匹配，作为后备方案）
        
        Args:
            text: 命令文本
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        _log.info("VoiceCommand: trying playlist name match for text=%r", text)
        try:
            # 从命令中提取播放列表名称/关键词
            playlist_keyword = text
            playlist_keyword = re.sub(r"(播单|列表|有声书|播客)\s*$", "", playlist_keyword).strip()

            # 加载播放列表并按名称查找匹配项
            index = PlaylistStorage.load_index()
            matched_playlist_id = None

            for pid, playlist_idx in index.items():
                # 检查播放列表名称是否包含关键词
                if playlist_keyword.lower() in playlist_idx.name.lower():
                    matched_playlist_id = pid
                    _log.info("Matched playlist by name: %r -> %s", playlist_keyword, pid)
                    break

            if not matched_playlist_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"找不到匹配的播单",
                )

            # 通过 playlist_service 播放
            result = await PlaylistService.play_playlist(
                matched_playlist_id,
                PlayPlaylistRequest(device_id=device_id, start_index=0, announce=True)
            )

            _log.info(
                "VoiceCommand: playing playlist %r for device %s",
                result.get("playlist"),
                device_id,
            )

            return {
                "action": "play_playlist",
                "playlist_id": matched_playlist_id,
                "device_id": device_id,
                "result": result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to play playlist: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _handle_chart_command(text: str, device_id: str | None) -> dict:
        """处理排行榜命令
        
        Args:
            text: 命令文本
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        platform_hint, chart_keyword = MusicService.parse_chart_command(text)
        plat = platform_hint or config.MUSIC_DEFAULT_PLATFORM
        _log.info(
            "VoiceCommand: chart intent detected, platform=%s keyword=%r",
            plat,
            chart_keyword,
        )

        try:
            # 获取排行榜列表
            charts_data = await MusicService.get_ranks(plat)
            chart_list: list[dict] = charts_data.get("data", {}).get("list", []) or []

            if not chart_list:
                raise HTTPException(
                    status_code=404, detail=f"平台 {plat} 没有可用的排行榜"
                )

            # 查找匹配的排行榜
            matched_chart = MusicService.find_chart(chart_list, chart_keyword or "")
            if not matched_chart:
                raise HTTPException(
                    status_code=404,
                    detail=f"找不到排行榜: {chart_keyword}",
                )

            rank_id = str(matched_chart.get("id", ""))
            chart_name = matched_chart.get("name", "")

            # 获取排行榜歌曲
            _log.info("Loading songs from chart: %s (id=%s)", chart_name, rank_id)
            songs_data = await MusicService.get_rank_songs(rank_id, plat, page=1, limit=50)
            songs_raw: list[dict] = songs_data.get("data", {}).get("list", []) or []
            
            if not songs_raw:
                raise HTTPException(status_code=404, detail=f"排行榜 {chart_name} 没有歌曲")

            # 创建临时播放列表
            temp_playlist_id = f"temp_chart_{plat}_{rank_id}_{int(datetime.now().timestamp())}"
            playlist = PlaylistService.create_playlist(
                CreatePlaylistRequest(
                    name=f"{chart_name}（{plat}）",
                    type="chart",
                    description=f"临时排行榜播放列表",
                )
            )
            temp_playlist_id = playlist.id

            # 转换歌曲为 PlaylistItem
            items = []
            for s in songs_raw:
                try:
                    items.append(
                        PlaylistItem(
                            title=str(s.get("name", "")),
                            artist=str(s.get("singer", "")),
                            album=s.get("meta", {}).get("albumName", ""),
                            audio_id=str(s.get("id", "")),
                            url=None,  # 需要动态获取
                            duration=_parse_duration(s.get("interval", 0)),
                            cover_url=s.get("meta", {}).get("picUrl", ""),
                            custom_params={"type": "music", "platform": plat, "song_id": str(s.get("id", ""))},
                        )
                    )
                except Exception as e:
                    _log.warning("Failed to parse song: %s", e)
                    continue

            if not items:
                raise HTTPException(status_code=404, detail="无法解析排行榜歌曲")

            # 添加歌曲到播放列表
            PlaylistService.add_items(temp_playlist_id, AddItemRequest(items=items))

            # 通过 playlist_service 播放
            result = await PlaylistService.play_playlist(
                temp_playlist_id,
                PlayPlaylistRequest(device_id=device_id, start_index=0, announce=True)
            )

            return {
                "action": "play_chart",
                "chart_name": chart_name,
                "platform": plat,
                "device_id": device_id,
                "playlist_id": temp_playlist_id,
                "result": result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to load chart: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _handle_search_command(search_query: str, device_id: str | None) -> dict:
        """处理搜索命令
        
        Args:
            search_query: 搜索关键词
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        _log.info("VoiceCommand: search intent detected, query=%r", search_query)

        try:
            plat = config.MUSIC_DEFAULT_PLATFORM

            # 搜索音乐
            search_data = await MusicService.search_music(search_query, plat, page=1, limit=50)
            songs_raw: list[dict] = search_data.get("data", {}).get("list", []) or []
            
            if not songs_raw:
                raise HTTPException(status_code=404, detail=f"没有找到歌曲: {search_query}")

            # 创建临时播放列表
            temp_playlist_id = f"temp_search_{search_query}_{int(datetime.now().timestamp())}"
            playlist = PlaylistService.create_playlist(
                CreatePlaylistRequest(
                    name=f"搜索: {search_query}",
                    type="search",
                    description=f"临时搜索结果播放列表",
                )
            )
            temp_playlist_id = playlist.id

            # 转换歌曲为 PlaylistItem
            items = []
            for s in songs_raw:
                try:
                    items.append(
                        PlaylistItem(
                            title=str(s.get("name", "")),
                            artist=str(s.get("singer", "")),
                            album=s.get("meta", {}).get("albumName", ""),
                            audio_id=str(s.get("id", "")),
                            url=None,  # 需要动态获取
                            duration=_parse_duration(s.get("interval", 0)),
                            cover_url=s.get("meta", {}).get("picUrl", ""),
                            custom_params={"type": "music", "platform": plat, "song_id": str(s.get("id", ""))},
                        )
                    )
                except Exception as e:
                    _log.warning("Failed to parse song: %s", e)
                    continue

            if not items:
                raise HTTPException(status_code=404, detail="无法解析搜索结果")

            # 添加歌曲到播放列表
            PlaylistService.add_items(temp_playlist_id, AddItemRequest(items=items))

            # 通过 playlist_service 播放
            result = await PlaylistService.play_playlist(
                temp_playlist_id,
                PlayPlaylistRequest(device_id=device_id, start_index=0, announce=True)
            )

            return {
                "action": "search_and_play",
                "query": search_query,
                "device_id": device_id,
                "playlist_id": temp_playlist_id,
                "result": result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to search and play: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _relay_raw_command(text: str, device_id: str | None) -> dict:
        """转发原始命令给音箱
        
        Args:
            text: 命令文本
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        _log.info("VoiceCommand: relaying raw command %r", text)
        try:
            client = get_client_sync()
            result = await client.send_command(text, device_id)
            return {"action": "command", "command": text, "result": result}
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def announce_search_results(
        query: str, count: int, device_id: str | None = None
    ) -> dict:
        """向音箱发送TTS，播报搜索结果数量
        
        Args:
            query: 搜索关键词
            count: 搜索结果数量
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        if count <= 0:
            raise HTTPException(status_code=422, detail="count must be > 0")
        
        tts_text = f"搜索到{count}首{query}的歌曲，是否播放？"
        _log.info("AnnounceSearch: TTS %r", tts_text)
        
        try:
            client = get_client_sync()
            result = await client.text_to_speech(tts_text, device_id)
            return {"tts": tts_text, "result": result}
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _handle_play_mode_command(mode: str, device_id: str | None) -> dict:
        """处理播放模式设置命令
        
        Args:
            mode: 播放模式 (loop/single/random)
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        current_playlist_id = VoiceCommandService._get_current_playlist_id(device_id)
        
        if not current_playlist_id:
            raise HTTPException(status_code=404, detail="当前没有播放中的播单")
        
        try:
            playlist = PlaylistService.set_play_mode(
                current_playlist_id,
                PlayModeRequest(play_mode=mode)
            )
            
            mode_names = {"loop": "列表循环", "single": "单曲循环", "random": "随机播放"}
            mode_name = mode_names.get(mode, mode)
            
            # 播报模式变更
            await VoiceCommandService._announce_tts(f"已切换到{mode_name}模式", device_id)
            
            return {
                "action": "set_play_mode",
                "playlist_id": current_playlist_id,
                "play_mode": mode,
                "mode_name": mode_name,
            }
        except Exception as e:
            _log.error("Failed to set play mode: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _handle_continue_command(device_id: str | None) -> dict:
        """处理继续播放命令
        
        Args:
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        current_playlist_id = VoiceCommandService._get_current_playlist_id(device_id)
        
        if not current_playlist_id:
            raise HTTPException(status_code=404, detail="当前没有播放中的播单")
        
        try:
            result = await PlaylistService.continue_playlist(
                current_playlist_id,
                ContinuePlayRequest(device_id=device_id, announce=True)
            )
            return {
                "action": "continue_playlist",
                "playlist_id": current_playlist_id,
                "result": result,
            }
        except Exception as e:
            _log.error("Failed to continue playlist: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _handle_stop_command(device_id: str | None) -> dict:
        """处理停止播放命令
        
        Args:
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        _log.info("处理停止播放命令，设备: %s", device_id)
        
        current_playlist_id = VoiceCommandService._get_current_playlist_id(device_id)
        
        _log.info("当前播单ID: %s", current_playlist_id)
        
        if not current_playlist_id:
            # 如果没有播单，直接停止播放器
            _log.info("没有播单，直接停止播放器")
            client = get_client_sync()
            await client.player_stop(device_id)
            
            # 通知播放控制器
            controller = get_controller()
            await controller.on_play_stopped(device_id)
            
            return {"action": "stop", "message": "已停止播放"}
        
        try:
            _log.info("通过 PlaylistService 停止播单: %s", current_playlist_id)
            result = await PlaylistService.stop_playlist(current_playlist_id, device_id)
            return {
                "action": "stop_playlist",
                "playlist_id": current_playlist_id,
                "result": result,
            }
        except Exception as e:
            _log.error("Failed to stop playlist: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))

    @staticmethod
    async def _handle_next_command(device_id: str | None) -> dict:
        """处理下一首命令
        
        Args:
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        current_playlist_id = VoiceCommandService._get_current_playlist_id(device_id)
        
        if not current_playlist_id:
            raise HTTPException(status_code=404, detail="当前没有播放中的播单")
        
        try:
            result = await PlaylistService.play_next_in_playlist(current_playlist_id, device_id)
            return {
                "action": "play_next",
                "playlist_id": current_playlist_id,
                "result": result,
            }
        except Exception as e:
            _log.error("Failed to play next: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=str(e))
