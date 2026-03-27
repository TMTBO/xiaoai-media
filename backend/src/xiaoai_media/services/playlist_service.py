"""
播单业务逻辑服务
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from xiaoai_media import config
from xiaoai_media.api.dependencies import get_client_sync
from xiaoai_media.services.playlist_models import (
    AddItemRequest,
    ContinuePlayRequest,
    CreatePlaylistRequest,
    PlayModeRequest,
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    PlayPlaylistRequest,
    UpdatePlaylistRequest,
)
from xiaoai_media.services.playlist_storage import PlaylistStorage

_log = logging.getLogger(__name__)


class PlaylistService:
    """播单业务逻辑服务"""
    
    # 章节目录识别的正则表达式模式
    # 用于识别目录名中的章节信息，支持多种命名格式
    CHAPTER_PATTERNS = [
        r'第\s*(\d+)\s*章',      # 第01章、第 1 章
        r'chapter\s*(\d+)',      # Chapter 1、Chapter01
        r'stage[\-_\s]*(\d+)',   # stage-02、stage_02、stage 02、stage02
        r'episode[\-_\s]*(\d+)', # episode-02、episode_02、episode 02
        r'ep[\-_\s]*(\d+)',      # ep-02、ep_02、ep 02
        r'^(\d+)\s*章',          # 01章、1 章
        r'^(\d+)[_\-\s]',        # 01-、01_、01 开头
        r'^(\d+)$',              # 纯数字目录名
    ]

    @staticmethod
    def _is_chapter_directory(dir_name: str) -> bool:
        """检查目录名是否包含章节信息
        
        Args:
            dir_name: 目录名称
            
        Returns:
            是否为章节目录
        """
        import re
        
        for pattern in PlaylistService.CHAPTER_PATTERNS:
            if re.search(pattern, dir_name.lower()):
                return True
        return False
    
    @staticmethod
    def _extract_chapter_number(dir_name: str) -> int | float:
        """从目录名中提取章节号
        
        Args:
            dir_name: 目录名称
            
        Returns:
            章节号（整数），如果没有找到则返回 float('inf')
        """
        import re
        
        for pattern in PlaylistService.CHAPTER_PATTERNS:
            match = re.search(pattern, dir_name.lower())
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return float('inf')  # 没有章节号，排在最后

    @staticmethod
    def generate_playlist_id(name: str) -> str:
        """生成播单 ID"""
        timestamp = str(int(time.time() * 1000))
        return f"{name[:10]}_{timestamp}"

    @staticmethod
    def make_proxy_url(original_url: str) -> str:
        """将原始 URL 转换为代理 URL
        
        如果 URL 已经是本地 URL（192.168.x.x 或 localhost），则直接返回，
        避免嵌套代理导致的延迟。
        """
        # 检查是否已经是本地 URL
        if any(host in original_url for host in ['192.168.', '127.0.0.1', 'localhost', '10.0.', '172.16.']):
            _log.debug("URL is already local, skipping proxy: %s", original_url[:100])
            return original_url
        
        # 检查是否已经是我们自己的代理 URL
        if '/api/proxy/stream' in original_url:
            _log.debug("URL is already proxied, skipping: %s", original_url[:100])
            return original_url
        
        proxy_url = f"{config.SERVER_BASE_URL}/api/proxy/stream?url={quote(original_url)}"
        _log.debug("Converted URL to proxy: %s -> %s", original_url[:100], proxy_url[:100])
        return proxy_url

    @staticmethod
    async def get_item_url(item: PlaylistItem) -> str:
        """获取播单项的播放 URL

        如果 item.url 存在，直接使用；
        否则调用 user_config.py 中的 get_audio_url 函数获取。
        """
        if item.url:
            return PlaylistService.make_proxy_url(item.url)

        # 尝试从 user_config.py 加载 get_audio_url 函数
        user_config_path = config.get_config_file_path(required=False)
        if not user_config_path or not user_config_path.exists():
            raise RuntimeError(
                "user_config.py not found, cannot get audio URL for item without URL"
            )

        # 动态导入 user_config
        spec = importlib.util.spec_from_file_location("user_config", user_config_path)
        if not spec or not spec.loader:
            raise RuntimeError("Failed to load user_config.py")

        user_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_config)

        # 检查是否有 get_audio_url 函数
        if not hasattr(user_config, "get_audio_url"):
            raise RuntimeError("get_audio_url function not found in user_config.py")

        get_audio_url = user_config.get_audio_url

        # 构建完整的参数字典
        # 注意：custom_params 中的值会覆盖 PlaylistItem 的基础字段
        # 这样可以确保 get_audio_url 接收到正确的字段名（如 id, name, singer）
        params = {
            "title": item.title,
            "artist": item.artist,
            "album": item.album,
            "audio_id": item.audio_id,
            **item.custom_params,  # custom_params 中的值会覆盖上面的默认值
        }

        _log.info("Calling get_audio_url with params: %s", {k: v for k, v in params.items() if k not in ['qualities', 'meta']})

        # 调用函数获取 URL
        if asyncio.iscoroutinefunction(get_audio_url):
            url = await get_audio_url(params)
        else:
            url = get_audio_url(params)

        if not url:
            raise RuntimeError(f"Failed to get audio URL for item: {item.title}")

        return PlaylistService.make_proxy_url(url)

    @staticmethod
    def list_playlists() -> dict[str, list[PlaylistIndex]]:
        """获取所有播单（仅返回索引信息）"""
        index = PlaylistStorage.load_index()
        return {
            "playlists": list(index.values()),
            "total": len(index),
        }

    @staticmethod
    def create_playlist(req: CreatePlaylistRequest) -> Playlist:
        """创建新播单"""
        playlist_id = PlaylistService.generate_playlist_id(req.name)
        now = datetime.now().isoformat()

        playlist = Playlist(
            id=playlist_id,
            name=req.name,
            type=req.type,
            description=req.description,
            voice_keywords=req.voice_keywords,
            items=[],
            created_at=now,
            updated_at=now,
        )

        PlaylistStorage.save_playlist(playlist)
        _log.info("Created playlist: %s (id=%s)", req.name, playlist_id)
        return playlist

    @staticmethod
    def get_playlist(playlist_id: str) -> Playlist | None:
        """获取指定播单（包含完整数据）"""
        return PlaylistStorage.load_playlist(playlist_id)

    @staticmethod
    def update_playlist(playlist_id: str, req: UpdatePlaylistRequest) -> Playlist:
        """更新播单信息"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if req.name is not None:
            playlist.name = req.name
        if req.type is not None:
            playlist.type = req.type
        if req.description is not None:
            playlist.description = req.description
        if req.voice_keywords is not None:
            playlist.voice_keywords = req.voice_keywords
        if req.play_mode is not None:
            if req.play_mode not in ["loop", "single", "random"]:
                raise ValueError(f"Invalid play_mode: {req.play_mode}")
            playlist.play_mode = req.play_mode
        if req.current_index is not None:
            if req.current_index < 0 or req.current_index >= len(playlist.items):
                raise ValueError(f"Invalid current_index: {req.current_index}")
            playlist.current_index = req.current_index

        playlist.updated_at = datetime.now().isoformat()
        PlaylistStorage.save_playlist(playlist)

        _log.info("Updated playlist: %s", playlist_id)
        return playlist

    @staticmethod
    def delete_playlist(playlist_id: str) -> None:
        """删除播单"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        PlaylistStorage.delete_playlist(playlist_id)
        _log.info("Deleted playlist: %s", playlist_id)

    @staticmethod
    def add_items(playlist_id: str, req: AddItemRequest) -> None:
        """添加播单项"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        playlist.items.extend(req.items)
        playlist.updated_at = datetime.now().isoformat()

        PlaylistStorage.save_playlist(playlist)
        _log.info("Added %d items to playlist: %s", len(req.items), playlist_id)

    @staticmethod
    def delete_item(playlist_id: str, item_index: int) -> PlaylistItem:
        """删除播单项"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if item_index < 0 or item_index >= len(playlist.items):
            raise ValueError(f"Item index out of range: {item_index}")

        removed_item = playlist.items.pop(item_index)
        playlist.updated_at = datetime.now().isoformat()

        PlaylistStorage.save_playlist(playlist)
        _log.info("Removed item %d from playlist: %s", item_index, playlist_id)
        return removed_item

    @staticmethod
    async def play_playlist(playlist_id: str, req: PlayPlaylistRequest) -> dict:
        """播放播单"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if not playlist.items:
            raise ValueError("Playlist is empty")

        if req.start_index < 0 or req.start_index >= len(playlist.items):
            raise ValueError(f"Invalid start_index: {req.start_index}")

        # 更新当前播放索引
        playlist.current_index = req.start_index
        playlist.updated_at = datetime.now().isoformat()
        PlaylistStorage.save_playlist(playlist)

        # 保存当前播放的播单ID到状态服务
        from xiaoai_media.services.state_service import get_state_service
        state_service = get_state_service()
        state_service.set(f"current_playlist_{req.device_id or 'default'}", playlist_id)

        # 获取要播放的项
        item = playlist.items[req.start_index]

        # 获取播放 URL
        play_url = await PlaylistService.get_item_url(item)

        _log.info(
            "Playing playlist item: %s - %s (url=%s)",
            playlist.name,
            item.title,
            play_url[:100],
        )

        # 发送播放命令
        client = get_client_sync()
        # 如果需要播报，先播报
        if req.announce:
            announce_text = f"正在播放{playlist.name}，{item.title}"
            if item.artist:
                announce_text += f"，{item.artist}"
            await client.text_to_speech(announce_text, req.device_id)
            await asyncio.sleep(1)  # 等待播报完成

        # 直接使用 play_url 播放
        result = await client.play_url(play_url, req.device_id, _type=1)
        _log.info("Play URL result: %s", result)

        # 启动播放监控器（如果已启用）
        from xiaoai_media import config as app_config
        if app_config.ENABLE_PLAYBACK_MONITOR:
            from xiaoai_media.playback_monitor import get_monitor
            monitor = get_monitor()
            if not monitor.running:
                await monitor.start()
                _log.info("播放监控器已自动启动")
            
            # 立即触发一次状态检查和推送
            try:
                # 等待一小段时间让设备开始播放
                await asyncio.sleep(0.5)
                
                # 获取当前播放状态
                status_result = await client.player_get_status(req.device_id)
                status_data = status_result.get("status", {})
                data = status_data.get("data", {})
                info_str = data.get("info", "{}")
                
                try:
                    import json
                    info = json.loads(info_str)
                except (json.JSONDecodeError, TypeError):
                    info = {}
                
                # 提取播放状态
                status_code = info.get("status", 0)
                play_status = {0: "stopped", 1: "playing", 2: "paused"}.get(status_code, "unknown")
                play_song_detail = info.get("play_song_detail", {})
                
                # 构建状态信息
                new_status = {
                    "status": play_status,
                    "audio_id": play_song_detail.get("audio_id", ""),
                    "position": play_song_detail.get("position", 0),
                    "duration": play_song_detail.get("duration", 0),
                    "media_type": info.get("media_type", 0),
                }
                
                # 立即通知状态变化
                await monitor._notify_status_change(req.device_id or "default", new_status)
                _log.info("已立即推送播放状态: %s", new_status)
            except Exception as e:
                _log.warning("立即推送播放状态失败: %s", e)

        return {
            "message": "Playing",
            "playlist": playlist.name,
            "item": item.model_dump(),
            "index": req.start_index,
            "total": len(playlist.items),
            "play_mode": playlist.play_mode,
        }

    @staticmethod
    async def continue_playlist(playlist_id: str, req: ContinuePlayRequest) -> dict:
        """继续播放播单（从当前索引位置开始）"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if not playlist.items:
            raise ValueError("Playlist is empty")

        # 从当前索引开始播放
        return await PlaylistService.play_playlist(
            playlist_id,
            PlayPlaylistRequest(
                device_id=req.device_id,
                start_index=playlist.current_index,
                announce=req.announce,
            ),
        )

    @staticmethod
    async def stop_playlist(playlist_id: str, device_id: str | None = None) -> dict:
        """停止播放播单"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        # 发送停止命令
        client = get_client_sync()
        await client.player_stop(device_id)

        # 清除播放状态
        from xiaoai_media.services.state_service import get_state_service
        state_service = get_state_service()
        state_service.set(f"current_playlist_{device_id or 'default'}", None)

        _log.info("Stopped playlist: %s", playlist.name)
        return {
            "message": "Stopped",
            "playlist": playlist.name,
        }

    @staticmethod
    def set_play_mode(playlist_id: str, req: PlayModeRequest) -> Playlist:
        """设置播放模式"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if req.play_mode not in ["loop", "single", "random"]:
            raise ValueError(f"Invalid play_mode: {req.play_mode}")

        playlist.play_mode = req.play_mode
        playlist.updated_at = datetime.now().isoformat()
        PlaylistStorage.save_playlist(playlist)

        _log.info("Set play mode for playlist %s: %s", playlist.name, req.play_mode)
        return playlist

    @staticmethod
    async def play_next_in_playlist(playlist_id: str, device_id: str | None = None) -> dict:
        """播放播单中的下一首（根据播放模式）"""
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")

        if not playlist.items:
            raise ValueError("Playlist is empty")

        # 根据播放模式计算下一首的索引
        if playlist.play_mode == "single":
            # 单曲循环：保持当前索引
            next_index = playlist.current_index
        elif playlist.play_mode == "random":
            # 随机播放：随机选择一首
            next_index = random.randint(0, len(playlist.items) - 1)
        else:  # loop
            # 列表循环：下一首，到末尾后回到开头
            next_index = (playlist.current_index + 1) % len(playlist.items)

        return await PlaylistService.play_playlist(
            playlist_id,
            PlayPlaylistRequest(device_id=device_id, start_index=next_index, announce=False),
        )

    @staticmethod
    async def play_by_voice_command(voice_text: str, device_id: str | None = None) -> dict:
        """根据语音命令播放播单

        从索引文件中匹配唤醒词，然后加载对应的播单
        """
        # 从索引文件中查找匹配的播单
        index = PlaylistStorage.load_index()
        matched_playlist_id: str | None = None

        for playlist_id, idx in index.items():
            # 检查播单名称是否在语音文本中
            if idx.name in voice_text:
                matched_playlist_id = playlist_id
                break

            # 检查语音关键词
            for keyword in idx.voice_keywords:
                if keyword in voice_text:
                    matched_playlist_id = playlist_id
                    break

            if matched_playlist_id:
                break

        if not matched_playlist_id:
            raise ValueError(f"No playlist matched for voice command: {voice_text}")

        # 加载完整的播单数据并播放
        return await PlaylistService.play_playlist(
            matched_playlist_id,
            PlayPlaylistRequest(device_id=device_id, start_index=0, announce=True),
        )

    @staticmethod
    def is_docker_environment() -> bool:
        """判断是否在Docker环境中运行"""
        # 检查是否存在 /.dockerenv 文件
        if Path("/.dockerenv").exists():
            return True
        # 检查 HOME 环境变量是否为 /data（Docker配置）
        if Path.home() == Path("/data"):
            return True
        return False

    @staticmethod
    def list_available_directories() -> list[dict[str, str]]:
        """列出可用的目录（主要用于Docker环境）
        
        Returns:
            目录列表，每个目录包含 path 和 name
        """
        is_docker = PlaylistService.is_docker_environment()
        
        if is_docker:
            # Docker环境：列出 /data 下的目录
            base_dir = Path("/data")
            directories = []
            
            # 添加 /data 本身
            directories.append({
                "path": str(base_dir),
                "name": "数据根目录 (/data)",
                "is_docker": True
            })
            
            # 列出 /data 下的子目录
            try:
                for item in sorted(base_dir.iterdir()):
                    if item.is_dir() and not item.name.startswith('.'):
                        # 检查是否为挂载点或包含文件
                        try:
                            # 尝试访问目录以确认可读
                            item.stat()
                            directories.append({
                                "path": str(item),
                                "name": item.name,
                                "is_docker": True
                            })
                        except (PermissionError, OSError) as e:
                            _log.warning("Cannot access directory %s: %s", item, e)
            except Exception as e:
                _log.error("Failed to list directories in /data: %s", e)
            
            return directories
        else:
            # 本地环境：列出常用目录
            directories = []
            home_dir = Path.home()
            
            # 添加用户主目录
            directories.append({
                "path": str(home_dir),
                "name": f"主目录 ({home_dir.name})",
                "is_docker": False
            })
            
            # 添加常用的音乐目录
            common_music_dirs = [
                home_dir / "Music",
                home_dir / "音乐",
                home_dir / "Documents" / "Music",
                home_dir / "Documents" / "音乐",
                home_dir / "Downloads",
                home_dir / "下载",
            ]
            
            for music_dir in common_music_dirs:
                if music_dir.exists() and music_dir.is_dir():
                    directories.append({
                        "path": str(music_dir),
                        "name": music_dir.name,
                        "is_docker": False
                    })
            
            return directories

    @staticmethod
    def browse_directory(path: str | None = None) -> dict[str, any]:
        """浏览指定目录，返回子目录和文件列表
        
        Args:
            path: 目录路径，如果为空则返回根目录列表
            
        Returns:
            包含当前路径、父路径、子目录列表和文件列表的字典
        """
        try:
            if not path:
                # 返回根目录列表
                is_docker = PlaylistService.is_docker_environment()
                
                if is_docker:
                    # Docker环境：从 /data 开始
                    current_path = Path("/data")
                else:
                    # 本地环境：从用户主目录开始
                    current_path = Path.home()
            else:
                current_path = Path(path)
            
            # 验证路径存在且是目录
            if not current_path.exists():
                raise ValueError(f"路径不存在: {path}")
            
            if not current_path.is_dir():
                raise ValueError(f"路径不是目录: {path}")
            
            # 获取父目录
            parent_path = str(current_path.parent) if current_path.parent != current_path else None
            
            # 列出子目录和文件
            subdirectories = []
            files = []
            
            try:
                for item in sorted(current_path.iterdir()):
                    # 跳过隐藏文件和目录
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_dir():
                        try:
                            # 尝试获取目录信息
                            subdirectories.append({
                                "path": str(item),
                                "name": item.name,
                                "is_accessible": True
                            })
                        except PermissionError:
                            # 没有权限访问的目录
                            subdirectories.append({
                                "path": str(item),
                                "name": item.name,
                                "is_accessible": False
                            })
                    elif item.is_file():
                        # 列出所有文件（不仅仅是音频文件）
                        try:
                            files.append({
                                "path": str(item),
                                "name": item.name,
                                "size": item.stat().st_size
                            })
                        except Exception as e:
                            _log.warning("Failed to get file info for %s: %s", item, e)
            except PermissionError:
                _log.warning("No permission to list directory: %s", current_path)
            
            return {
                "current_path": str(current_path),
                "parent_path": parent_path,
                "directories": subdirectories,
                "files": files,
                "total": len(subdirectories) + len(files)
            }
            
        except Exception as e:
            _log.error("Failed to browse directory %s: %s", path, e)
            raise RuntimeError(f"Failed to browse directory: {str(e)}")

    @staticmethod
    def _natural_sort_key(text: str) -> list:
        """
        生成自然排序的键
        
        参考 audiobookshelf 和 ECMAScript Intl.Collator 的实现
        将字符串分解为数字和非数字部分，数字部分转换为整数进行比较
        
        示例:
        - "Chapter 1" -> ["Chapter ", 1]
        - "Chapter 10" -> ["Chapter ", 10]
        - "第01章" -> ["第", 1, "章"]
        - "001-标题" -> [1, "-标题"]
        
        Args:
            text: 要排序的文本
            
        Returns:
            用于排序的键列表，每个元素都是 (类型, 值) 元组以确保可比较性
        """
        import re
        
        # 将字符串分解为数字和非数字部分
        # 使用正则表达式匹配连续的数字或非数字字符
        parts = re.split(r'(\d+)', text.lower())
        
        # 转换数字部分为整数，保留非数字部分为字符串
        # 使用元组 (类型标识, 值) 确保不同类型之间可以比较
        result = []
        for part in parts:
            if part:  # 跳过空字符串
                if part.isdigit():
                    # 数字部分：(0, 整数值)
                    # 类型标识 0 确保数字排在字符串前面
                    result.append((0, int(part)))
                else:
                    # 非数字部分：(1, 字符串值)
                    result.append((1, part))
        
        return result

    @staticmethod
    def _extract_directory_sort_key(file_path: str) -> tuple:
        """
        从文件路径中提取目录排序键
        
        用于多目录导入时，优先按目录名中的章节信息排序
        
        支持的章节格式：
        - 中文：第01章、第 1 章、01章
        - 英文：Chapter 1、Chapter01
        - Stage：stage-02、stage_02、stage 02、stage02
        - Episode：episode-05、episode_05、ep-08、ep_08
        - 纯数字：01、1
        - 前缀数字：01-标题、01_标题
        
        示例:
        - "/data/第01章/001.mp3" -> (1, "第01章", "001.mp3")
        - "/data/Chapter 10/track.mp3" -> (10, "Chapter 10", "track.mp3")
        - "/data/stage-02/audio.mp3" -> (2, "stage-02", "audio.mp3")
        - "/data/episode-05/track.mp3" -> (5, "episode-05", "track.mp3")
        - "/data/音乐/歌曲.mp3" -> (float('inf'), "音乐", "歌曲.mp3")
        
        Args:
            file_path: 文件路径
            
        Returns:
            (目录章节号, 目录名, 文件名) 元组，用于排序
        """
        from pathlib import Path
        
        path = Path(file_path)
        
        # 获取父目录名和文件名
        parent_dir = path.parent.name if path.parent else ""
        file_name = path.name
        
        # 提取章节号
        chapter_num = PlaylistService._extract_chapter_number(parent_dir)
        
        return (chapter_num, parent_dir, file_name)

    @staticmethod
    def _should_sort_files(playlist_type: str) -> bool:
        """判断是否需要对文件进行排序
        
        Args:
            playlist_type: 播单类型
            
        Returns:
            是否需要排序
        """
        # 音乐类型不排序，其他类型（有声书、播客、广播剧等）需要排序
        return playlist_type not in ['music', '']

    @staticmethod
    def import_from_directory(
        playlist_id: str,
        directory: str | None = None,
        files: list[str] | None = None,
        recursive: bool = False,
        file_extensions: list[str] | None = None
    ) -> dict[str, any]:
        """从指定目录或文件列表批量导入音频文件
        
        Args:
            playlist_id: 播单ID
            directory: 目录路径（与 files 二选一）
            files: 文件路径列表（与 directory 二选一）
            recursive: 是否递归扫描子目录（仅目录模式有效）
            file_extensions: 文件扩展名列表，默认为常见音频格式（仅目录模式有效）
            
        Returns:
            导入结果统计
        """
        playlist = PlaylistStorage.load_playlist(playlist_id)
        if playlist is None:
            raise ValueError(f"Playlist not found: {playlist_id}")
        
        # 验证参数
        if not directory and not files:
            raise ValueError("Either directory or files must be provided")
        
        if directory and files:
            raise ValueError("Cannot specify both directory and files")
        
        if file_extensions is None:
            file_extensions = [".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac", ".wma"]
        
        # 规范化扩展名（确保以点开头且小写）
        file_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                          for ext in file_extensions]
        
        # 扫描文件
        imported_items = []
        skipped_files = []
        total_scanned = 0
        
        try:
            # 文件列表模式
            if files:
                file_paths = [Path(f) for f in files]
                total_scanned = len(file_paths)
                
                for file_path in file_paths:
                    if not file_path.exists():
                        _log.warning("File not found: %s", file_path)
                        skipped_files.append(str(file_path))
                        continue
                    
                    if not file_path.is_file():
                        _log.warning("Path is not a file: %s", file_path)
                        skipped_files.append(str(file_path))
                        continue
                    
                    try:
                        item = PlaylistService._create_playlist_item_from_file(file_path)
                        imported_items.append(item)
                        _log.debug("Imported file: %s", file_path)
                    except Exception as e:
                        _log.warning("Failed to import file %s: %s", file_path, e)
                        skipped_files.append(str(file_path))
            
            # 目录模式
            else:
                dir_path = Path(directory)
                if not dir_path.exists():
                    raise ValueError(f"Directory not found: {directory}")
                
                if not dir_path.is_dir():
                    raise ValueError(f"Path is not a directory: {directory}")
                
                if recursive:
                    # 递归扫描
                    file_paths = [f for f in dir_path.rglob("*") if f.is_file()]
                else:
                    # 只扫描当前目录
                    file_paths = [f for f in dir_path.iterdir() if f.is_file()]
                
                total_scanned = len(file_paths)
                
                for file_path in file_paths:
                    # 检查文件扩展名
                    if file_path.suffix.lower() not in file_extensions:
                        continue
                    
                    try:
                        item = PlaylistService._create_playlist_item_from_file(file_path)
                        imported_items.append(item)
                        _log.debug("Imported file: %s", file_path)
                    except Exception as e:
                        _log.warning("Failed to import file %s: %s", file_path, e)
                        skipped_files.append(str(file_path))
            
            # 根据播单类型决定是否排序
            if imported_items and PlaylistService._should_sort_files(playlist.type):
                # 判断是否为多目录导入
                unique_dirs = set()
                for item in imported_items:
                    file_path = item.custom_params.get("file_path", "")
                    if file_path:
                        parent_dir = str(Path(file_path).parent)
                        unique_dirs.add(parent_dir)
                
                is_multi_directory = len(unique_dirs) > 1
                
                if is_multi_directory:
                    # 多目录导入：先按目录章节号排序，再按文件名排序
                    imported_items.sort(key=lambda item: (
                        PlaylistService._extract_directory_sort_key(
                            item.custom_params.get("file_path", "")
                        ),
                        PlaylistService._natural_sort_key(
                            item.custom_params.get("file_name", item.title)
                        )
                    ))
                    _log.info("Sorted %d items from %d directories using directory chapter sort", 
                             len(imported_items), len(unique_dirs))
                else:
                    # 单目录导入：只按文件名排序
                    imported_items.sort(key=lambda item: PlaylistService._natural_sort_key(
                        item.custom_params.get("file_name", item.title)
                    ))
                    _log.info("Sorted %d items using natural sort algorithm", len(imported_items))
            
            # 添加到播单
            if imported_items:
                playlist.items.extend(imported_items)
                playlist.updated_at = datetime.now().isoformat()
                PlaylistStorage.save_playlist(playlist)
                _log.info(
                    "Imported %d files to playlist %s",
                    len(imported_items),
                    playlist_id
                )
            
            return {
                "imported": len(imported_items),
                "skipped": len(skipped_files),
                "total_scanned": total_scanned,
                "skipped_files": skipped_files[:10],  # 只返回前10个失败的文件
                "playlist_total_items": len(playlist.items)
            }
            
        except Exception as e:
            _log.error("Failed to import: %s", e, exc_info=True)
            raise RuntimeError(f"Failed to import: {str(e)}")
    
    @staticmethod
    def _create_playlist_item_from_file(file_path: Path) -> PlaylistItem:
        """从文件路径创建播单项
        
        Args:
            file_path: 文件路径
            
        Returns:
            播单项
        """
        # 文件名作为标题（去除扩展名）
        title = file_path.stem
        
        # 尝试从文件路径提取艺术家和专辑信息
        parts = file_path.parts
        artist = ""
        album = ""
        
        if len(parts) >= 2:
            parent_dir = parts[-2]  # 父目录
            
            # 检查父目录是否是章节目录（包含章节信息）
            is_chapter_dir = PlaylistService._is_chapter_directory(parent_dir)
            
            if is_chapter_dir:
                # 父目录是章节目录，使用它作为专辑
                album = parent_dir
                # 祖父目录作为艺术家（如果存在）
                if len(parts) >= 3:
                    artist = parts[-3]
            else:
                # 父目录不是章节目录，按传统方式处理
                album = parent_dir
                if len(parts) >= 3:
                    artist = parts[-3]
        
        # 获取文件大小（如果文件存在）
        try:
            file_size = file_path.stat().st_size
        except (FileNotFoundError, OSError):
            file_size = 0
        
        # 创建播单项
        # 使用文件的绝对路径作为URL
        return PlaylistItem(
            title=title,
            artist=artist,
            album=album,
            url=f"file://{file_path.absolute()}",
            audio_id="",
            custom_params={
                "file_path": str(file_path.absolute()),
                "file_size": file_size,
                "file_extension": file_path.suffix,
                "file_name": file_path.name  # 保存完整文件名用于排序
            }
        )
