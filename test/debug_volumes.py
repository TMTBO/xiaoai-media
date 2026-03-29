#!/usr/bin/env python3
"""调试 Docker volumes 挂载的脚本"""

from pathlib import Path
import os

def check_directory(path: Path, indent: int = 0):
    """递归检查目录"""
    prefix = "  " * indent
    try:
        stat = path.stat()
        print(f"{prefix}📁 {path}")
        print(f"{prefix}   权限: {oct(stat.st_mode)[-3:]}")
        print(f"{prefix}   所有者: UID={stat.st_uid}, GID={stat.st_gid}")
        
        # 检查是否为挂载点
        if path != path.parent:
            parent_dev = path.parent.stat().st_dev
            current_dev = stat.st_dev
            if parent_dev != current_dev:
                print(f"{prefix}   ⚠️  这是一个挂载点!")
        
        # 列出子目录
        if path.is_dir():
            try:
                items = list(path.iterdir())
                print(f"{prefix}   包含 {len(items)} 个项目")
                
                # 只显示前几个子目录
                dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
                if dirs:
                    print(f"{prefix}   子目录: {', '.join(d.name for d in dirs[:5])}")
                    if len(dirs) > 5:
                        print(f"{prefix}            ... 还有 {len(dirs) - 5} 个")
                        
            except PermissionError:
                print(f"{prefix}   ❌ 无权限列出内容")
    except Exception as e:
        print(f"{prefix}❌ {path}: {e}")

def main():
    print("=" * 60)
    print("Docker Volumes 挂载检查")
    print("=" * 60)
    
    # 检查环境
    print(f"\n当前用户: {os.getuid()}:{os.getgid()}")
    print(f"HOME: {os.environ.get('HOME', 'not set')}")
    print(f"是否在 Docker 中: {Path('/.dockerenv').exists()}")
    
    # 检查 /data 目录
    print("\n" + "=" * 60)
    print("检查 /data 目录")
    print("=" * 60)
    
    data_dir = Path("/data")
    if data_dir.exists():
        check_directory(data_dir)
        
        print("\n子目录详情:")
        print("-" * 60)
        try:
            for item in sorted(data_dir.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    check_directory(item, indent=1)
                    print()
        except Exception as e:
            print(f"❌ 无法列出 /data 子目录: {e}")
    else:
        print("❌ /data 目录不存在")
    
    # 检查特定的 audiobooks 目录
    print("\n" + "=" * 60)
    print("检查 /data/audiobooks 目录")
    print("=" * 60)
    
    audiobooks_dir = Path("/data/audiobooks")
    if audiobooks_dir.exists():
        check_directory(audiobooks_dir)
        
        # 尝试列出一些文件
        try:
            files = list(audiobooks_dir.glob("**/*.mp3"))[:5]
            if files:
                print(f"\n找到的音频文件示例:")
                for f in files:
                    print(f"  - {f.relative_to(audiobooks_dir)}")
        except Exception as e:
            print(f"❌ 无法搜索音频文件: {e}")
    else:
        print("❌ /data/audiobooks 目录不存在")
        print("\n可能的原因:")
        print("  1. docker-compose.yml 中没有配置 volumes 挂载")
        print("  2. 挂载的源目录不存在")
        print("  3. 容器需要重启以应用新的挂载配置")

if __name__ == "__main__":
    main()
