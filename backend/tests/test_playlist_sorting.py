"""测试播放列表文件排序功能"""
import pytest
from xiaoai_media.services.playlist_service import PlaylistService


class TestPlaylistSorting:
    """测试自然排序功能"""
    
    def test_natural_sort_key_basic(self):
        """测试基本的自然排序键生成"""
        # 纯数字
        key1 = PlaylistService._natural_sort_key("1")
        key10 = PlaylistService._natural_sort_key("10")
        key2 = PlaylistService._natural_sort_key("2")
        
        # 验证 1 < 2 < 10
        assert key1 < key2 < key10
    
    def test_natural_sort_key_with_text(self):
        """测试带文本的自然排序"""
        key1 = PlaylistService._natural_sort_key("Chapter 1")
        key2 = PlaylistService._natural_sort_key("Chapter 2")
        key10 = PlaylistService._natural_sort_key("Chapter 10")
        
        # 验证正确的排序顺序
        assert key1 < key2 < key10
    
    def test_natural_sort_key_chinese(self):
        """测试中文章节"""
        key1 = PlaylistService._natural_sort_key("第1章")
        key2 = PlaylistService._natural_sort_key("第2章")
        key10 = PlaylistService._natural_sort_key("第10章")
        
        assert key1 < key2 < key10
    
    def test_natural_sort_key_leading_zeros(self):
        """测试前导零"""
        key001 = PlaylistService._natural_sort_key("001")
        key010 = PlaylistService._natural_sort_key("010")
        key100 = PlaylistService._natural_sort_key("100")
        
        # 前导零会被忽略，按数值排序
        assert key001 < key010 < key100
    
    def test_natural_sort_key_mixed_format(self):
        """测试混合格式"""
        key1 = PlaylistService._natural_sort_key("001-标题.mp3")
        key2 = PlaylistService._natural_sort_key("002-标题.mp3")
        key10 = PlaylistService._natural_sort_key("010-标题.mp3")
        
        assert key1 < key2 < key10
    
    def test_natural_sort_key_episode(self):
        """测试 Episode 格式"""
        key1 = PlaylistService._natural_sort_key("Episode 1")
        key5 = PlaylistService._natural_sort_key("Episode 5")
        key10 = PlaylistService._natural_sort_key("Episode 10")
        
        assert key1 < key5 < key10
    
    def test_natural_sort_real_world_example(self):
        """测试真实世界的例子（Moby Dick）"""
        filenames = [
            "Chapter 010",
            "Chapter 001-002",
            "Chapter 003",
            "Chapter 004-007",
            "Chapter 000: Etymology and Extracts",
        ]
        
        # 生成排序键并排序
        items = [(name, PlaylistService._natural_sort_key(name)) for name in filenames]
        items.sort(key=lambda x: x[1])
        
        # 验证排序结果
        sorted_names = [item[0] for item in items]
        assert sorted_names == [
            "Chapter 000: Etymology and Extracts",
            "Chapter 001-002",
            "Chapter 003",
            "Chapter 004-007",
            "Chapter 010",
        ]
    
    def test_natural_sort_complex_example(self):
        """测试复杂的排序场景"""
        filenames = [
            "第10章.mp3",
            "第2章.mp3",
            "第1章.mp3",
            "第20章.mp3",
            "Chapter 5.mp3",
            "001.mp3",
        ]
        
        items = [(name, PlaylistService._natural_sort_key(name)) for name in filenames]
        items.sort(key=lambda x: x[1])
        
        sorted_names = [item[0] for item in items]
        
        # 验证排序：001 < Chapter 5 < 第1章 < 第2章 < 第10章 < 第20章
        assert sorted_names[0] == "001.mp3"
        assert sorted_names[1] == "Chapter 5.mp3"
        assert sorted_names[2] == "第1章.mp3"
        assert sorted_names[3] == "第2章.mp3"
        assert sorted_names[4] == "第10章.mp3"
        assert sorted_names[5] == "第20章.mp3"
    
    def test_should_sort_files(self):
        """测试是否应该排序"""
        # 音乐类型不排序
        assert not PlaylistService._should_sort_files("music")
        assert not PlaylistService._should_sort_files("")
        
        # 其他类型需要排序
        assert PlaylistService._should_sort_files("audiobook")
        assert PlaylistService._should_sort_files("podcast")
        assert PlaylistService._should_sort_files("radio_drama")
        assert PlaylistService._should_sort_files("other")
    
    def test_natural_sort_case_insensitive(self):
        """测试大小写不敏感"""
        key_lower = PlaylistService._natural_sort_key("chapter 1")
        key_upper = PlaylistService._natural_sort_key("CHAPTER 1")
        key_mixed = PlaylistService._natural_sort_key("Chapter 1")
        
        # 所有变体应该生成相同的键
        assert key_lower == key_upper == key_mixed
    
    def test_natural_sort_multiple_numbers(self):
        """测试包含多个数字的文件名"""
        key1 = PlaylistService._natural_sort_key("Book 1 Chapter 5")
        key2 = PlaylistService._natural_sort_key("Book 1 Chapter 10")
        key3 = PlaylistService._natural_sort_key("Book 2 Chapter 1")
        
        # Book 1 Chapter 5 < Book 1 Chapter 10 < Book 2 Chapter 1
        assert key1 < key2 < key3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
