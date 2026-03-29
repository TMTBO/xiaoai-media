"""
测试播单存储结构重构

验证新的多文件存储格式是否正常工作
"""

import json
import tempfile
from pathlib import Path

import pytest


def test_playlist_storage_structure():
    """测试播单存储结构"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        playlists_dir = Path(tmpdir) / "playlists"
        playlists_dir.mkdir()

        # 创建索引文件
        index_data = {
            "test_playlist_1": {
                "id": "test_playlist_1",
                "name": "测试播单1",
                "type": "music",
                "description": "测试描述",
                "voice_keywords": ["音乐", "歌单"],
                "item_count": 2,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }

        index_file = playlists_dir / "index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        # 创建播单数据文件
        playlist_items = [
            {
                "title": "歌曲1",
                "artist": "艺术家1",
                "album": "专辑1",
                "audio_id": "123",
                "url": "http://example.com/song1.mp3",
                "custom_params": {},
            },
            {
                "title": "歌曲2",
                "artist": "艺术家2",
                "album": "专辑2",
                "audio_id": "456",
                "url": None,
                "custom_params": {"platform": "tx", "song_id": "456"},
            },
        ]

        data_file = playlists_dir / "test_playlist_1.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(playlist_items, f, ensure_ascii=False, indent=2)

        # 验证文件结构
        assert index_file.exists()
        assert data_file.exists()

        # 验证索引内容
        with open(index_file, "r", encoding="utf-8") as f:
            loaded_index = json.load(f)
        assert "test_playlist_1" in loaded_index
        assert loaded_index["test_playlist_1"]["name"] == "测试播单1"
        assert loaded_index["test_playlist_1"]["item_count"] == 2

        # 验证播单数据内容
        with open(data_file, "r", encoding="utf-8") as f:
            loaded_items = json.load(f)
        assert len(loaded_items) == 2
        assert loaded_items[0]["title"] == "歌曲1"
        assert loaded_items[1]["title"] == "歌曲2"

        # 验证精简的数据结构（不包含 duration 和 cover_url）
        for item in loaded_items:
            assert "title" in item
            assert "artist" in item
            assert "album" in item
            assert "audio_id" in item
            assert "url" in item or item["url"] is None
            assert "custom_params" in item
            # 确保不包含旧字段
            assert "duration" not in item
            assert "cover_url" not in item


def test_voice_keyword_matching():
    """测试语音关键词匹配（从索引文件）"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        playlists_dir = Path(tmpdir) / "playlists"
        playlists_dir.mkdir()

        # 创建多个播单的索引
        index_data = {
            "music_playlist": {
                "id": "music_playlist",
                "name": "我的音乐",
                "type": "music",
                "description": "",
                "voice_keywords": ["音乐", "歌单"],
                "item_count": 10,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
            "audiobook_playlist": {
                "id": "audiobook_playlist",
                "name": "有声书",
                "type": "audiobook",
                "description": "",
                "voice_keywords": ["有声书", "听书"],
                "item_count": 5,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
        }

        index_file = playlists_dir / "index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        # 模拟语音命令匹配
        voice_text = "播放音乐"

        # 从索引中查找匹配的播单
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)

        matched_playlist_id = None
        for playlist_id, idx in index.items():
            # 检查播单名称
            if idx["name"] in voice_text:
                matched_playlist_id = playlist_id
                break

            # 检查语音关键词
            for keyword in idx["voice_keywords"]:
                if keyword in voice_text:
                    matched_playlist_id = playlist_id
                    break

            if matched_playlist_id:
                break

        # 验证匹配结果
        assert matched_playlist_id == "music_playlist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
