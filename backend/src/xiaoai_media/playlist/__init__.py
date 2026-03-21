"""
播单管理模块 - 兼容层

此模块已迁移到 services 层，这里保留作为向后兼容的导入别名。
建议直接从 xiaoai_media.services 导入。
"""

import warnings

# 发出弃用警告
warnings.warn(
    "xiaoai_media.playlist module is deprecated. "
    "Please import from xiaoai_media.services instead.",
    DeprecationWarning,
    stacklevel=2,
)

# 从新位置导入，保持向后兼容
from xiaoai_media.services import (
    AddItemRequest,
    CreatePlaylistRequest,
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    PlaylistService,
    PlayPlaylistRequest,
    UpdatePlaylistRequest,
)

__all__ = [
    "PlaylistService",
    "Playlist",
    "PlaylistIndex",
    "PlaylistItem",
    "CreatePlaylistRequest",
    "UpdatePlaylistRequest",
    "AddItemRequest",
    "PlayPlaylistRequest",
]
