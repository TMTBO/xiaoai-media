#!/usr/bin/env python3
"""
播单数据迁移脚本

将旧的单文件播单格式 (playlists.json) 迁移到新的多文件格式：
- playlists/index.json: 播单索引
- playlists/{playlist_id}.json: 各个播单的详细数据
"""

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_log = logging.getLogger(__name__)


def get_data_dir() -> Path:
    """获取数据目录"""
    return Path.home()


def migrate_playlists():
    """执行播单迁移"""
    data_dir = get_data_dir()
    old_file = data_dir / "playlists.json"
    new_dir = data_dir / "playlists"
    index_file = new_dir / "index.json"

    # 检查旧文件是否存在
    if not old_file.exists():
        _log.info("未找到旧的播单文件 %s，无需迁移", old_file)
        return

    # 检查新目录是否已存在
    if new_dir.exists() and index_file.exists():
        _log.warning("新的播单目录 %s 已存在，跳过迁移", new_dir)
        _log.info("如需重新迁移，请先删除 %s 目录", new_dir)
        return

    _log.info("开始迁移播单数据...")
    _log.info("旧文件: %s", old_file)
    _log.info("新目录: %s", new_dir)

    try:
        # 读取旧文件
        with open(old_file, "r", encoding="utf-8") as f:
            old_data = json.load(f)

        _log.info("找到 %d 个播单", len(old_data))

        # 创建新目录
        new_dir.mkdir(parents=True, exist_ok=True)

        # 构建索引和分离数据
        index = {}
        migrated_count = 0

        for playlist_id, playlist_data in old_data.items():
            # 提取索引信息
            index_info = {
                "id": playlist_data.get("id", playlist_id),
                "name": playlist_data.get("name", ""),
                "type": playlist_data.get("type", ""),
                "description": playlist_data.get("description", ""),
                "voice_keywords": playlist_data.get("voice_keywords", []),
                "item_count": len(playlist_data.get("items", [])),
                "created_at": playlist_data.get("created_at", ""),
                "updated_at": playlist_data.get("updated_at", ""),
            }
            index[playlist_id] = index_info

            # 提取播单项数据（精简版）
            items = []
            for item in playlist_data.get("items", []):
                # 只保留必要字段
                simplified_item = {
                    "title": item.get("title", ""),
                    "artist": item.get("artist", ""),
                    "album": item.get("album", ""),
                    "audio_id": item.get("audio_id", ""),
                    "url": item.get("url"),
                    "custom_params": item.get("custom_params", {}),
                }
                items.append(simplified_item)

            # 保存播单数据文件
            data_file = new_dir / f"{playlist_id}.json"
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)

            migrated_count += 1
            _log.info("  迁移播单: %s (%d 项)", index_info["name"], len(items))

        # 保存索引文件
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        _log.info("迁移完成！共迁移 %d 个播单", migrated_count)
        _log.info("索引文件: %s", index_file)

        # 备份旧文件
        backup_file = old_file.with_suffix(".json.backup")
        old_file.rename(backup_file)
        _log.info("旧文件已备份到: %s", backup_file)

    except Exception as e:
        _log.error("迁移失败: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    migrate_playlists()
