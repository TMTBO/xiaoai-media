#!/bin/sh
set -e

# 修复数据目录权限
# 如果 /data/.xiaoai-media 是挂载卷，确保 appuser 有权限访问
if [ -d "/data/.xiaoai-media" ]; then
    echo "正在检查数据目录权限..."
    
    # 检查是否有权限访问（作为 root 运行此检查）
    if [ "$(id -u)" = "0" ]; then
        # 如果是 root 用户，修复权限
        chown -R appuser:appuser /data/.xiaoai-media || true
        echo "数据目录权限已更新"
    fi
fi

# 如果不是 root，或者已经是 appuser，直接执行命令
if [ "$(id -u)" = "0" ]; then
    # 以 appuser 身份执行应用
    exec su-exec appuser "$@"
else
    exec "$@"
fi
