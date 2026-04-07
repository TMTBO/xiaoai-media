"""定时任务执行器

负责执行各种类型的定时任务
"""

from typing import Any

from xiaoai_media.client import get_client_sync
from xiaoai_media.command_handler import CommandHandler
from xiaoai_media.logger import get_logger
from xiaoai_media.services.music_service import MusicService
from xiaoai_media.services.playlist_service import PlaylistService

_log = get_logger()


class SchedulerExecutor:
    """定时任务执行器"""

    def __init__(self):
        """初始化执行器"""
        self.music_service = MusicService()
        self.playlist_service = PlaylistService()
        self.command_handler = CommandHandler()

    async def _get_device_id(self, task_id: str, device_id: str | None) -> str:
        """获取设备ID（如果未指定则使用默认设备）

        Args:
            task_id: 任务ID
            device_id: 指定的设备ID

        Returns:
            设备ID
        """
        if device_id:
            _log.info("任务 %s: 使用指定设备 %s", task_id, device_id)
            return device_id
        else:
            client = get_client_sync()
            # 使用 client 的 _resolve_device_id 方法获取默认设备
            default_device_id = await client._resolve_device_id(None)
            _log.debug("任务 %s: 使用默认设备 %s", task_id, default_device_id)
            return default_device_id

    async def execute_play_music(self, task_id: str, params: dict[str, Any]):
        """执行播放音乐任务

        Args:
            task_id: 任务ID
            params: 任务参数
                - song_name: 歌曲名称
                - artist: 歌手名称（可选）
                - device_id: 设备ID（可选，默认使用主设备）
        """
        song_name = params.get("song_name")
        artist = params.get("artist")
        device_id = await self._get_device_id(task_id, params.get("device_id"))

        if not song_name:
            _log.error("任务 %s: 缺少歌曲名称参数", task_id)
            return

        try:
            from xiaoai_media.player import get_player

            client = get_client_sync()
            player = get_player()

            # 搜索歌曲
            search_query = f"{song_name} {artist}" if artist else song_name
            _log.info("任务 %s: 搜索歌曲 '%s'", task_id, search_query)

            result = await self.music_service.search_music(search_query, limit=1)
            songs = result.get("songs", [])

            if not songs:
                _log.warning("任务 %s: 未找到歌曲 '%s'", task_id, search_query)
                # 使用 TTS 提醒用户
                await client.text_to_speech(
                    f"未找到歌曲{song_name}", device_id=device_id
                )
                return

            song = songs[0]
            _log.info(
                "任务 %s: 找到歌曲 '%s - %s'",
                task_id,
                song.get("name"),
                song.get("singer"),
            )

            # 设置播放列表并播放
            player.set_playlist(device_id, songs, current_index=0)
            await player.play_at_index(device_id, 0, stop_first=True)
            _log.info(
                "任务 %s: 开始播放歌曲 '%s' (设备: %s)",
                task_id,
                song.get("name"),
                device_id,
            )

        except Exception as e:
            _log.error("任务 %s: 播放音乐失败: %s", task_id, e, exc_info=True)

    async def execute_play_playlist(self, task_id: str, params: dict[str, Any]):
        """执行播放播放列表任务

        Args:
            task_id: 任务ID
            params: 任务参数
                - playlist_id: 播放列表ID
                - device_id: 设备ID（可选，默认使用主设备）
        """
        from xiaoai_media.services.playlist_models import PlayPlaylistRequest

        playlist_id = params.get("playlist_id")
        device_id = await self._get_device_id(task_id, params.get("device_id"))

        if not playlist_id:
            _log.error("任务 %s: 缺少播放列表ID参数", task_id)
            return

        try:
            client = get_client_sync()

            _log.info("任务 %s: 播放播放列表 '%s'", task_id, playlist_id)

            # 获取播放列表
            playlist = self.playlist_service.get_playlist(playlist_id)

            if not playlist:
                _log.warning("任务 %s: 播放列表 '%s' 不存在", task_id, playlist_id)
                await client.text_to_speech("播放列表不存在", device_id=device_id)
                return

            if not playlist.items:
                _log.warning("任务 %s: 播放列表 '%s' 为空", task_id, playlist_id)
                await client.text_to_speech("播放列表为空", device_id=device_id)
                return

            # 播放播放列表
            play_request = PlayPlaylistRequest(
                device_id=device_id, start_index=0, announce=True
            )
            await self.playlist_service.play_playlist(playlist_id, play_request)
            _log.info(
                "任务 %s: 开始播放播放列表 '%s' (设备: %s)",
                task_id,
                playlist.name,
                device_id,
            )

        except Exception as e:
            _log.error("任务 %s: 播放播放列表失败: %s", task_id, e, exc_info=True)

    async def execute_reminder(self, task_id: str, params: dict[str, Any]):
        """执行提醒任务

        Args:
            task_id: 任务ID
            params: 任务参数
                - message: 提醒内容
                - device_id: 设备ID（可选，默认使用主设备）
        """
        message = params.get("message")
        device_id = await self._get_device_id(task_id, params.get("device_id"))

        if not message:
            _log.error("任务 %s: 缺少提醒内容参数", task_id)
            return

        try:
            client = get_client_sync()

            _log.info("任务 %s: 发送提醒 '%s' (设备: %s)", task_id, message, device_id)

            # 使用 TTS 播报提醒
            await client.text_to_speech(f"提醒：{message}", device_id=device_id)

            _log.info("任务 %s: 提醒已发送", task_id)

        except Exception as e:
            _log.error("任务 %s: 发送提醒失败: %s", task_id, e, exc_info=True)

    async def execute_command(self, task_id: str, params: dict[str, Any]):
        """执行语音指令任务

        Args:
            task_id: 任务ID
            params: 任务参数
                - command: 语音指令文本
                - device_id: 设备ID（可选，默认使用主设备）
        """
        command = params.get("command")
        device_id = await self._get_device_id(task_id, params.get("device_id"))

        if not command:
            _log.error("任务 %s: 缺少指令内容参数", task_id)
            return

        try:
            from xiaoai_media import config

            _log.info("任务 %s: 执行指令 '%s' (设备: %s)", task_id, command, device_id)

            # 检查是否应该本地处理（是否在 wake words 中）
            if config.should_handle_command(command):
                _log.debug("任务 %s: 指令包含唤醒词，本地处理", task_id)
                # 使用 CommandHandler 本地处理指令
                await self.command_handler.handle_command(device_id, command)
            else:
                _log.debug("任务 %s: 指令不包含唤醒词，发送给小爱音箱处理", task_id)
                # 发送给小爱音箱处理
                client = get_client_sync()
                await client.send_command(command, device_id=device_id)

            _log.info("任务 %s: 指令执行完成", task_id)

        except Exception as e:
            _log.error("任务 %s: 执行指令失败: %s", task_id, e, exc_info=True)


# 全局执行器实例
_executor: SchedulerExecutor | None = None


def get_scheduler_executor() -> SchedulerExecutor:
    """获取全局执行器实例

    Returns:
        SchedulerExecutor 实例
    """
    global _executor
    if _executor is None:
        _executor = SchedulerExecutor()
    return _executor
