#!/bin/bash

# 播单批量导入功能测试脚本

BASE_URL="http://localhost:8000/api"

echo "=== 播单批量导入功能测试 ==="
echo ""

# 1. 检查环境
echo "1. 检查运行环境..."
DIRS_RESPONSE=$(curl -s "$BASE_URL/playlists/directories")
IS_DOCKER=$(echo "$DIRS_RESPONSE" | jq -r '.is_docker')
echo "运行模式: $([ "$IS_DOCKER" = "true" ] && echo "Docker" || echo "本地")"
echo ""

# 2. 显示可用目录
echo "2. 可用目录列表:"
echo "$DIRS_RESPONSE" | jq -r '.directories[] | "  - \(.name): \(.path)"'
echo ""

# 3. 创建测试播单
echo "3. 创建测试播单..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/playlists" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "批量导入测试",
    "type": "music",
    "description": "测试批量导入功能",
    "voice_keywords": ["测试音乐"]
  }')

PLAYLIST_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')
echo "播单ID: $PLAYLIST_ID"
echo ""

# 4. 提示用户输入目录
if [ "$IS_DOCKER" = "true" ]; then
  echo "4. Docker模式 - 请从上面的列表中选择一个目录"
  echo "   例如: /data/music"
else
  echo "4. 本地模式 - 请输入要导入的目录路径"
  echo "   例如: /Users/username/Music"
fi

read -p "请输入目录路径: " IMPORT_DIR

if [ -z "$IMPORT_DIR" ]; then
  echo "未输入目录，跳过导入测试"
  exit 0
fi

# 5. 执行导入
echo ""
echo "5. 开始导入文件..."
IMPORT_RESPONSE=$(curl -s -X POST "$BASE_URL/playlists/$PLAYLIST_ID/import" \
  -H "Content-Type: application/json" \
  -d "{
    \"directory\": \"$IMPORT_DIR\",
    \"recursive\": true,
    \"file_extensions\": [\".mp3\", \".m4a\", \".flac\", \".wav\"]
  }")

echo "$IMPORT_RESPONSE" | jq '.'
echo ""

# 6. 查看导入结果
IMPORTED=$(echo "$IMPORT_RESPONSE" | jq -r '.imported // 0')
if [ "$IMPORTED" -gt 0 ]; then
  echo "6. 导入成功！查看播单内容..."
  curl -s "$BASE_URL/playlists/$PLAYLIST_ID" | jq '{
    name: .name,
    total_items: (.items | length),
    first_5_items: .items[:5] | map({title, artist, album})
  }'
else
  echo "6. 没有文件被导入"
  echo "   可能原因："
  echo "   - 目录不存在或为空"
  echo "   - 没有匹配的音频文件"
  echo "   - 权限不足"
fi

echo ""
echo "=== 测试完成 ==="
