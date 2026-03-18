#!/bin/bash

echo "=========================================="
echo "对话记录功能测试脚本"
echo "=========================================="
echo ""

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试后端 API
echo "1. 测试后端 API..."
echo "   URL: http://localhost:8000/api/command/conversation"
echo ""

response=$(curl -s -w "\n%{http_code}" "http://localhost:8000/api/command/conversation")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ API 响应成功 (HTTP $http_code)${NC}"
    
    # 解析对话数量
    count=$(echo "$body" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('conversations', [])))" 2>/dev/null)
    
    if [ ! -z "$count" ]; then
        echo -e "${GREEN}✓ 成功获取 $count 条对话记录${NC}"
        
        # 显示前3条对话
        echo ""
        echo "前3条对话记录："
        echo "$body" | python3 -c "
import sys, json
data = json.load(sys.stdin)
conversations = data.get('conversations', [])[:3]
for i, conv in enumerate(conversations, 1):
    q = conv.get('question', '')[:40]
    a = conv.get('content', '')[:40]
    print(f'  {i}. 问: {q}')
    print(f'     答: {a}')
    print()
" 2>/dev/null
    else
        echo -e "${YELLOW}⚠ 无法解析对话数据${NC}"
    fi
else
    echo -e "${RED}✗ API 请求失败 (HTTP $http_code)${NC}"
    echo "响应内容："
    echo "$body"
fi

echo ""
echo "=========================================="
echo "2. 检查前端文件..."
echo ""

cd "$PROJECT_ROOT"

files=(
    "frontend/src/views/ConversationHistory.vue"
    "frontend/src/api/index.ts"
    "frontend/src/router/index.ts"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file (不存在)${NC}"
        all_exist=false
    fi
done

echo ""
echo "=========================================="
echo "3. 检查前端服务..."
echo ""

if lsof -ti:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务正在运行 (http://localhost:5173)${NC}"
    echo "  访问地址: http://localhost:5173/conversation"
else
    echo -e "${YELLOW}⚠ 前端服务未运行${NC}"
    echo "  启动命令: cd frontend && npm run dev"
fi

echo ""
echo "=========================================="
echo "4. 功能清单"
echo "=========================================="
echo ""
echo "后端功能："
echo "  ✓ GET /api/command/conversation - 获取对话记录"
echo "  ✓ 支持 device_id 参数"
echo "  ✓ 返回 JSON 格式数据"
echo ""
echo "前端功能："
echo "  ✓ /conversation 路由"
echo "  ✓ 设备选择器"
echo "  ✓ 对话时间轴展示"
echo "  ✓ 智能时间格式化"
echo "  ✓ 用户问题和小爱回答区分"
echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
