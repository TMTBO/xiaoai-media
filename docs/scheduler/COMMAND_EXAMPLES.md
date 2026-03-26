# 定时执行指令使用示例

本文档提供了定时执行指令功能的实际使用示例。

## 基础示例

### 1. 每天早上播放音乐

每天早上 7 点自动播放起床音乐：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放轻快的音乐",
    "cron_expression": "0 7 * * *"
  }'
```

### 2. 工作日闹钟

周一到周五早上 6:30 播放闹钟：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放闹钟铃声",
    "cron_expression": "30 6 * * 1-5"
  }'
```

### 3. 晚安音乐

每晚 10 点播放睡眠音乐：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放睡眠音乐",
    "cron_expression": "0 22 * * *"
  }'
```

## 进阶示例

### 4. 定时播放特定歌手

每天下午 3 点播放周杰伦的歌：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放周杰伦的歌",
    "cron_expression": "0 15 * * *"
  }'
```

### 5. 定时播放播放列表

每周六早上 9 点播放周末音乐播放列表：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放周末音乐播放列表",
    "cron_expression": "0 9 * * 6"
  }'
```

### 6. 每小时整点报时

每小时整点播放报时音效：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放报时音效",
    "cron_expression": "0 * * * *"
  }'
```

## 延迟执行示例

### 7. 10 分钟后停止播放

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "停止播放",
    "delay_minutes": 10
  }'
```

### 8. 30 分钟后播放白噪音

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放白噪音",
    "delay_minutes": 30
  }'
```

### 9. 1 小时后降低音量

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "音量调到 30",
    "delay_minutes": 60
  }'
```

## 多设备示例

### 10. 在卧室设备播放音乐

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放轻音乐",
    "cron_expression": "0 22 * * *",
    "device_id": "bedroom_speaker_id"
  }'
```

### 11. 在客厅设备播放新闻

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放今日新闻",
    "cron_expression": "0 7 * * *",
    "device_id": "living_room_speaker_id"
  }'
```

## 实用场景

### 12. 番茄工作法

工作 25 分钟后休息提醒：

```bash
# 开始工作时调用
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "提醒我休息一下",
    "delay_minutes": 25
  }'
```

### 13. 定时提醒喝水

每 2 小时提醒喝水：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "提醒我喝水",
    "cron_expression": "0 */2 * * *"
  }'
```

### 14. 午休音乐

每天中午 12:30 播放轻音乐：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放轻音乐",
    "cron_expression": "30 12 * * *"
  }'
```

### 15. 下班提醒

工作日下午 6 点提醒下班：

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "提醒我该下班了",
    "cron_expression": "0 18 * * 1-5"
  }'
```

## Python 客户端示例

### 使用 requests 库

```python
import requests

def create_scheduled_command(command, cron_expression=None, delay_minutes=None, device_id=None):
    """创建定时执行指令任务"""
    url = "http://localhost:8000/api/scheduler/quick/command"
    
    data = {
        "command": command
    }
    
    if cron_expression:
        data["cron_expression"] = cron_expression
    elif delay_minutes:
        data["delay_minutes"] = delay_minutes
    else:
        raise ValueError("必须提供 cron_expression 或 delay_minutes")
    
    if device_id:
        data["device_id"] = device_id
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    return response.json()

# 示例：每天早上 7 点播放音乐
task = create_scheduled_command(
    command="播放轻快的音乐",
    cron_expression="0 7 * * *"
)
print(f"任务已创建: {task['task_id']}")

# 示例：10 分钟后停止播放
task = create_scheduled_command(
    command="停止播放",
    delay_minutes=10
)
print(f"延迟任务已创建: {task['task_id']}")
```

### 使用 aiohttp 库（异步）

```python
import aiohttp
import asyncio

async def create_scheduled_command_async(command, cron_expression=None, delay_minutes=None):
    """异步创建定时执行指令任务"""
    url = "http://localhost:8000/api/scheduler/quick/command"
    
    data = {
        "command": command
    }
    
    if cron_expression:
        data["cron_expression"] = cron_expression
    elif delay_minutes:
        data["delay_minutes"] = delay_minutes
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()

# 使用示例
async def main():
    task = await create_scheduled_command_async(
        command="播放周杰伦的歌",
        cron_expression="0 15 * * *"
    )
    print(f"任务已创建: {task['task_id']}")

asyncio.run(main())
```

## 管理任务

### 查看所有指令任务

```bash
curl "http://localhost:8000/api/scheduler/tasks?task_type=command"
```

### 查看特定任务详情

```bash
curl "http://localhost:8000/api/scheduler/tasks/{task_id}"
```

### 暂停任务

```bash
curl -X PUT "http://localhost:8000/api/scheduler/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

### 恢复任务

```bash
curl -X PUT "http://localhost:8000/api/scheduler/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true
  }'
```

### 删除任务

```bash
curl -X DELETE "http://localhost:8000/api/scheduler/tasks/{task_id}"
```

## 注意事项

1. 所有指令都会通过语音命令处理流程执行，支持播放音乐、播放列表、搜索等所有功能
2. 如果不指定 device_id，将使用配置文件中的默认设备
3. 延迟执行的任务是一次性的，执行后会自动删除
4. 定时执行的任务会持续执行，需要手动删除或暂停
5. 任务会持久化保存，服务重启后自动恢复
6. 建议为任务设置有意义的名称，方便管理

## 常见问题

### Q: 如何获取设备 ID？

A: 可以通过以下 API 获取设备列表：

```bash
curl "http://localhost:8000/api/devices"
```

### Q: 任务没有执行怎么办？

A: 检查以下几点：
1. 确认任务的 enabled 状态为 true
2. 检查 Cron 表达式是否正确
3. 查看服务日志确认是否有错误信息
4. 确认设备 ID 是否正确（如果指定了）

### Q: 如何修改已创建的任务？

A: 使用 PUT 请求更新任务：

```bash
curl -X PUT "http://localhost:8000/api/scheduler/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "cron_expression": "0 8 * * *",
    "params": {
      "command": "播放新的音乐"
    }
  }'
```

### Q: 延迟时间有限制吗？

A: 是的，延迟时间最长为 1440 分钟（24 小时）。
