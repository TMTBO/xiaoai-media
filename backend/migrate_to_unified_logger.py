#!/usr/bin/env python3
"""
迁移脚本：将所有模块的 logger 实例替换为统一的 logger
"""
import re
from pathlib import Path

# 需要更新的文件列表
files_to_update = [
    "src/xiaoai_media/client.py",
    "src/xiaoai_media/command_handler.py",
    "src/xiaoai_media/conversation.py",
    "src/xiaoai_media/playback_monitor.py",
    "src/xiaoai_media/player.py",
    "src/xiaoai_media/scheduler_executor.py",
    "src/xiaoai_media/services/music_service.py",
    "src/xiaoai_media/services/playlist_loader.py",
    "src/xiaoai_media/services/playlist_service.py",
    "src/xiaoai_media/services/playlist_storage.py",
    "src/xiaoai_media/services/scheduler_service.py",
    "src/xiaoai_media/services/state_service.py",
    "src/xiaoai_media/services/voice_command_service.py",
    "src/xiaoai_media/api/routes/music.py",
    "src/xiaoai_media/api/routes/playlist.py",
    "src/xiaoai_media/api/routes/proxy.py",
    "src/xiaoai_media/api/routes/scheduler.py",
    "src/xiaoai_media/api/routes/state.py",
]


def update_file(file_path: Path):
    """更新单个文件"""
    print(f"处理文件: {file_path}")
    
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    
    # 1. 替换 import logging
    if "import logging" in content and "from xiaoai_media.logger import get_logger" not in content:
        # 在 import logging 后添加新的导入
        content = content.replace(
            "import logging",
            "import logging\nfrom xiaoai_media.logger import get_logger"
        )
    
    # 2. 替换 _log = logging.getLogger(__name__)
    content = re.sub(
        r"_log = logging\.getLogger\(__name__\)",
        "_log = get_logger()",
        content
    )
    
    # 3. 替换 logger = logging.getLogger(__name__)
    content = re.sub(
        r"logger = logging\.getLogger\(__name__\)",
        "logger = get_logger()",
        content
    )
    
    # 4. 替换 logging.getLogger(__name__) 的直接使用
    content = re.sub(
        r"logging\.getLogger\(__name__\)",
        "get_logger()",
        content
    )
    
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✓ 已更新")
    else:
        print(f"  - 无需更新")


def main():
    """主函数"""
    print("=" * 60)
    print("迁移到统一 logger")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    for file_path_str in files_to_update:
        file_path = base_dir / file_path_str
        if file_path.exists():
            update_file(file_path)
        else:
            print(f"警告: 文件不存在: {file_path}")
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
