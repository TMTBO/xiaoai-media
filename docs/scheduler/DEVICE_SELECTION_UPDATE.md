# 设备选择功能统一更新

## 更新日期
2026-03-26

## 问题描述

用户发现只有执行指令任务支持设备选择，而其他任务类型（播放音乐、播放播放列表、提醒）不支持设备选择，这是不合理的。

## 解决方案

统一为所有任务类型添加设备选择功能。

## 实现内容

### ✅ 后端修改

#### 文件：`backend/src/xiaoai_media/scheduler_executor.py`

为所有任务执行方法添加 `device_id` 参数支持：

1. **execute_play_music**
   - 添加 `device_id` 参数
   - 支持指定设备或使用默认设备
   - 在指定设备上播放音乐和发送TTS

2. **execute_play_playlist**
   - 添加 `device_id` 参数
   - 支持指定设备或使用默认设备
   - 在指定设备上播放播放列表和发送TTS

3. **execute_reminder**
   - 添加 `device_id` 参数
   - 支持指定设备或使用默认设备
   - 在指定设备上发送TTS提醒

4. **execute_command**
   - 已支持 `device_id` 参数（无需修改）

### ✅ 前端修改

#### 文件：`frontend/src/views/SchedulerManager.vue`

1. **创建对话框**
   - 将设备选择字段移到所有任务类型之后
   - 所有任务类型共享同一个设备选择字段
   - 添加帮助文本说明

2. **表单处理**
   - 统一处理所有任务类型的 `device_id` 参数
   - 编辑任务时正确加载 `device_id`
   - 重置表单时清空 `device_id`

### ✅ 文档更新

1. **docs/scheduler/README.md**
   - 更新所有任务类型的参数说明
   - 添加设备选择说明

2. **docs/scheduler/CHANGELOG.md**
   - 记录设备选择功能增强

3. **docs/scheduler/DEVICE_SELECTION_FEATURE.md**（新增）
   - 完整的设备选择功能说明
   - 使用方法和示例
   - 使用场景
   - 最佳实践
   - 常见问题

## 功能特性

### 统一的设备选择

所有任务类型都支持：
- ✅ 指定设备ID执行任务
- ✅ 不指定时使用默认设备
- ✅ 前端界面统一显示设备选择字段
- ✅ 完整的错误处理和日志记录

### 支持的任务类型

1. **播放音乐** - 在指定设备上播放音乐
2. **播放播放列表** - 在指定设备上播放播放列表
3. **提醒** - 在指定设备上发送语音提醒
4. **执行指令** - 在指定设备上执行语音指令

## 使用示例

### 后端API

```bash
# 播放音乐任务（指定设备）
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "play_music",
    "name": "卧室早上播放音乐",
    "cron_expression": "0 7 * * *",
    "params": {
      "song_name": "晴天",
      "device_id": "bedroom_speaker"
    }
  }'

# 提醒任务（指定设备）
curl -X POST "http://localhost:8000/api/scheduler/tasks/cron" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "厨房做饭提醒",
    "cron_expression": "0 18 * * *",
    "params": {
      "message": "该准备晚饭了",
      "device_id": "kitchen_speaker"
    }
  }'
```

### 前端界面

1. 打开创建任务对话框
2. 选择任意任务类型
3. 填写任务参数
4. 在"设备ID（可选）"字段输入设备ID
5. 点击创建

## 使用场景

### 1. 多房间音乐控制

在不同房间的设备上播放不同的音乐：
- 卧室早上播放轻音乐
- 客厅晚上播放新闻
- 书房工作时播放专注音乐

### 2. 分区提醒

在不同区域的设备上发送提醒：
- 厨房提醒做饭
- 书房提醒休息
- 卧室提醒睡觉

### 3. 家庭成员专属

为不同家庭成员设置专属任务：
- 儿童房播放睡眠故事
- 老人房提醒吃药
- 主卧播放起床音乐

## 技术实现

### 后端逻辑

```python
async def execute_play_music(self, task_id: str, params: dict[str, Any]):
    song_name = params.get("song_name")
    device_id = params.get("device_id")
    
    # 如果没有指定设备，使用默认设备
    if not device_id:
        client = get_client()
        device_id = client.device_id
    
    # 在指定设备上播放
    await self.music_service.play_song(song["id"], device_id=device_id)
```

### 前端界面

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

1. **设备ID格式**
   - 字符串类型
   - 区分大小写
   - 可通过设备列表API查询

2. **设备在线状态**
   - 确保设备在线且可访问
   - 设备离线会导致任务执行失败

3. **默认设备**
   - 不指定设备时使用配置文件中的默认设备
   - 确保默认设备配置正确

4. **快捷操作**
   - 快捷操作卡片不支持设备选择
   - 需要指定设备时使用完整的创建对话框

## 文件清单

### 修改的文件

```
backend/src/xiaoai_media/
└── scheduler_executor.py              (修改)

frontend/src/views/
└── SchedulerManager.vue               (修改)

docs/scheduler/
├── README.md                          (修改)
├── CHANGELOG.md                       (修改)
└── DEVICE_SELECTION_FEATURE.md        (新增)

DEVICE_SELECTION_UPDATE.md             (新增)
```

## 测试验证

### 后端测试
- ✅ 语法检查通过
- ✅ 所有执行方法支持 device_id 参数
- ✅ 默认设备逻辑正确

### 前端测试
- ✅ 语法检查通过
- ✅ 界面显示正确
- ✅ 表单处理正确

## 总结

成功统一了所有任务类型的设备选择功能：

✅ 后端所有执行方法支持 device_id 参数
✅ 前端界面统一显示设备选择字段
✅ 完善的文档和使用示例
✅ 代码质量良好，无语法错误

这个改进使得定时任务功能更加完整和一致，用户可以灵活地在不同设备上执行不同的任务，大大提升了多设备场景下的使用体验。

---

**实现者**: Kiro AI Assistant  
**完成日期**: 2026-03-26  
**版本**: v0.2.1
