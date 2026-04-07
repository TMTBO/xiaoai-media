"""
播单存储管理
"""

from __future__ import annotations

import json
from xiaoai_media.logger import get_logger
from pathlib import Path

from xiaoai_media import config
from xiaoai_media.services.playlist_models import Playlist, PlaylistIndex, PlaylistItem

_log = get_logger()


class PlaylistStorage:
    """播单存储管理器"""

    @staticmethod
    def get_playlists_dir() -> Path:
        """获取播单存储目录路径"""
        return config.get_data_dir() / "playlists"

    @staticmethod
    def get_index_file() -> Path:
        """获取播单索引文件路径"""
        return PlaylistStorage.get_playlists_dir() / "index.json"

    @staticmethod
    def get_playlist_data_file(playlist_id: str) -> Path:
        """获取播单详细数据文件路径"""
        return PlaylistStorage.get_playlists_dir() / f"{playlist_id}.json"

    @staticmethod
    def ensure_storage_dir() -> None:
        """确保存储目录存在"""
        storage_dir = PlaylistStorage.get_playlists_dir()
        storage_dir.mkdir(parents=True, exist_ok=True)
        _log.debug("Playlist storage directory: %s", storage_dir)

        # 验证目录是否可写
        test_file = storage_dir / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            _log.error("Storage directory is not writable: %s", e)
            raise RuntimeError(f"Storage directory {storage_dir} is not writable: {e}")

    @staticmethod
    def load_index() -> dict[str, PlaylistIndex]:
        """从索引文件加载所有播单的基本信息"""
        index_file = PlaylistStorage.get_index_file()
        if not index_file.exists():
            return {}

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {pid: PlaylistIndex(**pdata) for pid, pdata in data.items()}
        except Exception as e:
            _log.error("Failed to load playlist index from %s: %s", index_file, e)
            return {}

    @staticmethod
    def save_index(index: dict[str, PlaylistIndex]) -> None:
        """保存播单索引到文件"""
        PlaylistStorage.ensure_storage_dir()
        index_file = PlaylistStorage.get_index_file()

        try:
            data = {pid: idx.model_dump() for pid, idx in index.items()}
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            _log.debug("Saved %d playlist indexes to %s", len(index), index_file)
        except Exception as e:
            _log.error("Failed to save playlist index to %s: %s", index_file, e)
            raise RuntimeError(f"Failed to save playlist index: {e}")

    @staticmethod
    def load_playlist_data(playlist_id: str) -> list[PlaylistItem]:
        """加载播单的详细数据（播单项列表）"""
        data_file = PlaylistStorage.get_playlist_data_file(playlist_id)
        if not data_file.exists():
            return []

        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [PlaylistItem(**item) for item in data]
        except Exception as e:
            _log.error("Failed to load playlist data from %s: %s", data_file, e)
            return []

    @staticmethod
    def save_playlist_data(playlist_id: str, items: list[PlaylistItem]) -> None:
        """保存播单的详细数据到文件"""
        PlaylistStorage.ensure_storage_dir()
        data_file = PlaylistStorage.get_playlist_data_file(playlist_id)

        try:
            data = [item.model_dump() for item in items]
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            _log.debug("Saved %d items to %s", len(items), data_file)
        except Exception as e:
            _log.error("Failed to save playlist data to %s: %s", data_file, e)
            raise RuntimeError(f"Failed to save playlist data: {e}")

    @staticmethod
    def load_playlist(playlist_id: str) -> Playlist | None:
        """加载完整的播单信息（索引 + 详细数据）"""
        index = PlaylistStorage.load_index()
        if playlist_id not in index:
            return None

        idx = index[playlist_id]
        items = PlaylistStorage.load_playlist_data(playlist_id)

        return Playlist(
            id=idx.id,
            name=idx.name,
            type=idx.type,
            description=idx.description,
            voice_keywords=idx.voice_keywords,
            items=items,
            created_at=idx.created_at,
            updated_at=idx.updated_at,
            play_mode=idx.play_mode,
            current_index=idx.current_index,
        )

    @staticmethod
    def save_playlist(playlist: Playlist) -> None:
        """保存完整的播单信息（索引 + 详细数据）"""
        # 保存索引
        index = PlaylistStorage.load_index()
        index[playlist.id] = PlaylistIndex(
            id=playlist.id,
            name=playlist.name,
            type=playlist.type,
            description=playlist.description,
            voice_keywords=playlist.voice_keywords,
            item_count=len(playlist.items),
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
            play_mode=playlist.play_mode,
            current_index=playlist.current_index,
        )
        PlaylistStorage.save_index(index)

        # 保存详细数据
        PlaylistStorage.save_playlist_data(playlist.id, playlist.items)

    @staticmethod
    def delete_playlist(playlist_id: str) -> None:
        """删除播单的所有文件"""
        # 从索引中删除
        index = PlaylistStorage.load_index()
        if playlist_id in index:
            del index[playlist_id]
            PlaylistStorage.save_index(index)

        # 删除数据文件
        data_file = PlaylistStorage.get_playlist_data_file(playlist_id)
        if data_file.exists():
            data_file.unlink()
            _log.info("Deleted playlist data file: %s", data_file)
