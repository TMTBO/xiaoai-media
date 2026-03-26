# 定时执行指令功能实现总结

## 实现日期
2026-03-26

## 功能概述

在 scheduler 中添加了定时执行指令的能力，允许用户创建定时或延迟执行任何语音指令的任务。

## 实现内容

### 1. 核心代码修改

#### 1.1 添加新的任务类型
**文件**: `backend/src/xiaoai_media/services/scheduler_service.py`

```python
class TaskType(str, Enum):
    PLAY_MUSIC = "play_music"
    PLAY_PLAYLIST = "play_playlist"
    REMINDER = "reminder"
    COMMAND = "command"  # 新增
```

#### 1.2 实现指令执行逻辑
**文件**: `backend/src/xiaoai_media/scheduler_executor.py`

- 导入 `CommandHandler`
- 在 `SchedulerExecutor.__init__` 中初始化 `CommandHandler`
- 添加 `execute_command` 方法：
  - 接收 `command` 和可选的 `device_id` 参数
  - 如果未指定设备，使用默认设备
  - 调用 `CommandHandler.handle_command` 执行指令
  - 完整的错误处理和日志记录

#### 1.3 注册任务回调
**文件**: `backend/src/xiaoai_media/api/main.py`

```python
scheduler_service.register_callback(TaskType.COMMAND, executor.execute_command)
```

#### 1.4 添加 API 接口
**文件**: `backend/src/xiaoai_media/api/routes/scheduler.py`

- 添加 `QuickCommandCreate` 请求模型
- 添加 `POST /api/scheduler/quick/command` 端点
- 支持两种模式：
  - 定时执行：使用 `cron_expression`
  - 延迟执行：使用 `delay_minutes`
- 参数验证和错误处理

### 2. 文档

创建了以下文档：

1. **COMMAND_EXECUTION.md** - 功能说明文档
   - 功能概述和特性
   - API 使用说明
   - 请求参数详解
   - Cron 表达式说明
   - 任务管理方法
   - 注意事项和技术实现

2. **COMMAND_EXAMPLES.md** - 使用示例文档
   - 15+ 实际使用场景
   - Python 客户端示例
   - 任务管理示例
   - 常见问题解答

3. **更新 README.md** - 主文档更新
   - 添加新任务类型说明
   - 添加快捷 API 文档
   - 添加使用场景示例

4. **更新 CHANGELOG.md** - 版本更新日志
   - 记录 v0.2.0 版本更新
   - 列出所有新增功能

### 3. 测试

创建了测试文件：`backend/tests/test_command_scheduler.py`

包含以下测试用例：
- 测试执行指令（指定设备ID）
- 测试执行指令（使用默认设备）
- 测试执行指令（缺少参数）
- 测试添加定时指令任务
- 测试添加一次性指令任务
- 测试指令任务执行

## 功能特性

### 支持的功能

1. **定时执行**
   - 使用 Cron 表达式设置定期执行
   - 支持复杂的时间规则
   - 任务持久化，重启后自动恢复

2. **延迟执行**
   - 设置延迟分钟数（1-1440分钟）
   - 一次性执行，完成后自动删除

3. **设备指定**
   - 可选择在特定设备上执行
   - 不指定则使用默认设备

4. **指令处理**
   - 通过统一的语音命令处理流程
   - 支持所有语音命令功能
   - 完整的错误处理

### API 端点

```
POST /api/scheduler/quick/command
```

**请求参数**：
- `command` (string, 必填): 语音指令文本
- `cron_expression` (string, 可选): Cron 表达式
- `delay_minutes` (integer, 可选): 延迟分钟数
- `device_id` (string, 可选): 设备ID

**注意**: `cron_expression` 和 `delay_minutes` 必须提供其中之一。

## 使用示例

### 定时执行

每天早上 7 点播放音乐：
```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放周杰伦的歌",
    "cron_expression": "0 7 * * *"
  }'
```

### 延迟执行

30 分钟后停止播放：
```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "停止播放",
    "delay_minutes": 30
  }'
```

### 指定设备

在特定设备上执行：
```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放睡眠音乐",
    "cron_expression": "0 22 * * *",
    "device_id": "bedroom_speaker"
  }'
```

## 技术实现

### 执行流程

1. 用户通过 API 创建指令任务
2. Scheduler 在指定时间触发任务
3. 调用 `SchedulerExecutor.execute_command`
4. `execute_command` 使用 `CommandHandler` 处理指令
5. `CommandHandler` 调用统一的语音命令 API
6. 指令通过正常的语音命令流程执行

### 关键组件

- **SchedulerService**: 任务调度和管理
- **SchedulerExecutor**: 任务执行器
- **CommandHandler**: 指令处理器
- **TaskType.COMMAND**: 新的任务类型

### 持久化

任务配置保存在：`~/.xiaoai_media/scheduler/tasks.json`

示例：
```json
{
  "task-uuid": {
    "task_id": "task-uuid",
    "task_type": "command",
    "name": "执行指令: 播放周杰伦的歌",
    "trigger_type": "cron",
    "cron_expression": "0 7 * * *",
    "params": {
      "command": "播放周杰伦的歌"
    },
    "enabled": true,
    "created_at": "2026-03-26T10:00:00",
    "updated_at": "2026-03-26T10:00:00"
  }
}
```

## 使用场景

1. **定时播放音乐** - 每天早上自动播放起床音乐
2. **工作提醒** - 工作日定时提醒休息、喝水等
3. **睡眠辅助** - 晚上定时播放睡眠音乐
4. **自动控制** - 定时调整音量、停止播放等
5. **番茄工作法** - 工作一段时间后自动提醒休息
6. **多设备控制** - 在不同设备上执行不同指令

## 注意事项

1. 指令会通过统一的语音命令处理流程执行
2. 支持所有语音命令功能（播放、搜索、控制等）
3. 如果不指定 device_id，将使用默认设备
4. 延迟执行的任务是一次性的，执行后自动删除
5. 定时执行的任务会持续执行，直到手动删除
6. 任务会持久化保存，重启后自动恢复
7. 延迟时间最长为 1440 分钟（24 小时）

## 后续扩展

可以考虑的扩展功能：

1. **条件执行** - 根据时间、天气等条件执行不同指令
2. **任务链** - 支持顺序执行多个指令
3. **重试机制** - 失败时自动重试
4. **执行历史** - 记录任务执行历史和结果
5. **通知功能** - 任务执行完成后发送通知
6. **前端界面** - 可视化的任务管理界面

## 相关文件

### 核心代码
- `backend/src/xiaoai_media/services/scheduler_service.py`
- `backend/src/xiaoai_media/scheduler_executor.py`
- `backend/src/xiaoai_media/api/routes/scheduler.py`
- `backend/src/xiaoai_media/api/main.py`
- `backend/src/xiaoai_media/command_handler.py`

### 测试
- `backend/tests/test_command_scheduler.py`

### 文档
- `docs/scheduler/COMMAND_EXECUTION.md`
- `docs/scheduler/COMMAND_EXAMPLES.md`
- `docs/scheduler/README.md`
- `docs/scheduler/CHANGELOG.md`
- `docs/scheduler/COMMAND_FEATURE_SUMMARY.md`

## 总结

成功在 scheduler 中添加了定时执行指令的能力，实现了：

✅ 新的任务类型 `TaskType.COMMAND`
✅ 完整的指令执行逻辑
✅ 快捷 API 接口
✅ 定时和延迟两种执行模式
✅ 设备指定功能
✅ 完整的文档和示例
✅ 测试用例

该功能与现有的 scheduler 系统无缝集成，支持所有语音命令功能，为用户提供了更灵活的自动化控制能力。
