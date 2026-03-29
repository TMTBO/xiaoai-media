"""
测试从文件路径提取艺术家和专辑信息
"""

import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend" / "src"))

from xiaoai_media.services.playlist_service import PlaylistService


def test_chapter_directory_extraction():
    """测试章节目录的艺术家和专辑提取"""
    
    print("测试章节目录的艺术家和专辑提取...")
    
    # 测试 stage 格式
    test_cases = [
        {
            "path": "/data/牛津树1-14阶段PDF+音频/stage-01/A Good Trick.mp3",
            "expected_artist": "牛津树1-14阶段PDF+音频",
            "expected_album": "stage-01",
            "expected_title": "A Good Trick"
        },
        {
            "path": "/data/牛津树1-14阶段PDF+音频/stage-13/Dragon Tales.mp3",
            "expected_artist": "牛津树1-14阶段PDF+音频",
            "expected_album": "stage-13",
            "expected_title": "Dragon Tales"
        },
        {
            "path": "/data/有声书/第01章/001.mp3",
            "expected_artist": "有声书",
            "expected_album": "第01章",
            "expected_title": "001"
        },
        {
            "path": "/data/播客/episode-05/intro.mp3",
            "expected_artist": "播客",
            "expected_album": "episode-05",
            "expected_title": "intro"
        },
        {
            "path": "/data/音乐/Chapter 10/track.mp3",
            "expected_artist": "音乐",
            "expected_album": "Chapter 10",
            "expected_title": "track"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['path']}")
        
        file_path = Path(test_case['path'])
        item = PlaylistService._create_playlist_item_from_file(file_path)
        
        print(f"  标题: {item.title}")
        print(f"  艺术家: {item.artist}")
        print(f"  专辑: {item.album}")
        
        assert item.title == test_case['expected_title'], \
            f"标题错误: 期望 '{test_case['expected_title']}', 实际 '{item.title}'"
        assert item.artist == test_case['expected_artist'], \
            f"艺术家错误: 期望 '{test_case['expected_artist']}', 实际 '{item.artist}'"
        assert item.album == test_case['expected_album'], \
            f"专辑错误: 期望 '{test_case['expected_album']}', 实际 '{item.album}'"
        
        print(f"  ✓ 通过")
    
    print("\n✅ 所有章节目录测试通过！")


def test_traditional_directory_extraction():
    """测试传统目录结构的艺术家和专辑提取"""
    
    print("\n测试传统目录结构的艺术家和专辑提取...")
    
    # 测试传统的 艺术家/专辑/歌曲 结构
    test_cases = [
        {
            "path": "/data/周杰伦/范特西/双截棍.mp3",
            "expected_artist": "周杰伦",
            "expected_album": "范特西",
            "expected_title": "双截棍"
        },
        {
            "path": "/data/Taylor Swift/1989/Shake It Off.mp3",
            "expected_artist": "Taylor Swift",
            "expected_album": "1989",
            "expected_title": "Shake It Off"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['path']}")
        
        file_path = Path(test_case['path'])
        item = PlaylistService._create_playlist_item_from_file(file_path)
        
        print(f"  标题: {item.title}")
        print(f"  艺术家: {item.artist}")
        print(f"  专辑: {item.album}")
        
        assert item.title == test_case['expected_title'], \
            f"标题错误: 期望 '{test_case['expected_title']}', 实际 '{item.title}'"
        assert item.artist == test_case['expected_artist'], \
            f"艺术家错误: 期望 '{test_case['expected_artist']}', 实际 '{item.artist}'"
        assert item.album == test_case['expected_album'], \
            f"专辑错误: 期望 '{test_case['expected_album']}', 实际 '{item.album}'"
        
        print(f"  ✓ 通过")
    
    print("\n✅ 所有传统目录测试通过！")


if __name__ == "__main__":
    try:
        test_chapter_directory_extraction()
        test_traditional_directory_extraction()
        print("\n" + "="*50)
        print("✅ 所有测试通过！")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
