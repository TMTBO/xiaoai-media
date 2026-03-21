"""测试数据目录获取功能"""

from pathlib import Path
from xiaoai_media import config


def test_get_data_dir():
    """测试 get_data_dir() 方法"""
    data_dir = config.get_data_dir()
    
    # 应该返回 Path 对象
    assert isinstance(data_dir, Path)
    
    # 应该是 HOME 目录
    assert data_dir == Path.home()
    
    print(f"✓ 数据目录: {data_dir}")


def test_get_config_file_path():
    """测试 get_config_file_path() 方法"""
    # 不要求必须存在
    config_path = config.get_config_file_path(required=False)
    if config_path:
        assert isinstance(config_path, Path)
        assert config_path.name == "user_config.py"
        print(f"✓ 配置文件: {config_path}")
    else:
        print("✓ 配置文件不存在（正常）")
    
    # 要求返回路径（即使不存在）
    config_path_required = config.get_config_file_path(required=True)
    assert isinstance(config_path_required, Path)
    assert config_path_required.name == "user_config.py"
    print(f"✓ 配置文件路径（required=True）: {config_path_required}")


def test_data_dir_with_home_env():
    """测试数据目录使用 HOME 环境变量"""
    data_dir = config.get_data_dir()
    home_dir = Path.home()
    
    # 数据目录应该等于 HOME 目录
    assert data_dir == home_dir
    print(f"✓ 数据目录使用 HOME: {data_dir}")
    
    # 配置文件应该在 HOME 目录下
    config_path = config.get_config_file_path(required=True)
    assert config_path.parent == home_dir
    print(f"✓ 配置文件在 HOME 目录: {config_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("测试数据目录获取功能")
    print("=" * 60)
    
    test_get_data_dir()
    test_get_config_file_path()
    test_data_dir_with_home_env()
    
    print("=" * 60)
    print("所有测试通过！")
    print("=" * 60)
