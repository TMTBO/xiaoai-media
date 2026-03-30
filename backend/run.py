#!/usr/bin/env python3
"""
启动脚本，使用动态日志配置启动uvicorn
"""
import os
import sys
import logging.config
import uvicorn
from xiaoai_media.log_config import get_log_config


if __name__ == "__main__":
    # 获取日志配置
    log_config = get_log_config()
    
    # 获取启动配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # 配置 reload 排除项
    # 排除 user_config.py 和数据目录，因为这些文件的变更由配置热重载机制处理
    reload_excludes = None
    if reload:
        reload_excludes = [
            "user_config.py",
            ".xiaoai_media/*",
            "*.json",
            ".mi.token",
        ]
    
    # 启动uvicorn，传递日志配置
    uvicorn.run(
        "xiaoai_media.api.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_excludes=reload_excludes,
        log_config=log_config,
        timeout_graceful_shutdown=2,
        timeout_keep_alive=5,
    )
