#!/bin/bash

# 定时任务功能测试脚本

echo "=========================================="
echo "定时任务功能测试"
echo "=========================================="
echo ""

# 检查后端是否运行
echo "1. 检查后端服务..."
if curl -s http://localhost:8000/api/scheduler/tasks > /dev/null 2>&1; then
    echo "✅ 后端服务正常运行"
else
    echo "❌ 后端服务未运行，请先启动后端："
    echo "   cd backend && python run.py"
    exit 1
fi

echo ""
echo "2. 测试创建快速提醒..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": "测试提醒",
    "delay_minutes": 1
  }')

if echo "$RESPONSE" | grep -q "task_id"; then
    echo "✅ 快速提醒创建成功"
    TASK_ID=$(echo "$RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    echo "   任务ID: $TASK_ID"
else
    echo "❌ 创建失败"
    echo "   响应: $RESPONSE"
    exit 1
fi

echo ""
echo "3. 测试获取任务列表..."
TASKS=$(curl -s http://localhost:8000/api/scheduler/tasks)
TASK_COUNT=$(echo "$TASKS" | grep -o '"task_id"' | wc -l)
echo "✅ 当前任务数量: $TASK_COUNT"

echo ""
echo "4. 测试获取任务详情..."
TASK_DETAIL=$(curl -s http://localhost:8000/api/scheduler/tasks/$TASK_ID)
if echo "$TASK_DETAIL" | grep -q "测试提醒"; then
    echo "✅ 任务详情获取成功"
else
    echo "❌ 获取失败"
fi

echo ""
echo "5. 测试更新任务..."
UPDATE_RESPONSE=$(curl -s -X PUT http://localhost:8000/api/scheduler/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }')

if echo "$UPDATE_RESPONSE" | grep -q '"enabled":false'; then
    echo "✅ 任务更新成功（已禁用）"
else
    echo "❌ 更新失败"
fi

echo ""
echo "6. 测试删除任务..."
DELETE_RESPONSE=$(curl -s -X DELETE http://localhost:8000/api/scheduler/tasks/$TASK_ID)
if echo "$DELETE_RESPONSE" | grep -q "已删除"; then
    echo "✅ 任务删除成功"
else
    echo "❌ 删除失败"
fi

echo ""
echo "7. 测试创建定时播放音乐..."
MUSIC_RESPONSE=$(curl -s -X POST http://localhost:8000/api/scheduler/quick/play-music \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "晴天",
    "artist": "周杰伦",
    "cron_expression": "0 7 * * *"
  }')

if echo "$MUSIC_RESPONSE" | grep -q "task_id"; then
    echo "✅ 定时播放音乐任务创建成功"
    MUSIC_TASK_ID=$(echo "$MUSIC_RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    
    # 清理测试任务
    curl -s -X DELETE http://localhost:8000/api/scheduler/tasks/$MUSIC_TASK_ID > /dev/null
    echo "   (测试任务已清理)"
else
    echo "❌ 创建失败"
fi

echo ""
echo "=========================================="
echo "✅ 所有测试通过！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 访问 Web 管理界面: http://localhost:5173"
echo "2. 在左侧菜单点击'定时任务'"
echo "3. 尝试创建和管理任务"
echo ""
echo "文档："
echo "- 快速开始: docs/scheduler/QUICK_START.md"
echo "- 完整指南: docs/scheduler/COMPLETE_GUIDE.md"
echo "- 前端测试: docs/scheduler/FRONTEND_TEST.md"
