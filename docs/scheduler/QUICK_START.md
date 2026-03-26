# 定时任务快速开始指南

## 安装依赖

```bash
cd backend
pip install -e .
```

这会自动安装 `apscheduler>=3.10.0` 依赖。

## 启动应用

```bash
cd backend
python run.py
```

应用启动后，你会看到日志：

```
2024-03-20 10:00:00 INFO     xiaoai_media.api.main - 定时任务调度器已启动
```

## 快速测试

### 1. 创建一个10分钟后的提醒

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": "该喝水了",
    "delay_minutes": 10
  }'
```

响应示例：

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "task_type": "reminder",
  "name": "提醒: 该喝水了",
  "trigger_type": "date",
  "run_date": "2024-03-20T10:10:00",
  "params": {
    "message": "该喝水了"
  },
  "enabled": true,
  "next_run_time": "2024-03-20T10:10:00",
  "created_at": "2024-03-20T10:00:00",
  "updated_at": "2024-03-20T10:00:00"
}
```

### 2. 创建每天早上7点播放音乐的任务

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-music \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "晴天",
    "artist": "周杰伦",
    "cron_expression": "0 7 * * *"
  }'
```

### 3. 查看所有任务

```bash
curl http://localhost:8000/api/scheduler/tasks
```

### 4. 查看特定类型的任务

```bash
# 只看提醒任务
curl http://localhost:8000/api/scheduler/tasks?task_type=reminder

# 只看播放音乐任务
curl http://localhost:8000/api/scheduler/tasks?task_type=play_music

# 只看播放播放列表任务
curl http://localhost:8000/api/scheduler/tasks?task_type=play_playlist
```

### 5. 更新任务

```bash
curl -X PUT http://localhost:8000/api/scheduler/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新的任务名称",
    "enabled": false
  }'
```

### 6. 删除任务

```bash
curl -X DELETE http://localhost:8000/api/scheduler/tasks/{task_id}
```

## 常用场景示例

### 场景1：每天早上7点播放起床音乐

```bash
curl -X POST http://localhost:8000/api/scheduler/tasks/cron \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_music",
    "name": "早安音乐",
    "cron_expression": "0 7 * * *",
    "params": {
      "song_name": "晴天",
      "artist": "周杰伦"
    },
    "enabled": true
  }'
```

### 场景2：工作日晚上8点播放放松音乐播放列表

```bash
curl -X POST http://localhost:8000/api/scheduler/tasks/cron \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_playlist",
    "name": "晚间放松时光",
    "cron_expression": "0 20 * * 1-5",
    "params": {
      "playlist_id": "my-relax-playlist"
    },
    "enabled": true
  }'
```

### 场景3：每2小时提醒喝水

```bash
curl -X POST http://localhost:8000/api/scheduler/tasks/cron \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "喝水提醒",
    "cron_expression": "0 */2 * * *",
    "params": {
      "message": "该喝水了，保持健康"
    },
    "enabled": true
  }'
```

### 场景4：30分钟后提醒关火

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": "记得关火",
    "delay_minutes": 30
  }'
```

### 场景5：每周日中午12点播放周末音乐

```bash
curl -X POST http://localhost:8000/api/scheduler/tasks/cron \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_playlist",
    "name": "周末音乐",
    "cron_expression": "0 12 * * 0",
    "params": {
      "playlist_id": "weekend-playlist"
    },
    "enabled": true
  }'
```

## Cron 表达式速查表

格式：`分 时 日 月 周`

| 表达式 | 说明 |
|--------|------|
| `0 7 * * *` | 每天早上7点 |
| `30 20 * * *` | 每天晚上8点30分 |
| `0 */2 * * *` | 每2小时 |
| `0 9-17 * * *` | 每天9点到17点，每小时 |
| `0 7 * * 1-5` | 周一到周五早上7点 |
| `0 12 * * 0` | 每周日中午12点 |
| `0 0 1 * *` | 每月1号凌晨 |
| `0 8 1,15 * *` | 每月1号和15号早上8点 |
| `*/30 * * * *` | 每30分钟 |
| `0 0 * * 1` | 每周一凌晨 |

## 查看任务执行日志

任务执行时会在应用日志中输出：

```
2024-03-20 10:10:00 INFO     xiaoai_media.services.scheduler_service - 执行任务: a1b2c3d4-e5f6-7890-abcd-ef1234567890 (类型: reminder)
2024-03-20 10:10:00 INFO     xiaoai_media.scheduler_executor - 任务 a1b2c3d4-e5f6-7890-abcd-ef1234567890: 发送提醒 '该喝水了'
2024-03-20 10:10:00 INFO     xiaoai_media.scheduler_executor - 任务 a1b2c3d4-e5f6-7890-abcd-ef1234567890: 提醒已发送
2024-03-20 10:10:00 INFO     xiaoai_media.services.scheduler_service - 任务 a1b2c3d4-e5f6-7890-abcd-ef1234567890 执行成功
2024-03-20 10:10:00 INFO     xiaoai_media.services.scheduler_service - 一次性任务 a1b2c3d4-e5f6-7890-abcd-ef1234567890 已完成，删除任务
```

## 查看持久化文件

任务配置保存在：

```bash
cat ~/.xiaoai_media/scheduler/tasks.json
```

文件内容示例：

```json
{
  "a1b2c3d4-e5f6-7890-abcd-ef1234567890": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "task_type": "play_music",
    "name": "早安音乐",
    "trigger_type": "cron",
    "cron_expression": "0 7 * * *",
    "params": {
      "song_name": "晴天",
      "artist": "周杰伦"
    },
    "enabled": true,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00"
  }
}
```

## 测试任务功能

运行测试套件：

```bash
cd backend
pytest tests/test_scheduler.py -v
```

## API 文档

启动应用后，访问 Swagger 文档：

```
http://localhost:8000/docs
```

在文档中可以看到所有定时任务相关的 API 端点，并可以直接测试。

## 故障排查

### 任务没有执行

1. 检查任务是否启用：
   ```bash
   curl http://localhost:8000/api/scheduler/tasks/{task_id}
   ```

2. 查看应用日志，搜索任务ID或错误信息

3. 确认时区设置正确（默认为 Asia/Shanghai）

### 任务执行失败

1. 查看日志中的错误详情
2. 确认音乐服务或播放列表是否可用
3. 检查任务参数是否正确

### 应用重启后任务丢失

1. 检查持久化文件是否存在：
   ```bash
   ls -la ~/.xiaoai_media/scheduler/
   ```

2. 检查文件权限

3. 查看应用启动日志中的恢复信息

## 下一步

- 阅读完整的 [API 文档](./README.md)
- 查看 [前端开发指南](./FRONTEND_GUIDE.md)
- 了解如何扩展新的任务类型
