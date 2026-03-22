from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# 数据存储根目录（向后兼容，建议使用 get_data_dir() 方法）
DATA_DIR = Path.home()


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
        _log.info("使用配置文件: %s", config_path)
        return config_path

    data_dir = get_data_dir()
    _log.warning("未找到用户配置文件，将使用默认配置")
    _log.info("配置文件路径: %s (不存在)", data_dir / "user_config.py")
    return None


def _load_user_config() -> Any | None:
    """加载用户配置文件 user_config.py

    Returns:
        用户配置模块，如果不存在则返回 None
    """
    config_path = _find_config_file()

    if config_path is None:
        _log.info("使用默认配置运行")
        return None

    try:
        spec = importlib.util.spec_from_file_location("user_config", config_path)
        if spec and spec.loader:
            user_config = importlib.util.module_from_spec(spec)
            sys.modules["user_config"] = user_config
            spec.loader.exec_module(user_config)
            _log.info("成功加载用户配置文件: %s", config_path)
            return user_config
    except Exception as e:
        _log.error("加载用户配置文件失败: %s", e, exc_info=True)
        _log.warning("将使用默认配置继续运行")
        return None

    return None


# 加载用户配置
_user_config = _load_user_config()


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
# 播放监控配置
# ============================================

ENABLE_PLAYBACK_MONITOR: bool = _get_config("ENABLE_PLAYBACK_MONITOR", True)
PLAYBACK_MONITOR_INTERVAL: float = _get_config("PLAYBACK_MONITOR_INTERVAL", 3.0)

# ============================================
# 唤醒词配置
# ============================================

WAKE_WORDS: list[str] = _get_config("WAKE_WORDS", [])
ENABLE_WAKE_WORD_FILTER: bool = _get_config("ENABLE_WAKE_WORD_FILTER", True)



# ============================================
# 日志配置
# ============================================

LOG_LEVEL: str = _get_config("LOG_LEVEL", "INFO")
VERBOSE_PLAYBACK_LOG: bool = _get_config("VERBOSE_PLAYBACK_LOG", False)

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
            _log.error("用户自定义 should_handle_command 函数执行失败: %s", e)
            # 失败时使用默认逻辑

    # 默认逻辑：检查唤醒词
    if not ENABLE_WAKE_WORD_FILTER:
        return True

    if not WAKE_WORDS:
        return True

    # 检查是否包含任何唤醒词
    for wake_word in WAKE_WORDS:
        if wake_word in query:
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
            _log.error("用户自定义 preprocess_command 函数执行失败: %s", e)
            # 失败时使用默认逻辑

    # 默认逻辑：移除唤醒词
    processed = query
    for wake_word in WAKE_WORDS:
        processed = processed.replace(wake_word, "")

    return processed.strip()


# ============================================
# 日志配置
# ============================================

LOG_LEVEL: str = _get_config("LOG_LEVEL", "INFO")
VERBOSE_PLAYBACK_LOG: bool = _get_config("VERBOSE_PLAYBACK_LOG", False)
