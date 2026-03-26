#!/usr/bin/env python3
"""
启动脚本，使用动态日志配置启动uvicorn
"""
import os
import sys
import uvicorn
from xiaoai_media.log_config import get_log_config


if __name__ == "__main__":
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # 启动uvicorn
    uvicorn.run(
        "xiaoai_media.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_config=get_log_config(),
    )
