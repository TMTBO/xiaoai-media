#!/bin/bash
# Docker Volumes 挂载检查脚本

set -e

echo "======================================"
echo "Docker Volumes 挂载检查"
echo "======================================"
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 docker-compose 是否运行
echo "1. 检查容器状态..."
if docker-compose ps | grep -q "xiaoai-media.*Up"; then
    echo -e "${GREEN}✓${NC} 容器正在运行"
else
    echo -e "${RED}✗${NC} 容器未运行"
    echo "  请先启动容器: docker-compose up -d"
    exit 1
fi
echo

# 检查宿主机上的源目录
echo "2. 检查宿主机源目录..."
SOURCE_DIR="/mnt/NAS/audiobooks"
if [ -d "$SOURCE_DIR" ]; then
    echo -e "${GREEN}✓${NC} 源目录存在: $SOURCE_DIR"
    
    # 检查权限
    if [ -r "$SOURCE_DIR" ]; then
        echo -e "${GREEN}✓${NC} 目录可读"
    else
        echo -e "${RED}✗${NC} 目录不可读"
    fi
    
    # 统计文件数量
    FILE_COUNT=$(find "$SOURCE_DIR" -type f 2>/dev/null | wc -l)
    echo "  包含文件数: $FILE_COUNT"
    
    # 显示一些示例文件
    echo "  示例文件:"
    find "$SOURCE_DIR" -type f -name "*.mp3" -o -name "*.m4a" -o -name "*.flac" 2>/dev/null | head -3 | while read file; do
        echo "    - $(basename "$file")"
    done
else
    echo -e "${RED}✗${NC} 源目录不存在: $SOURCE_DIR"
    echo "  请检查 NAS 是否已挂载"
fi
echo

# 检查 docker-compose.yml 配置
echo "3. 检查 docker-compose.yml 配置..."
if grep -q "/mnt/NAS/audiobooks:/data/audiobooks" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} volumes 配置已添加"
    echo "  配置内容:"
    grep -A 5 "volumes:" docker-compose.yml | grep audiobooks
else
    echo -e "${YELLOW}!${NC} volumes 配置未找到"
    echo "  请在 docker-compose.yml 中添加:"
    echo "    - /mnt/NAS/audiobooks:/data/audiobooks"
fi
echo

# 检查容器内的挂载
echo "4. 检查容器内的挂载..."
if docker-compose exec -T xiaoai-media test -d /data/audiobooks; then
    echo -e "${GREEN}✓${NC} 容器内目录存在: /data/audiobooks"
    
    # 检查容器内的文件
    FILE_COUNT=$(docker-compose exec -T xiaoai-media sh -c "find /data/audiobooks -type f 2>/dev/null | wc -l")
    echo "  容器内文件数: $FILE_COUNT"
    
    # 检查权限
    PERMS=$(docker-compose exec -T xiaoai-media stat -c "%a" /data/audiobooks 2>/dev/null || echo "unknown")
    echo "  目录权限: $PERMS"
    
    # 尝试列出文件
    echo "  示例文件:"
    docker-compose exec -T xiaoai-media sh -c "find /data/audiobooks -type f \( -name '*.mp3' -o -name '*.m4a' -o -name '*.flac' \) 2>/dev/null | head -3" | while read file; do
        echo "    - $(basename "$file")"
    done
else
    echo -e "${RED}✗${NC} 容器内目录不存在: /data/audiobooks"
    echo "  可能需要重启容器: docker-compose restart"
fi
echo

# 运行调试脚本
echo "5. 运行详细诊断..."
if [ -f "debug_volumes.py" ]; then
    echo "执行 debug_volumes.py..."
    docker-compose exec -T xiaoai-media python debug_volumes.py
else
    echo -e "${YELLOW}!${NC} debug_volumes.py 不存在，跳过详细诊断"
fi
echo

# 总结和建议
echo "======================================"
echo "检查完成"
echo "======================================"
echo
echo "如果发现问题，请尝试以下步骤:"
echo "1. 确保 NAS 已正确挂载到宿主机"
echo "2. 检查 docker-compose.yml 中的 volumes 配置"
echo "3. 重启容器: docker-compose restart"
echo "4. 查看容器日志: docker-compose logs -f"
echo
echo "详细文档: docs/deployment/DOCKER_VOLUMES_GUIDE.md"
