# 定时任务功能文档

## 概述

定时任务功能基于 APScheduler 实现，支持在应用内创建和管理各种定时任务。所有任务配置会持久化到 Home 目录（`~/.xiaoai_media/scheduler/tasks.json`），应用重启后会自动恢复。

## 功能特性

- ✅ 定时播放音乐
- ✅ 定时播放播放列表
- ✅ 定时提醒（如：10分钟后提醒我）
- ✅ 定时执行指令（支持任何语音命令）
- ✅ 任务持久化到 Home 目录
- ✅ 支持 Cron 表达式（周期性任务）
- ✅ 支持一次性任务
- ✅ 完整的管理 API（创建、查询、更新、删除）
- ✅ 快捷操作 API

## 任务类型

### 1. 播放音乐 (play_music)

定时播放指定的歌曲。

参数：
- `song_name`: 歌曲名称（必填）
- `artist`: 歌手名称（可选）
- `device_id`: 设备ID（可选，默认使用主设备）

### 2. 播放播放列表 (play_playlist)

定时播放指定的播放列表。

参数：
- `playlist_id`: 播放列表ID（必填）
- `device_id`: 设备ID（可选，默认使用主设备）

### 3. 提醒 (reminder)

定时语音提醒。

参数：
- `message`: 提醒内容（必填）
- `device_id`: 设备ID（可选，默认使用主设备）

### 4. 执行指令 (command)

定时或延迟执行任何语音指令。

参数：
- `command`: 语音指令文本（必填）
- `device_id`: 设备ID（可选，默认使用主设备）

**特点**：
- 支持所有语音命令功能（播放音乐、播放列表、搜索等）
- 可以指定在特定设备上执行
- 支持定时执行（Cron）和延迟执行
- 指令通过统一的语音命令处理流程执行

**注意**：所有任务类型都支持设备选择，可以在不同设备上执行不同的任务。

**详细文档**：
- [定时执行指令功能说明](./COMMAND_EXECUTION.md)
- [使用示例](./COMMAND_EXAMPLES.md)

## API 端点

### 基础任务管理

#### 创建 Cron 定时任务

```http
POST /api/scheduler/tasks/cron
Content-Type: application/json

{
  "task_type": "play_music",
  "name": "每天早上7点播放音乐",
  "cron_expression": "0 7 * * *",
  "params": {
    "song_name": "晴天",
    "artist": "周杰伦"
  },
  "enabled": true
}
```

Cron 表达式格式：`分 时 日 月 周`

常用示例：
- `0 7 * * *` - 每天早上7点
- `30 20 * * 1-5` - 周一到周五晚上8点30分
- `0 */2 * * *` - 每2小时
- `0 12 * * 0` - 每周日中午12点
- `0 0 1 * *` - 每月1号凌晨

#### 创建一次性定时任务

```http
POST /api/scheduler/tasks/date
Content-Type: application/json

{
  "task_type": "reminder",
  "name": "下午3点提醒开会",
  "run_date": "2024-03-20T15:00:00",
  "params": {
    "message": "该开会了"
  },
  "enabled": true
}
```

#### 创建延迟任务

```http
POST /api/scheduler/tasks/delay
Content-Type: application/json

{
  "task_type": "reminder",
  "name": "10分钟后提醒",
  "delay_minutes": 10,
  "params": {
    "message": "时间到了"
  }
}
```

#### 列出所有任务

```http
GET /api/scheduler/tasks
```

可选查询参数：
- `task_type`: 按任务类型过滤（play_music, play_playlist, reminder）

#### 获取任务详情

```http
GET /api/scheduler/tasks/{task_id}
```

#### 更新任务

```http
PUT /api/scheduler/tasks/{task_id}
Content-Type: application/json

{
  "name": "新的任务名称",
  "cron_expression": "0 8 * * *",
  "enabled": false
}
```

#### 删除任务

```http
DELETE /api/scheduler/tasks/{task_id}
```

### 快捷操作 API

#### 快速创建提醒

```http
POST /api/scheduler/quick/reminder
Content-Type: application/json

{
  "message": "该喝水了",
  "delay_minutes": 30
}
```

#### 快速创建定时播放音乐

```http
POST /api/scheduler/quick/play-music
Content-Type: application/json

{
  "song_name": "晴天",
  "artist": "周杰伦",
  "cron_expression": "0 7 * * *"
}
```

#### 快速创建定时播放播放列表

```http
POST /api/scheduler/quick/play-playlist
Content-Type: application/json

{
  "playlist_id": "my-morning-playlist",
  "cron_expression": "0 7 * * 1-5"
}
```

#### 快速创建定时/延迟执行指令

```http
POST /api/scheduler/quick/command
Content-Type: application/json

{
  "command": "播放周杰伦的歌",
  "cron_expression": "0 7 * * *"
}
```

或延迟执行：

```http
POST /api/scheduler/quick/command
Content-Type: application/json

{
  "command": "停止播放",
  "delay_minutes": 30
}
```

参数说明：
- `command`: 语音指令文本（必填）
- `cron_expression`: Cron 表达式，用于定时执行（可选）
- `delay_minutes`: 延迟分钟数，用于延迟执行（可选）
- `device_id`: 设备ID（可选）

注意：`cron_expression` 和 `delay_minutes` 必须提供其中之一。

## 使用场景示例

### 场景 1：每天早上7点播放起床音乐

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-music \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "晴天",
    "artist": "周杰伦",
    "cron_expression": "0 7 * * *"
  }'
```

### 场景 2：工作日晚上8点播放放松音乐播放列表

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-playlist \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_id": "relax-playlist",
    "cron_expression": "0 20 * * 1-5"
  }'
```

### 场景 3：10分钟后提醒喝水

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": "该喝水了",
    "delay_minutes": 10
  }'
```

### 场景 4：每2小时提醒休息

```bash
curl -X POST http://localhost:8000/api/scheduler/tasks/cron \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "每2小时提醒休息",
    "cron_expression": "0 */2 * * *",
    "params": {
      "message": "该休息一下了"
    },
    "enabled": true
  }'
```

### 场景 5：每天早上7点执行语音指令

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放周杰伦的歌",
    "cron_expression": "0 7 * * *"
  }'
```

### 场景 6：30分钟后停止播放

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "停止播放",
    "delay_minutes": 30
  }'
```

## 数据持久化

任务配置保存在：`~/.xiaoai_media/scheduler/tasks.json`

文件格式示例：

```json
{
  "task-uuid-1": {
    "task_id": "task-uuid-1",
    "task_type": "play_music",
    "name": "每天早上7点播放音乐",
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

## 管理后台集成

前端管理页面需要实现以下功能：

1. 任务列表展示
   - 显示所有任务
   - 按类型筛选（包括执行指令）
   - 显示下次执行时间
   - 启用/禁用开关

2. 创建任务表单
   - 选择任务类型（包括执行指令）
   - 输入任务名称
   - 配置触发时间（Cron 或具体时间）
   - 输入任务参数

3. 编辑任务
   - 修改任务配置
   - 启用/禁用任务

4. 删除任务
   - 确认删除对话框

5. 快捷操作
   - 快速提醒按钮
   - 快速播放音乐
   - 快速播放播放列表
   - 快速执行指令（新增）
     - 支持定时执行（Cron）
     - 支持延迟执行（分钟数）

**前端功能详细文档**：[前端定时执行指令功能指南](./FRONTEND_COMMAND_GUIDE.md)

## 注意事项

1. 时区设置为 `Asia/Shanghai`
2. 一次性任务执行后会自动删除
3. 过期的一次性任务在应用启动时会被清理
4. 任务执行失败会记录日志，但不会影响后续执行
5. 延迟提醒最长支持 1440 分钟（24小时）

## 故障排查

### 任务没有执行

1. 检查任务是否启用：`GET /api/scheduler/tasks/{task_id}`
2. 检查下次执行时间是否正确
3. 查看应用日志中的错误信息

### 任务执行失败

1. 检查任务参数是否正确
2. 确认音乐服务或播放列表是否可用
3. 查看日志中的详细错误信息

### 任务丢失

1. 检查持久化文件：`~/.xiaoai_media/scheduler/tasks.json`
2. 确认文件权限是否正确
3. 查看应用启动日志中的恢复信息

## 开发扩展

如需添加新的任务类型：

1. 在 `scheduler_service.py` 中添加新的 `TaskType` 枚举值
2. 在 `scheduler_executor.py` 中实现对应的执行方法
3. 在 `main.py` 中注册回调函数
4. 更新 API 文档

示例：

```python
# 1. 添加任务类型
class TaskType(str, Enum):
    PLAY_MUSIC = "play_music"
    PLAY_PLAYLIST = "play_playlist"
    REMINDER = "reminder"
    VOLUME_CONTROL = "volume_control"  # 新增

# 2. 实现执行方法
async def execute_volume_control(self, task_id: str, params: dict[str, Any]):
    volume = params.get("volume", 50)
    client = get_client()
    await client.set_volume(volume)

# 3. 注册回调
scheduler_service.register_callback(
    TaskType.VOLUME_CONTROL, 
    executor.execute_volume_control
)
```
