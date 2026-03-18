# 对话记录功能 - 快速参考

## 🚀 快速开始

### 访问页面
```
http://localhost:5173/conversation
```

### 使用步骤
1. 点击左侧"对话记录"菜单
2. 选择设备（可选）
3. 点击"查询对话"按钮
4. 查看对话记录

## 📡 API 端点

### 获取对话记录
```bash
GET /api/command/conversation?device_id={device_id}
```

**示例**:
```bash
curl "http://localhost:8000/api/command/conversation"
```

**响应**:
```json
{
  "conversations": [
    {
      "timestamp_ms": 1773740151066,
      "question": "定三十分钟的闹钟",
      "content": ""
    }
  ]
}
```

## 🔧 测试命令

### 快速测试
```bash
cd test/conversation
./test_conversation.sh
```

### 手动测试后端
```bash
curl -s "http://localhost:8000/api/command/conversation" | python3 -m json.tool
```

### 检查前端服务
```bash
curl -I "http://localhost:5173/conversation"
```
