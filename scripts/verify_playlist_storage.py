#!/usr/bin/env python3
"""
验证播单存储结构

检查播单存储是否正常工作
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_log = logging.getLogger(__name__)


def get_data_dir() -> Path:
    """获取数据目录"""
    return Path.home()


def verify_storage():
    """验证播单存储结构"""
    data_dir = get_data_dir()
    playlists_dir = data_dir / "playlists"
    index_file = playlists_dir / "index.json"

    _log.info("数据目录: %s", data_dir)
    _log.info("播单目录: %s", playlists_dir)

    # 检查目录是否存在
    if not playlists_dir.exists():
        _log.warning("播单目录不存在: %s", playlists_dir)
        _log.info("这是正常的，如果你还没有创建任何播单")
        return

    _log.info("✓ 播单目录存在")

    # 检查索引文件
    if not index_file.exists():
        _log.warning("索引文件不存在: %s", index_file)
        _log.info("这是正常的，如果你还没有创建任何播单")
        return

    _log.info("✓ 索引文件存在")

    # 读取索引文件
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)

        _log.info("✓ 索引文件格式正确")
        _log.info("播单数量: %d", len(index))

        # 验证每个播单
        for playlist_id, idx in index.items():
            _log.info("\n播单: %s", idx.get("name", "未命名"))
            _log.info("  ID: %s", playlist_id)
            _log.info("  类型: %s", idx.get("type", ""))
            _log.info("  项目数: %d", idx.get("item_count", 0))
            _log.info("  语音关键词: %s", ", ".join(idx.get("voice_keywords", [])))

            # 检查数据文件
            data_file = playlists_dir / f"{playlist_id}.json"
            if not data_file.exists():
                _log.error("  ✗ 数据文件不存在: %s", data_file)
                continue

            _log.info("  ✓ 数据文件存在")

            # 读取数据文件
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    items = json.load(f)

                _log.info("  ✓ 数据文件格式正确")
                _log.info("  实际项目数: %d", len(items))

                # 验证项目数是否匹配
                if len(items) != idx.get("item_count", 0):
                    _log.warning(
                        "  ⚠ 项目数不匹配: 索引=%d, 实际=%d",
                        idx.get("item_count", 0),
                        len(items),
                    )

                # 验证数据结构
                if items:
                    first_item = items[0]
                    required_fields = ["title", "artist", "album", "audio_id"]
                    missing_fields = [
                        f for f in required_fields if f not in first_item
                    ]

                    if missing_fields:
                        _log.warning(
                            "  ⚠ 缺少必需字段: %s", ", ".join(missing_fields)
                        )
                    else:
                        _log.info("  ✓ 数据结构正确")

                    # 检查是否有旧字段
                    old_fields = ["duration", "cover_url"]
                    found_old_fields = [f for f in old_fields if f in first_item]
                    if found_old_fields:
                        _log.warning(
                            "  ⚠ 发现旧字段（建议迁移）: %s",
                            ", ".join(found_old_fields),
                        )

            except json.JSONDecodeError as e:
                _log.error("  ✗ 数据文件格式错误: %s", e)
            except Exception as e:
                _log.error("  ✗ 读取数据文件失败: %s", e)

        _log.info("\n验证完成！")

    except json.JSONDecodeError as e:
        _log.error("✗ 索引文件格式错误: %s", e)
    except Exception as e:
        _log.error("✗ 读取索引文件失败: %s", e)


if __name__ == "__main__":
    verify_storage()
