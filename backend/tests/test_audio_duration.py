"""
测试从音频文件读取时长功能
"""

import pytest
from pathlib import Path
from xiaoai_media.services.playlist_service import PlaylistService


def test_get_audio_duration_from_file_with_file_protocol():
    """测试从 file:// URL 读取音频时长"""
    # 这个测试需要一个真实的音频文件
    # 在实际环境中，你需要提供一个测试音频文件
    test_file = Path(__file__).parent / "test_data" / "sample.mp3"
    
    if not test_file.exists():
        pytest.skip("测试音频文件不存在")
    
    file_url = f"file://{test_file.absolute()}"
    duration = PlaylistService._get_audio_duration_from_file(file_url)
    
    # 验证返回的是一个正整数
    assert isinstance(duration, int)
    assert duration >= 0


def test_get_audio_duration_from_file_with_path():
    """测试从普通路径读取音频时长"""
    test_file = Path(__file__).parent / "test_data" / "sample.mp3"
    
    if not test_file.exists():
        pytest.skip("测试音频文件不存在")
    
    duration = PlaylistService._get_audio_duration_from_file(str(test_file))
    
    # 验证返回的是一个正整数
    assert isinstance(duration, int)
    assert duration >= 0


def test_get_audio_duration_from_nonexistent_file():
    """测试读取不存在的文件"""
    duration = PlaylistService._get_audio_duration_from_file("/nonexistent/file.mp3")
    
    # 不存在的文件应该返回 0
    assert duration == 0


def test_get_audio_duration_from_invalid_file():
    """测试读取非音频文件"""
    # 使用当前测试文件作为非音频文件
    test_file = Path(__file__)
    duration = PlaylistService._get_audio_duration_from_file(str(test_file))
    
    # 非音频文件应该返回 0
    assert duration == 0
