# 定时执行指令功能

## 概述

scheduler 现在支持定时或延迟执行语音指令，可以在指定时间自动执行任何语音命令。

## 功能特性

- 定时执行：使用 Cron 表达式设置定期执行的指令
- 延迟执行：设置在指定分钟后执行一次性指令
- 设备指定：可选择在特定设备上执行指令
- 自动处理：指令会通过统一的语音命令处理流程执行

## API 使用

### 快速创建定时/延迟指令任务

**端点**: `POST /api/scheduler/quick/command`

#### 定时执行示例

每天早上 7 点播放音乐：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放周杰伦的歌",
    "cron_expression": "0 7 * * *"
  }'
```

每周一到周五晚上 8 点播放新闻：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放今日新闻",
    "cron_expression": "0 20 * * 1-5"
  }'
```

#### 延迟执行示例

10 分钟后执行指令：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放轻音乐",
    "delay_minutes": 10
  }'
```

#### 指定设备执行

在特定设备上执行指令：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放睡眠音乐",
    "cron_expression": "0 22 * * *",
    "device_id": "your_device_id"
  }'
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| command | string | 是 | 要执行的语音指令文本 |
| cron_expression | string | 否* | Cron 表达式（定时执行） |
| delay_minutes | integer | 否* | 延迟分钟数（延迟执行，1-1440） |
| device_id | string | 否 | 设备ID（不指定则使用默认设备） |

*注意：`cron_expression` 和 `delay_minutes` 必须提供其中之一，不能同时提供。

### 响应示例

```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_type": "command",
  "name": "执行指令: 播放周杰伦的歌",
  "trigger_type": "cron",
  "cron_expression": "0 7 * * *",
  "params": {
    "command": "播放周杰伦的歌"
  },
  "enabled": true,
  "next_run_time": "2026-03-27T07:00:00",
  "created_at": "2026-03-26T10:30:00",
  "updated_at": "2026-03-26T10:30:00"
}
```

## 使用场景

### 1. 定时播放音乐

每天早上 7 点播放起床音乐：
```json
{
  "command": "播放轻快的音乐",
  "cron_expression": "0 7 * * *"
}
```

### 2. 定时播放播放列表

每晚 10 点播放睡眠音乐：
```json
{
  "command": "播放睡眠音乐播放列表",
  "cron_expression": "0 22 * * *"
}
```

### 3. 工作日提醒

周一到周五下午 6 点提醒下班：
```json
{
  "command": "提醒我该下班了",
  "cron_expression": "0 18 * * 1-5"
}
```

### 4. 延迟执行

30 分钟后停止播放：
```json
{
  "command": "停止播放",
  "delay_minutes": 30
}
```

## Cron 表达式说明

格式：`分 时 日 月 周`

- 分：0-59
- 时：0-23
- 日：1-31
- 月：1-12
- 周：0-6（0=周日）

### 常用示例

| 表达式 | 说明 |
|--------|------|
| `0 7 * * *` | 每天早上 7 点 |
| `30 20 * * *` | 每天晚上 8 点 30 分 |
| `0 */2 * * *` | 每 2 小时 |
| `0 9 * * 1-5` | 周一到周五早上 9 点 |
| `0 0 1 * *` | 每月 1 号凌晨 |
| `0 12 * * 0` | 每周日中午 12 点 |

## 任务管理

### 查看所有指令任务

```bash
curl "http://localhost:8000/api/scheduler/tasks?task_type=command"
```

### 查看特定任务

```bash
curl "http://localhost:8000/api/scheduler/tasks/{task_id}"
```

### 删除任务

```bash
curl -X DELETE "http://localhost:8000/api/scheduler/tasks/{task_id}"
```

### 更新任务

```bash
curl -X PUT "http://localhost:8000/api/scheduler/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

## 注意事项

1. 指令会通过统一的语音命令处理流程执行，支持所有语音命令功能
2. 如果不指定 device_id，将使用默认设备
3. 延迟执行的任务是一次性的，执行后会自动删除
4. 定时执行的任务会持续执行，直到手动删除
5. 任务会持久化保存，重启后自动恢复
6. 延迟时间最长为 1440 分钟（24 小时）

## 技术实现

### 任务类型

新增了 `TaskType.COMMAND` 任务类型，用于标识指令执行任务。

### 执行流程

1. 任务触发时，scheduler 调用 `execute_command` 方法
2. `execute_command` 使用 `CommandHandler` 处理指令
3. `CommandHandler` 调用统一的语音命令 API
4. 指令通过正常的语音命令流程执行

### 相关文件

- `backend/src/xiaoai_media/services/scheduler_service.py` - 任务类型定义
- `backend/src/xiaoai_media/scheduler_executor.py` - 指令执行逻辑
- `backend/src/xiaoai_media/api/routes/scheduler.py` - API 接口
- `backend/src/xiaoai_media/api/main.py` - 回调注册
