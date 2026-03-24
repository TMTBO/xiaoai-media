"""语音命令服务

处理自然语言语音命令的解析和执行。
"""

from __future__ import annotations

import logging
import re

from fastapi import HTTPException

from xiaoai_media import config
from xiaoai_media.api.dependencies import get_client_sync
from .music_service import MusicService
from .playlist_loader import PlaylistLoaderService

_log = logging.getLogger(__name__)


class VoiceCommandService:
    """语音命令服务类"""

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
        if "停止播放" in text or "停止" in text:
            return await VoiceCommandService._handle_stop_command(device_id)
        if "下一首" in text:
            return await VoiceCommandService._handle_next_command(device_id)

        # 模式1: 播放列表 - "播放音乐播单", "打开我的有声书"
        if re.search(r"播单|列表|有声书|播客", text):
            return await VoiceCommandService._handle_playlist_command(text, device_id)

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
    async def _handle_playlist_command(text: str, device_id: str | None) -> dict:
        """处理播放列表命令
        
        Args:
            text: 命令文本
            device_id: 设备ID
            
        Returns:
            执行结果
        """
        _log.info("VoiceCommand: playlist intent detected for text=%r", text)
        try:
            # 从命令中提取播放列表名称/关键词
            playlist_keyword = text
            playlist_keyword = re.sub(r"(播单|列表|有声书|播客)\s*$", "", playlist_keyword).strip()

            # 加载播放列表并查找匹配项
            from xiaoai_media.services.playlist_storage import PlaylistStorage

            index = PlaylistStorage.load_index()
            matched_playlist = None

            # 尝试按名称或语音关键词匹配
            for pid, playlist_idx in index.items():
                # 检查播放列表名称是否包含关键词
                if playlist_keyword.lower() in playlist_idx.name.lower():
                    matched_playlist = (pid, playlist_idx)
                    break
                # 检查语音关键词
                for vk in playlist_idx.voice_keywords:
                    if vk.lower() in text.lower():
                        matched_playlist = (pid, playlist_idx)
                        break
                if matched_playlist:
                    break

            if not matched_playlist:
                raise HTTPException(
                    status_code=404,
                    detail=f"找不到匹配的播单: {playlist_keyword}",
                )

            playlist_id, playlist_idx = matched_playlist

            # 加载播放列表
            load_result = await PlaylistLoaderService.load_from_saved_playlist(
                playlist_id=playlist_id,
                device_id=device_id,
                auto_play=True,
            )

            _log.info(
                "VoiceCommand: loaded playlist %r for device %s",
                playlist_idx.name,
                device_id,
            )

            return {
                "action": "play_playlist",
                "playlist_name": playlist_idx.name,
                "playlist_id": playlist_id,
                "device_id": device_id,
                "result": load_result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to load playlist: %s", e, exc_info=True)
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
            # 使用播放列表加载服务
            load_result = await PlaylistLoaderService.load_from_chart(
                chart_keyword=chart_keyword,
                device_id=device_id,
                platform=plat,
                auto_play=True,
            )

            return {
                "action": "play_chart",
                "chart_name": load_result.get("chart_name"),
                "platform": plat,
                "device_id": device_id,
                "result": load_result,
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
            # 使用播放列表加载服务
            load_result = await PlaylistLoaderService.load_from_search(
                query=search_query,
                device_id=device_id,
                auto_play=True,
            )

            return {
                "action": "search_and_play",
                "query": search_query,
                "device_id": device_id,
                "result": load_result,
            }

        except HTTPException:
            raise
        except Exception as e:
            _log.error("Failed to search and load: %s", e, exc_info=True)
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
        from xiaoai_media.services.state_service import get_state_service
        
        # 从状态服务获取当前播放的播单ID
        state_service = get_state_service()
        current_playlist_id = state_service.get(f"current_playlist_{device_id or 'default'}")
        
        if not current_playlist_id:
            raise HTTPException(status_code=404, detail="当前没有播放中的播单")
        
        from xiaoai_media.services.playlist_service import PlaylistService
        from xiaoai_media.services.playlist_models import PlayModeRequest
        
        try:
            playlist = PlaylistService.set_play_mode(
                current_playlist_id,
                PlayModeRequest(play_mode=mode)
            )
            
            mode_names = {"loop": "列表循环", "single": "单曲循环", "random": "随机播放"}
            mode_name = mode_names.get(mode, mode)
            
            # 播报模式变更
            client = get_client_sync()
            await client.text_to_speech(f"已切换到{mode_name}模式", device_id)
            
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
        from xiaoai_media.services.state_service import get_state_service
        
        # 从状态服务获取当前播放的播单ID
        state_service = get_state_service()
        current_playlist_id = state_service.get(f"current_playlist_{device_id or 'default'}")
        
        if not current_playlist_id:
            raise HTTPException(status_code=404, detail="当前没有播放中的播单")
        
        from xiaoai_media.services.playlist_service import PlaylistService
        from xiaoai_media.services.playlist_models import ContinuePlayRequest
        
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
        from xiaoai_media.services.state_service import get_state_service
        
        # 从状态服务获取当前播放的播单ID
        state_service = get_state_service()
        current_playlist_id = state_service.get(f"current_playlist_{device_id or 'default'}")
        
        if not current_playlist_id:
            # 如果没有播单，直接停止播放器
            client = get_client_sync()
            await client.player_stop(device_id)
            return {"action": "stop", "message": "已停止播放"}
        
        from xiaoai_media.services.playlist_service import PlaylistService
        
        try:
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
        from xiaoai_media.services.state_service import get_state_service
        
        # 从状态服务获取当前播放的播单ID
        state_service = get_state_service()
        current_playlist_id = state_service.get(f"current_playlist_{device_id or 'default'}")
        
        if not current_playlist_id:
            raise HTTPException(status_code=404, detail="当前没有播放中的播单")
        
        from xiaoai_media.services.playlist_service import PlaylistService
        
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
