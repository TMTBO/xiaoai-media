"""
统一的日志管理模块

提供全局的 logger 实例，所有模块都应该使用这个 logger。
这样可以统一管理日志级别和配置。
"""

import logging
from typing import Optional

# 全局 logger 实例
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """获取全局 logger 实例

    Returns:
        全局 logger 实例
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger("xiaoai_media")
    return _logger


def set_log_level(level: str) -> None:
    """设置日志级别

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger()
    logger.setLevel(level.upper())

    # 同时更新所有子 logger
    for name in logging.root.manager.loggerDict:
        if name.startswith("xiaoai_media"):
            logging.getLogger(name).setLevel(level.upper())


def get_log_level() -> str:
    """获取当前日志级别

    Returns:
        当前日志级别名称
    """
    logger = get_logger()
    return logging.getLevelName(logger.level)


# 导出便捷函数
def debug(msg: str, *args, **kwargs):
    """记录 DEBUG 级别日志"""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """记录 INFO 级别日志"""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """记录 WARNING 级别日志"""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """记录 ERROR 级别日志"""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """记录 CRITICAL 级别日志"""
    get_logger().critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """记录异常信息"""
    get_logger().exception(msg, *args, **kwargs)
