# 设备选择功能说明

## 概述

所有定时任务类型现在都支持设备选择功能，可以在创建任务时指定在哪个设备上执行任务。

## 功能特性

### 支持的任务类型

所有任务类型都支持设备选择：

1. **播放音乐** (play_music)
2. **播放播放列表** (play_playlist)
3. **提醒** (reminder)
4. **执行指令** (command)

### 设备选择行为

- **指定设备**：任务将在指定的设备上执行
- **不指定设备**：任务将在默认设备上执行（配置文件中的主设备）

## 使用方法

### API 使用

在创建任务时，在 `params` 中添加 `device_id` 参数：

#### 播放音乐任务

```bash
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_music",
    "name": "卧室早上播放音乐",
    "cron_expression": "0 7 * * *",
    "params": {
      "song_name": "晴天",
      "artist": "周杰伦",
      "device_id": "bedroom_speaker_id"
    }
  }'
```

#### 播放播放列表任务

```bash
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_playlist",
    "name": "客厅晚上播放音乐",
    "cron_expression": "0 20 * * *",
    "params": {
      "playlist_id": "relax-playlist",
      "device_id": "living_room_speaker_id"
    }
  }'
```

#### 提醒任务

```bash
curl -X POST "http://localhost:8000/api/scheduler/tasks/delay" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "10分钟后提醒",
    "delay_minutes": 10,
    "params": {
      "message": "该喝水了",
      "device_id": "kitchen_speaker_id"
    }
  }'
```

#### 执行指令任务

```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放睡眠音乐",
    "cron_expression": "0 22 * * *",
    "device_id": "bedroom_speaker_id"
  }'
```

### 前端界面使用

#### 创建任务对话框

1. 点击"创建任务"按钮
2. 选择任务类型（任意类型）
3. 填写任务参数
4. 在"设备ID（可选）"字段输入设备ID
5. 点击"创建"

#### 快捷操作

快捷操作卡片目前不支持设备选择，使用默认设备。如需指定设备，请使用完整的创建对话框。

## 使用场景

### 1. 多房间音乐控制

在不同房间的设备上播放不同的音乐：

```bash
# 卧室早上7点播放轻音乐
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_music",
    "name": "卧室早上音乐",
    "cron_expression": "0 7 * * *",
    "params": {
      "song_name": "轻音乐",
      "device_id": "bedroom_speaker"
    }
  }'

# 客厅晚上8点播放新闻
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放今日新闻",
    "cron_expression": "0 20 * * *",
    "device_id": "living_room_speaker"
  }'
```

### 2. 分区提醒

在不同区域的设备上发送提醒：

```bash
# 厨房提醒做饭
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "做饭提醒",
    "cron_expression": "0 18 * * *",
    "params": {
      "message": "该准备晚饭了",
      "device_id": "kitchen_speaker"
    }
  }'

# 书房提醒休息
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "休息提醒",
    "cron_expression": "0 */2 * * *",
    "params": {
      "message": "该休息一下了",
      "device_id": "study_speaker"
    }
  }'
```

### 3. 儿童房定时播放

为儿童房设置专门的播放任务：

```bash
# 儿童房晚上9点播放睡眠故事
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_playlist",
    "name": "儿童睡眠故事",
    "cron_expression": "0 21 * * *",
    "params": {
      "playlist_id": "kids-bedtime-stories",
      "device_id": "kids_room_speaker"
    }
  }'
```

### 4. 老人房定时提醒

为老人房设置吃药提醒：

```bash
# 老人房早晚提醒吃药
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "吃药提醒",
    "cron_expression": "0 8,20 * * *",
    "params": {
      "message": "该吃药了",
      "device_id": "elderly_room_speaker"
    }
  }'
```

## 获取设备ID

### 方法1：通过API查询

```bash
curl "http://localhost:8000/api/devices"
```

返回示例：
```json
{
  "devices": [
    {
      "device_id": "bedroom_speaker_123",
      "name": "卧室小爱音箱",
      "model": "xiaomi.wifispeaker.lx06"
    },
    {
      "device_id": "living_room_speaker_456",
      "name": "客厅小爱音箱",
      "model": "xiaomi.wifispeaker.lx05"
    }
  ]
}
```

### 方法2：通过前端界面

1. 打开"设备列表"页面
2. 查看设备列表
3. 复制需要的设备ID

## 技术实现

### 后端实现

所有任务执行方法都支持 `device_id` 参数：

```python
async def execute_play_music(self, task_id: str, params: dict[str, Any]):
    """执行播放音乐任务"""
    song_name = params.get("song_name")
    artist = params.get("artist")
    device_id = params.get("device_id")  # 获取设备ID
    
    if not device_id:
        client = get_client()
        device_id = client.device_id  # 使用默认设备
    
    # 在指定设备上播放
    await self.music_service.play_song(song["id"], device_id=device_id)
```

### 前端实现

创建对话框中所有任务类型都显示设备选择字段：

```vue
<!-- 所有任务类型都支持设备选择 -->
<el-form-item label="设备ID（可选）">
  <el-input
    v-model="taskForm.device_id"
    placeholder="不填则使用默认设备"
  />
  <template #extra>
    <span style="font-size: 12px; color: #909399;">
      可在设备列表页面查看可用设备ID
    </span>
  </template>
</el-form-item>
```

## 注意事项

### 1. 设备ID格式

- 设备ID是字符串类型
- 通常格式为：`设备名称_数字` 或 `did_数字`
- 区分大小写

### 2. 设备在线状态

- 确保指定的设备在线且可访问
- 如果设备离线，任务执行会失败
- 建议使用稳定在线的设备

### 3. 默认设备

- 不指定设备ID时，使用配置文件中的默认设备
- 默认设备在 `user_config.py` 中配置
- 确保默认设备配置正确

### 4. 权限问题

- 确保有权限访问指定的设备
- 某些设备可能需要特殊权限
- 检查设备是否在同一账号下

### 5. 快捷操作限制

- 快捷操作卡片不支持设备选择
- 需要指定设备时，使用完整的创建对话框
- 这是为了保持快捷操作的简洁性

## 最佳实践

### 1. 设备命名规范

为设备设置有意义的名称，方便识别：
- ✅ `bedroom_speaker` - 卧室音箱
- ✅ `living_room_speaker` - 客厅音箱
- ✅ `kitchen_speaker` - 厨房音箱
- ❌ `device_123` - 难以识别

### 2. 任务命名包含设备信息

在任务名称中包含设备信息，方便管理：
- ✅ "卧室早上播放音乐"
- ✅ "客厅晚上播放新闻"
- ❌ "播放音乐"

### 3. 测试设备连接

创建任务前，先测试设备是否可用：
1. 在命令面板中手动发送指令到该设备
2. 确认设备响应正常
3. 再创建定时任务

### 4. 备用方案

为重要任务设置备用设备：
- 创建两个相同的任务
- 分别指定主设备和备用设备
- 确保至少一个设备可用

## 常见问题

### Q: 如何知道设备ID是否正确？

A: 
1. 通过设备列表API查询所有设备
2. 在前端设备列表页面查看
3. 尝试手动发送指令到该设备测试

### Q: 设备ID填错了会怎样？

A: 
- 任务会执行失败
- 错误信息会记录在日志中
- 可以编辑任务修改设备ID

### Q: 可以同时在多个设备上执行任务吗？

A: 
- 单个任务只能指定一个设备
- 如需多个设备，创建多个任务
- 可以设置相同的执行时间

### Q: 不同任务类型的设备选择有区别吗？

A: 
- 没有区别，所有任务类型的设备选择功能完全相同
- 都支持指定设备或使用默认设备
- 实现方式统一

### Q: 快捷操作为什么不支持设备选择？

A: 
- 为了保持快捷操作的简洁性
- 快捷操作主要用于快速创建常用任务
- 需要指定设备时，使用完整的创建对话框

## 更新日志

### v0.2.0 - 2026-03-26

- ✅ 所有任务类型都支持设备选择
- ✅ 后端所有执行方法支持 device_id 参数
- ✅ 前端创建对话框统一显示设备选择字段
- ✅ 完善的文档和使用示例

## 相关文档

- [定时任务主文档](./README.md)
- [定时执行指令功能](./COMMAND_EXECUTION.md)
- [前端功能指南](./FRONTEND_COMMAND_GUIDE.md)
- [更新日志](./CHANGELOG.md)
