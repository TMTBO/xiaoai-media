# 定时任务功能更新日志

## [v0.2.0] - 2026-03-26

### 新增功能

#### 定时执行指令 (command)
- ✅ 新增 `TaskType.COMMAND` 任务类型
- ✅ 支持定时执行任何语音指令
- ✅ 支持延迟执行语音指令
- ✅ 可指定在特定设备上执行指令
- ✅ 指令通过统一的语音命令处理流程执行
- ✅ 支持所有语音命令功能（播放音乐、播放列表、搜索等）

#### 设备选择功能增强
- ✅ 所有任务类型现在都支持设备选择
- ✅ 播放音乐任务支持指定设备
- ✅ 播放播放列表任务支持指定设备
- ✅ 提醒任务支持指定设备
- ✅ 执行指令任务支持指定设备
- ✅ 不指定设备时自动使用默认设备

#### API 端点
- ✅ `POST /api/scheduler/quick/command` - 快速创建定时/延迟执行指令任务
  - 支持 Cron 表达式定时执行
  - 支持延迟分钟数延迟执行
  - 可选指定设备ID

#### 实现细节
- 在 `SchedulerExecutor` 中添加 `execute_command` 方法
- 所有执行方法都支持 `device_id` 参数
- 集成 `CommandHandler` 处理指令执行
- 在 `main.py` 中注册 command 任务回调
- 支持自动使用默认设备或指定设备

#### 前端功能
- ✅ 快捷操作面板新增"定时/延迟执行指令"卡片
- ✅ 创建对话框所有任务类型都显示设备选择字段
- ✅ 任务列表支持筛选执行指令任务
- ✅ 完整的表单验证和错误提示

#### 文档
- ✅ [定时执行指令功能说明](./COMMAND_EXECUTION.md)
- ✅ [使用示例](./COMMAND_EXAMPLES.md)
- ✅ [前端功能指南](./FRONTEND_COMMAND_GUIDE.md)
- ✅ [前端界面参考](./FRONTEND_UI_REFERENCE.md)
- ✅ 更新主 README 文档

#### 测试
- ✅ 添加 `test_command_scheduler.py` 测试文件
- ✅ 测试指令执行逻辑
- ✅ 测试任务创建和管理

### 使用示例

定时执行：
```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "播放周杰伦的歌",
    "cron_expression": "0 7 * * *"
  }'
```

延迟执行：
```bash
curl -X POST "http://localhost:8000/api/scheduler/quick/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "停止播放",
    "delay_minutes": 30
  }'
```

---

## [v0.1.0] - 2024-03-20

### 新增功能

#### 核心功能
- ✅ 基于 APScheduler 的定时任务调度系统
- ✅ 支持 Cron 表达式（周期性任务）
- ✅ 支持一次性定时任务
- ✅ 支持延迟任务（如：10分钟后提醒）
- ✅ 任务持久化到 Home 目录（`~/.xiaoai_media/scheduler/tasks.json`）
- ✅ 应用重启后自动恢复任务
- ✅ 过期任务自动清理

#### 任务类型
- ✅ 定时播放音乐（play_music）
  - 支持按歌曲名称和歌手搜索
  - 自动播放搜索到的第一首歌曲
  - 未找到歌曲时语音提示
  
- ✅ 定时播放播放列表（play_playlist）
  - 支持按播放列表ID播放
  - 播放列表不存在或为空时语音提示
  
- ✅ 定时提醒（reminder）
  - 使用 TTS 语音播报提醒内容
  - 支持自定义提醒文本

#### API 端点

##### 基础任务管理
- `POST /api/scheduler/tasks/cron` - 创建 Cron 定时任务
- `POST /api/scheduler/tasks/date` - 创建一次性定时任务
- `POST /api/scheduler/tasks/delay` - 创建延迟任务
- `GET /api/scheduler/tasks` - 列出所有任务（支持按类型筛选）
- `GET /api/scheduler/tasks/{task_id}` - 获取任务详情
- `PUT /api/scheduler/tasks/{task_id}` - 更新任务
- `DELETE /api/scheduler/tasks/{task_id}` - 删除任务

##### 快捷操作
- `POST /api/scheduler/quick/reminder` - 快速创建提醒
- `POST /api/scheduler/quick/play-music` - 快速创建定时播放音乐
- `POST /api/scheduler/quick/play-playlist` - 快速创建定时播放播放列表

#### 技术实现
- 使用 AsyncIOScheduler 支持异步任务执行
- 任务回调注册机制，易于扩展新任务类型
- 完整的错误处理和日志记录
- 时区设置为 Asia/Shanghai
- 任务元数据与调度器分离，便于持久化

#### 文档
- ✅ 完整的 API 文档（README.md）
- ✅ 快速开始指南（QUICK_START.md）
- ✅ 前端开发指南（FRONTEND_GUIDE.md）
- ✅ 更新日志（CHANGELOG.md）

#### 测试
- ✅ 完整的单元测试套件
- ✅ 测试覆盖所有核心功能
- ✅ 持久化和恢复测试
- ✅ 过期任务清理测试

### 依赖更新
- 新增 `apscheduler>=3.10.0` 依赖

### 文件变更

#### 新增文件
```
backend/src/xiaoai_media/services/scheduler_service.py
backend/src/xiaoai_media/scheduler_executor.py
backend/src/xiaoai_media/api/routes/scheduler.py
backend/tests/test_scheduler.py
docs/scheduler/README.md
docs/scheduler/QUICK_START.md
docs/scheduler/FRONTEND_GUIDE.md
docs/scheduler/CHANGELOG.md
```

#### 修改文件
```
backend/pyproject.toml - 添加 apscheduler 依赖
backend/src/xiaoai_media/api/main.py - 集成调度器服务
```

### 使用示例

#### 创建每天早上7点播放音乐
```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-music \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "晴天",
    "artist": "周杰伦",
    "cron_expression": "0 7 * * *"
  }'
```

#### 创建10分钟后提醒
```bash
curl -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": "该喝水了",
    "delay_minutes": 10
  }'
```

#### 创建工作日晚上8点播放播放列表
```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-playlist \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_id": "relax-playlist",
    "cron_expression": "0 20 * * 1-5"
  }'
```

### 数据存储

任务配置保存在：`~/.xiaoai_media/scheduler/tasks.json`

### 已知限制

1. 延迟提醒最长支持 1440 分钟（24小时）
2. 任务执行失败不会自动重试（会记录日志）
3. 暂不支持任务执行历史记录
4. 暂不支持任务分组管理

### 后续计划

#### v0.2.0 计划
- [ ] 任务执行历史记录
- [ ] 任务执行失败通知
- [ ] 批量操作 API
- [ ] 任务分组管理
- [ ] 导入/导出任务配置
- [ ] Cron 表达式可视化编辑器（前端）
- [ ] 任务执行统计

#### v0.3.0 计划
- [ ] 更多任务类型（音量控制、设备控制等）
- [ ] 任务依赖关系
- [ ] 条件触发（如：天气、时间段等）
- [ ] 任务优先级
- [ ] 并发控制优化

### 贡献者
- 初始实现：AI Assistant

### 反馈

如有问题或建议，请提交 Issue 或 Pull Request。
