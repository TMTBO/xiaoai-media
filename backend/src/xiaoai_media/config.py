from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Callable

# 延迟导入 logger，避免循环依赖
def _get_logger():
    from xiaoai_media.logger import get_logger
    return get_logger()

# 数据存储根目录（向后兼容，建议使用 get_data_dir() 方法）
DATA_DIR = Path.home()

# 配置变更回调函数列表
_config_change_callbacks: list[Callable[[], None]] = []


def get_data_dir() -> Path:
    """获取数据存储根目录

    直接使用 HOME 目录作为数据目录
    - 开发环境：通过 HOME=. 设置，解析为项目根目录
    - Docker 环境：HOME=/data，解析为 /data

    Returns:
        数据目录路径
    """
    return Path.home()


def get_config_file_path(required: bool = False) -> Path | None:
    """获取用户配置文件路径（公共接口）

    查找 $HOME/user_config.py
    - 开发环境：通过 HOME=. 设置，查找项目根目录的 user_config.py
    - Docker 环境：HOME=/data，查找 /data/user_config.py

    Args:
        required: 如果为 True，则在未找到配置文件时返回默认路径（数据目录），
                 如果为 False，则在未找到时返回 None

    Returns:
        配置文件路径
    """
    data_dir = get_data_dir()
    data_config = data_dir / "user_config.py"
    if data_config.exists():
        return data_config

    # 如果需要路径（用于写入），返回数据目录路径
    if required:
        return data_config

    return None


def _find_config_file() -> Path | None:
    """查找用户配置文件（内部使用，带日志输出）

    Returns:
        配置文件路径，如果都不存在则返回 None
    """
    config_path = get_config_file_path(required=False)

    if config_path:
        _get_logger().info("使用配置文件: %s", config_path)
        return config_path

    data_dir = get_data_dir()
    _get_logger().warning("未找到用户配置文件，将使用默认配置")
    _get_logger().info("配置文件路径: %s (不存在)", data_dir / "user_config.py")
    return None


def _load_user_config() -> Any | None:
    """加载用户配置文件 user_config.py

    Returns:
        用户配置模块，如果不存在则返回 None
    """
    config_path = _find_config_file()

    if config_path is None:
        _get_logger().info("使用默认配置运行")
        return None

    try:
        # 将配置文件所在目录添加到 sys.path 的最前面
        # 这样 user_config.py 可以导入同目录下的 music_provider.py
        config_dir = str(config_path.parent.resolve())
        if config_dir not in sys.path:
            sys.path.insert(0, config_dir)
            _get_logger().debug("已将配置目录添加到 sys.path: %s", config_dir)
        
        spec = importlib.util.spec_from_file_location("user_config", config_path)
        if spec and spec.loader:
            user_config = importlib.util.module_from_spec(spec)
            sys.modules["user_config"] = user_config
            spec.loader.exec_module(user_config)
            _get_logger().info("成功加载用户配置文件: %s", config_path)
            return user_config
    except Exception as e:
        _get_logger().error("加载用户配置文件失败: %s", e, exc_info=True)
        _get_logger().warning("将使用默认配置继续运行")
        return None

    return None


# 加载用户配置
_user_config = _load_user_config()


def register_config_change_callback(callback: Callable[[], None]) -> None:
    """注册配置变更回调函数
    
    当配置重新加载时，会调用所有注册的回调函数
    
    Args:
        callback: 配置变更时要调用的回调函数
    """
    if callback not in _config_change_callbacks:
        _config_change_callbacks.append(callback)
        _get_logger().debug("已注册配置变更回调: %s", callback.__name__)


def unregister_config_change_callback(callback: Callable[[], None]) -> None:
    """取消注册配置变更回调函数
    
    Args:
        callback: 要取消注册的回调函数
    """
    if callback in _config_change_callbacks:
        _config_change_callbacks.remove(callback)
        _get_logger().debug("已取消注册配置变更回调: %s", callback.__name__)


def reload_config() -> None:
    """重新加载配置并通知所有监听者
    
    此函数会：
    1. 重新加载用户配置文件
    2. 更新所有配置变量
    3. 调用所有注册的回调函数
    """
    global _user_config
    global MI_USER, MI_PASS, MI_DID, MI_REGION
    global MUSIC_API_BASE_URL, MUSIC_DEFAULT_PLATFORM
    global SERVER_BASE_URL
    global ENABLE_CONVERSATION_POLLING, CONVERSATION_POLL_INTERVAL
    global WAKE_WORDS, ENABLE_WAKE_WORD_FILTER
    global LOG_LEVEL
    global PROXY_SKIP_AUTH_FOR_LAN, PROXY_LAN_NETWORKS
    
    _get_logger().info("开始重新加载配置...")
    
    # 重新加载用户配置
    _user_config = _load_user_config()
    
    # 更新所有配置变量
    MI_USER = _get_config("MI_USER", "")
    MI_PASS = _get_config("MI_PASS", "")
    MI_DID = _get_config("MI_DID", "")
    MI_REGION = _get_config("MI_REGION", "cn")
    
    MUSIC_API_BASE_URL = _get_config("MUSIC_API_BASE_URL", "http://localhost:5050")
    MUSIC_DEFAULT_PLATFORM = _get_config("MUSIC_DEFAULT_PLATFORM", "tx")
    
    SERVER_BASE_URL = _get_config("SERVER_BASE_URL", "http://localhost:8000")
    
    ENABLE_CONVERSATION_POLLING = _get_config("ENABLE_CONVERSATION_POLLING", True)
    CONVERSATION_POLL_INTERVAL = _get_config("CONVERSATION_POLL_INTERVAL", 2.0)
    
    WAKE_WORDS = _get_config("WAKE_WORDS", [])
    ENABLE_WAKE_WORD_FILTER = _get_config("ENABLE_WAKE_WORD_FILTER", True)
    
    PROXY_SKIP_AUTH_FOR_LAN = _get_config("PROXY_SKIP_AUTH_FOR_LAN", True)
    PROXY_LAN_NETWORKS = _get_config("PROXY_LAN_NETWORKS", [
        "192.168.0.0/16",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "127.0.0.0/8",
    ])
    
    LOG_LEVEL = _get_config("LOG_LEVEL", "INFO")
    
    _get_logger().info("配置已重新加载")
    
    # 通知所有监听者
    for callback in _config_change_callbacks:
        try:
            callback()
            _get_logger().debug("已调用配置变更回调: %s", callback.__name__)
        except Exception as e:
            _get_logger().error("配置变更回调执行失败 (%s): %s", callback.__name__, e, exc_info=True)


def _get_config(key: str, default: Any = "") -> Any:
    """获取配置值

    Args:
        key: 配置键名
        default: 默认值

    Returns:
        配置值
    """
    if _user_config is not None and hasattr(_user_config, key):
        value = getattr(_user_config, key)
        return value

    return default


# ============================================
# 小米账号配置
# ============================================

MI_USER: str = _get_config("MI_USER", "")
MI_PASS: str = _get_config("MI_PASS", "")
MI_DID: str = _get_config("MI_DID", "")
MI_REGION: str = _get_config("MI_REGION", "cn")

# ============================================
# 音乐服务配置
# ============================================

MUSIC_API_BASE_URL: str = _get_config("MUSIC_API_BASE_URL", "http://localhost:5050")
MUSIC_DEFAULT_PLATFORM: str = _get_config("MUSIC_DEFAULT_PLATFORM", "tx")

# ============================================
# 本服务配置
# ============================================

# 本服务的基础 URL，用于生成代理链接
# 注意：必须使用音箱可访问的局域网 IP，不能使用 localhost
SERVER_BASE_URL: str = _get_config("SERVER_BASE_URL", "http://localhost:8000")

# ============================================
# 对话监听配置
# ============================================

ENABLE_CONVERSATION_POLLING: bool = _get_config("ENABLE_CONVERSATION_POLLING", True)
CONVERSATION_POLL_INTERVAL: float = _get_config("CONVERSATION_POLL_INTERVAL", 2.0)

# ============================================
# 唤醒词配置
# ============================================

WAKE_WORDS: list[str] = _get_config("WAKE_WORDS", [])
ENABLE_WAKE_WORD_FILTER: bool = _get_config("ENABLE_WAKE_WORD_FILTER", True)

# ============================================
# 代理访问控制配置
# ============================================

# 局域网访问是否跳过身份校验
PROXY_SKIP_AUTH_FOR_LAN: bool = _get_config("PROXY_SKIP_AUTH_FOR_LAN", True)

# 局域网 IP 段配置（CIDR 格式）
PROXY_LAN_NETWORKS: list[str] = _get_config("PROXY_LAN_NETWORKS", [
    "192.168.0.0/16",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "127.0.0.0/8",
])


# ============================================
# 日志配置
# ============================================

LOG_LEVEL: str = _get_config("LOG_LEVEL", "INFO")

# ============================================
# 自定义处理函数
# ============================================


def should_handle_command(query: str) -> bool:
    """判断是否应该处理该指令

    Args:
        query: 用户的语音指令文本

    Returns:
        True 表示应该处理，False 表示忽略
    """
    # 如果用户配置了自定义函数，使用用户的函数
    if _user_config is not None and hasattr(_user_config, "should_handle_command"):
        try:
            return _user_config.should_handle_command(query)
        except Exception as e:
            _get_logger().error("用户自定义 should_handle_command 函数执行失败: %s", e)
            # 失败时使用默认逻辑

    # 默认逻辑：检查唤醒词
    if not ENABLE_WAKE_WORD_FILTER:
        return True

    if not WAKE_WORDS:
        return True

    # 检查是否以任何唤醒词开头
    for wake_word in WAKE_WORDS:
        if query.startswith(wake_word):
            return True

    return False


def preprocess_command(query: str) -> str:
    """预处理指令文本

    Args:
        query: 原始指令文本

    Returns:
        处理后的指令文本
    """
    # 如果用户配置了自定义函数，使用用户的函数
    if _user_config is not None and hasattr(_user_config, "preprocess_command"):
        try:
            return _user_config.preprocess_command(query)
        except Exception as e:
            _get_logger().error("用户自定义 preprocess_command 函数执行失败: %s", e)
            # 失败时使用默认逻辑

    # 默认逻辑：移除开头的唤醒词
    processed = query
    for wake_word in WAKE_WORDS:
        if processed.startswith(wake_word):
            processed = processed[len(wake_word):]
            break  # 只移除第一个匹配的唤醒词

    return processed.strip()


# ============================================
# 日志配置
# ============================================

LOG_LEVEL: str = _get_config("LOG_LEVEL", "INFO")
