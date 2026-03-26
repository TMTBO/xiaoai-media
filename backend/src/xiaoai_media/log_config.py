"""
日志配置模块
动态生成uvicorn日志配置，支持从环境变量读取日志级别
"""
import os
import sys
import logging


# ANSI颜色代码
class Colors:
    GREY = "\x1b[38;21m"
    BLUE = "\x1b[38;5;39m"
    YELLOW = "\x1b[38;5;226m"
    RED = "\x1b[38;5;196m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    GREEN = "\x1b[38;5;34m"
    CYAN = "\x1b[38;5;51m"


class CustomFormatter(logging.Formatter):
    """自定义格式化器，统一日志格式并添加颜色"""
    
    # 不同日志级别的颜色
    LEVEL_COLORS = {
        logging.DEBUG: Colors.GREY,
        logging.INFO: Colors.BLUE,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BOLD_RED,
    }
    
    def __init__(self, *args, use_colors=None, **kwargs):
        super().__init__(*args, **kwargs)
        # 自动检测是否应该使用颜色
        if use_colors is None:
            # 检查是否是TTY终端
            self.use_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        else:
            self.use_colors = use_colors
    
    def format(self, record):
        # 保存原始levelname
        levelname_orig = record.levelname
        
        if self.use_colors:
            # 添加颜色
            levelname_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
            record.levelname = f"{levelname_color}{record.levelname:<8}{Colors.RESET}"
            
            # 模块名使用青色
            name_orig = record.name
            record.name = f"{Colors.CYAN}{record.name}{Colors.RESET}"
            
            result = super().format(record)
            
            # 恢复原始值
            record.name = name_orig
        else:
            # 不使用颜色，只确保宽度
            record.levelname = f"{record.levelname:<8}"
            result = super().format(record)
        
        # 恢复原始levelname
        record.levelname = levelname_orig
        return result


class AccessFormatter(logging.Formatter):
    """访问日志格式化器，带颜色"""
    
    # HTTP状态码颜色
    STATUS_COLORS = {
        2: Colors.GREEN,   # 2xx - 成功
        3: Colors.CYAN,    # 3xx - 重定向
        4: Colors.YELLOW,  # 4xx - 客户端错误
        5: Colors.RED,     # 5xx - 服务器错误
    }
    
    def __init__(self, *args, use_colors=None, **kwargs):
        super().__init__(*args, **kwargs)
        # 自动检测是否应该使用颜色
        if use_colors is None:
            self.use_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        else:
            self.use_colors = use_colors
    
    def format(self, record):
        # 保存原始levelname
        levelname_orig = record.levelname
        
        # 从record中提取uvicorn的访问日志信息
        if hasattr(record, 'args') and len(record.args) >= 5:
            # uvicorn.access的args格式: (client_addr, method, full_path, http_version, status_code)
            client_addr = record.args[0]
            method = record.args[1]
            full_path = record.args[2]
            http_version = record.args[3]
            status_code = record.args[4]
            
            if self.use_colors:
                # 根据状态码选择颜色
                status_class = status_code // 100
                status_color = self.STATUS_COLORS.get(status_class, Colors.RESET)
                
                # 格式化消息（带颜色）
                record.msg = (
                    f'{Colors.GREY}{client_addr}{Colors.RESET} - '
                    f'"{Colors.CYAN}{method}{Colors.RESET} {full_path} {http_version}" '
                    f'{status_color}{status_code}{Colors.RESET}'
                )
                
                # 日志级别颜色
                record.levelname = f"{Colors.BLUE}{record.levelname:<8}{Colors.RESET}"
                
                # 模块名颜色
                name_orig = record.name
                record.name = f"{Colors.CYAN}{record.name}{Colors.RESET}"
                
                record.args = ()
                result = super().format(record)
                
                # 恢复原始值
                record.name = name_orig
            else:
                # 不使用颜色
                record.msg = f'{client_addr} - "{method} {full_path} {http_version}" {status_code}'
                record.levelname = f"{record.levelname:<8}"
                record.args = ()
                result = super().format(record)
        else:
            # 普通消息，使用CustomFormatter的逻辑
            if self.use_colors:
                record.levelname = f"{Colors.BLUE}{record.levelname:<8}{Colors.RESET}"
                name_orig = record.name
                record.name = f"{Colors.CYAN}{record.name}{Colors.RESET}"
                result = super().format(record)
                record.name = name_orig
            else:
                record.levelname = f"{record.levelname:<8}"
                result = super().format(record)
        
        # 恢复原始levelname
        record.levelname = levelname_orig
        return result


def get_log_config() -> dict:
    """获取日志配置字典"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    # 检查是否禁用颜色
    use_colors = os.getenv("LOG_COLORS", "true").lower() != "false"
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "xiaoai_media.log_config.CustomFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": use_colors,
            },
            "access": {
                "()": "xiaoai_media.log_config.AccessFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": use_colors,
            }
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": log_level,
                "propagate": False
            },
            "watchfiles": {
                "handlers": ["default"],
                "level": "WARNING",  # 只显示WARNING及以上级别，隐藏INFO级别的文件变化通知
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["default"]
        }
    }
