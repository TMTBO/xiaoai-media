from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# 用户配置文件路径（项目根目录）
_user_config_path = Path(__file__).resolve().parents[3] / "user_config.py"


def _load_user_config() -> Any | None:
    """加载用户配置文件 user_config.py
    
    Returns:
        用户配置模块，如果不存在则返回 None
    """
    if not _user_config_path.exists():
        _log.error("未找到用户配置文件 user_config.py，请创建配置文件")
        _log.error("运行: cp user_config_template.py user_config.py")
        raise FileNotFoundError(
            f"配置文件不存在: {_user_config_path}\n"
            f"请运行: cp user_config_template.py user_config.py"
        )
    
    try:
        spec = importlib.util.spec_from_file_location("user_config", _user_config_path)
        if spec and spec.loader:
            user_config = importlib.util.module_from_spec(spec)
            sys.modules["user_config"] = user_config
            spec.loader.exec_module(user_config)
            _log.info("成功加载用户配置文件: %s", _user_config_path)
            return user_config
    except Exception as e:
        _log.error("加载用户配置文件失败: %s", e, exc_info=True)
        raise
    
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
MI_PASS_TOKEN: str = _get_config("MI_PASS_TOKEN", "")
MI_DID: str = _get_config("MI_DID", "")
MI_REGION: str = _get_config("MI_REGION", "cn")

# ============================================
# 音乐服务配置
# ============================================

MUSIC_API_BASE_URL: str = _get_config("MUSIC_API_BASE_URL", "http://localhost:5050")
MUSIC_DEFAULT_PLATFORM: str = _get_config("MUSIC_DEFAULT_PLATFORM", "tx")

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
