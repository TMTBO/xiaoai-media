"""服务层模块

将业务逻辑从API路由中分离，提供可复用的服务组件。
"""

from .music_service import MusicService
from .config_service import ConfigService
from .playlist_loader import PlaylistLoaderService, SongItem, SongQuality, SongMeta
from .voice_command_service import VoiceCommandService
from .playlist_service import PlaylistService
from .playlist_models import (
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    CreatePlaylistRequest,
    UpdatePlaylistRequest,
    AddItemRequest,
    PlayPlaylistRequest,
    PlayModeRequest,
    ContinuePlayRequest,
)
from .playlist_storage import PlaylistStorage
from .state_service import StateService, get_state_service

__all__ = [
    "MusicService",
    "ConfigService",
    "PlaylistLoaderService",
    "VoiceCommandService",
    "SongItem",
    "SongQuality",
    "SongMeta",
    "PlaylistService",
    "Playlist",
    "PlaylistIndex",
    "PlaylistItem",
    "CreatePlaylistRequest",
    "UpdatePlaylistRequest",
    "AddItemRequest",
    "PlayPlaylistRequest",
    "PlayModeRequest",
    "ContinuePlayRequest",
    "PlaylistStorage",
    "StateService",
    "get_state_service",
]
