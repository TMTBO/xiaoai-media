"""
测试多目录导入时的排序逻辑
"""

import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend" / "src"))

from xiaoai_media.services.playlist_service import PlaylistService


def test_extract_directory_sort_key():
    """测试从文件路径中提取目录排序键"""
    
    print("测试目录排序键提取...")
    
    # 测试中文章节格式
    key1 = PlaylistService._extract_directory_sort_key("/data/第01章/001.mp3")
    assert key1[0] == 1, f"Expected 1, got {key1[0]}"
    assert key1[1] == "第01章", f"Expected '第01章', got {key1[1]}"
    assert key1[2] == "001.mp3", f"Expected '001.mp3', got {key1[2]}"
    print(f"✓ 中文章节格式: {key1}")
    
    key2 = PlaylistService._extract_directory_sort_key("/data/第10章/track.mp3")
    assert key2[0] == 10, f"Expected 10, got {key2[0]}"
    print(f"✓ 中文章节格式(10): {key2}")
    
    # 测试英文章节格式
    key3 = PlaylistService._extract_directory_sort_key("/data/Chapter 5/audio.mp3")
    assert key3[0] == 5, f"Expected 5, got {key3[0]}"
    print(f"✓ 英文章节格式: {key3}")
    
    key4 = PlaylistService._extract_directory_sort_key("/data/Chapter05/audio.mp3")
    assert key4[0] == 5, f"Expected 5, got {key4[0]}"
    print(f"✓ 英文章节格式(无空格): {key4}")
    
    # 测试 stage 格式
    key_stage1 = PlaylistService._extract_directory_sort_key("/data/stage-02/audio.mp3")
    assert key_stage1[0] == 2, f"Expected 2, got {key_stage1[0]}"
    print(f"✓ stage-02 格式: {key_stage1}")
    
    key_stage2 = PlaylistService._extract_directory_sort_key("/data/stage_10/audio.mp3")
    assert key_stage2[0] == 10, f"Expected 10, got {key_stage2[0]}"
    print(f"✓ stage_10 格式: {key_stage2}")
    
    key_stage3 = PlaylistService._extract_directory_sort_key("/data/stage 03/audio.mp3")
    assert key_stage3[0] == 3, f"Expected 3, got {key_stage3[0]}"
    print(f"✓ stage 03 格式: {key_stage3}")
    
    key_stage4 = PlaylistService._extract_directory_sort_key("/data/stage01/audio.mp3")
    assert key_stage4[0] == 1, f"Expected 1, got {key_stage4[0]}"
    print(f"✓ stage01 格式: {key_stage4}")
    
    # 测试 episode 格式
    key_ep1 = PlaylistService._extract_directory_sort_key("/data/episode-05/audio.mp3")
    assert key_ep1[0] == 5, f"Expected 5, got {key_ep1[0]}"
    print(f"✓ episode-05 格式: {key_ep1}")
    
    key_ep2 = PlaylistService._extract_directory_sort_key("/data/ep-08/audio.mp3")
    assert key_ep2[0] == 8, f"Expected 8, got {key_ep2[0]}"
    print(f"✓ ep-08 格式: {key_ep2}")
    
    # 测试纯数字目录名
    key5 = PlaylistService._extract_directory_sort_key("/data/03/file.mp3")
    assert key5[0] == 3, f"Expected 3, got {key5[0]}"
    print(f"✓ 纯数字目录: {key5}")
    
    # 测试无章节号的目录（应该排在最后）
    key6 = PlaylistService._extract_directory_sort_key("/data/音乐/歌曲.mp3")
    assert key6[0] == float('inf'), f"Expected inf, got {key6[0]}"
    print(f"✓ 无章节号目录: {key6}")
    
    # 验证排序顺序
    keys = [key2, key1, key6, key3, key5, key4, key_stage1, key_stage2, key_ep1]
    sorted_keys = sorted(keys)
    
    print("\n排序结果:")
    for i, key in enumerate(sorted_keys):
        print(f"  {i+1}. 章节号={key[0]}, 目录={key[1]}, 文件={key[2]}")
    
    # 验证排序顺序正确
    assert sorted_keys[0][0] == 1  # 第01章 或 stage01
    assert sorted_keys[1][0] == 2  # stage-02
    assert sorted_keys[2][0] == 3  # 03
    print("✓ 排序顺序正确")


def test_natural_sort_key():
    """测试自然排序键生成"""
    
    print("\n测试自然排序键...")
    
    # 测试数字排序
    key1 = PlaylistService._natural_sort_key("Chapter 1")
    key2 = PlaylistService._natural_sort_key("Chapter 10")
    key3 = PlaylistService._natural_sort_key("Chapter 2")
    
    # Chapter 1 < Chapter 2 < Chapter 10
    assert key1 < key3 < key2, "Chapter 排序错误"
    print(f"✓ Chapter 排序: 1 < 2 < 10")
    
    # 测试中文
    key4 = PlaylistService._natural_sort_key("第01章")
    key5 = PlaylistService._natural_sort_key("第10章")
    key6 = PlaylistService._natural_sort_key("第2章")
    
    # 第01章 < 第2章 < 第10章
    assert key4 < key6 < key5, "中文章节排序错误"
    print(f"✓ 中文章节排序: 01 < 2 < 10")
    
    # 测试文件名
    key7 = PlaylistService._natural_sort_key("001-标题.mp3")
    key8 = PlaylistService._natural_sort_key("010-标题.mp3")
    key9 = PlaylistService._natural_sort_key("002-标题.mp3")
    
    # 001 < 002 < 010
    assert key7 < key9 < key8, "文件名排序错误"
    print(f"✓ 文件名排序: 001 < 002 < 010")


if __name__ == "__main__":
    try:
        test_extract_directory_sort_key()
        test_natural_sort_key()
        print("\n✅ 所有测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

