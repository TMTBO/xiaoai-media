"""
播单数据模型
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlaylistItem(BaseModel):
    """播单项（单个音频/视频）- 精简版，只保留必要信息"""

    title: str = Field(..., description="歌曲名")
    artist: str = Field("", description="艺术家")
    album: str = Field("", description="专辑名")
    audio_id: str = Field("", description="音频ID（如果有）")
    url: str | None = Field(
        None,
        description="音频URL，如果为空则需要通过 audio_id 或 custom_params 动态获取",
    )
    duration: int = Field(0, description="音频时长（秒）")
    cover_url: str = Field("", description="封面图片URL")
    custom_params: dict[str, Any] = Field(
        default_factory=dict,
        description="自定义参数，用于调用 user_config.py 中的 get_audio_url 函数",
    )


class PlaylistIndex(BaseModel):
    """播单索引信息（存储在 index.json 中）"""

    id: str = Field(..., description="播单唯一标识")
    name: str = Field(..., description="播单名称，例如：音乐、有声书、播客")
    type: str = Field("", description="播单类型，例如：music, audiobook, podcast")
    description: str = Field("", description="播单描述")
    voice_keywords: list[str] = Field(
        default_factory=list,
        description="语音识别关键词，用于语音命令控制",
    )
    item_count: int = Field(0, description="播单项数量")
    created_at: str = ""
    updated_at: str = ""
    play_mode: str = Field(
        "loop",
        description="播放模式：loop(列表循环), single(单曲循环), random(随机播放)",
    )
    current_index: int = Field(0, description="当前播放的索引位置")


class Playlist(BaseModel):
    """播单完整信息（包含索引信息和播单项）"""

    id: str = Field(..., description="播单唯一标识")
    name: str = Field(..., description="播单名称，例如：音乐、有声书、播客")
    type: str = Field("", description="播单类型，例如：music, audiobook, podcast")
    description: str = Field("", description="播单描述")
    items: list[PlaylistItem] = Field(default_factory=list, description="播单项列表")
    voice_keywords: list[str] = Field(
        default_factory=list,
        description="语音识别关键词，用于语音命令控制",
    )
    created_at: str = ""
    updated_at: str = ""
    play_mode: str = Field(
        "loop",
        description="播放模式：loop(列表循环), single(单曲循环), random(随机播放)",
    )
    current_index: int = Field(0, description="当前播放的索引位置")


class CreatePlaylistRequest(BaseModel):
    """创建播单请求"""

    name: str
    type: str = ""
    description: str = ""
    voice_keywords: list[str] = []


class UpdatePlaylistRequest(BaseModel):
    """更新播单请求"""

    name: str | None = None
    type: str | None = None
    description: str | None = None
    voice_keywords: list[str] | None = None
    play_mode: str | None = None
    current_index: int | None = None


class AddItemRequest(BaseModel):
    """添加播单项请求"""

    items: list[PlaylistItem]


class PlayPlaylistRequest(BaseModel):
    """播放播单请求"""

    device_id: str | None = None
    start_index: int = Field(0, description="从第几首开始播放（从 0 开始）")
    announce: bool = Field(True, description="是否语音播报")


class PlayModeRequest(BaseModel):
    """设置播放模式请求"""

    play_mode: str = Field(
        ..., description="播放模式：loop(列表循环), single(单曲循环), random(随机播放)"
    )


class ContinuePlayRequest(BaseModel):
    """继续播放请求"""

    device_id: str | None = None
    announce: bool = Field(True, description="是否语音播报")


class ImportFromDirectoryRequest(BaseModel):
    """从目录或文件批量导入请求"""

    directory: str | None = Field(
        None, description="要导入的目录路径（与 files 二选一）"
    )
    files: list[str] | None = Field(
        None, description="要导入的文件路径列表（与 directory 二选一）"
    )
    recursive: bool = Field(False, description="是否递归扫描子目录（仅目录模式有效）")
    file_extensions: list[str] = Field(
        default_factory=lambda: [".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac"],
        description="要导入的文件扩展名列表（仅目录模式有效）",
    )
