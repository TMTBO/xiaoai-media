# 定时任务功能

## 概述

已成功集成基于 APScheduler 的定时任务功能，支持：

- ✅ 定时播放音乐
- ✅ 定时播放播放列表  
- ✅ 定时提醒（如：10分钟后提醒我）
- ✅ 任务持久化到 Home 目录
- ✅ 完整的管理 API
- ✅ 应用重启后自动恢复任务

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -e .
```

### 2. 启动应用

```bash
cd backend
python run.py
```

### 3. 创建第一个任务

```bash
# 10分钟后提醒
curl -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": "该喝水了",
    "delay_minutes": 10
  }'
```

## 文档导航

### 📚 核心文档
- [完整 API 文档](docs/scheduler/README.md) - 详细的 API 说明和使用指南
- [快速开始指南](docs/scheduler/QUICK_START.md) - 5分钟上手定时任务
- [实现总结](docs/scheduler/IMPLEMENTATION_SUMMARY.md) - 技术实现细节

### 🎨 前端开发
- [前端开发指南](docs/scheduler/FRONTEND_GUIDE.md) - 管理后台开发参考

### 📝 其他
- [更新日志](docs/scheduler/CHANGELOG.md) - 版本更新记录

## 主要功能

### 1. 定时播放音乐

每天早上7点播放起床音乐：

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-music \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "晴天",
    "artist": "周杰伦",
    "cron_expression": "0 7 * * *"
  }'
```

### 2. 定时播放播放列表

工作日晚上8点播放放松音乐：

```bash
curl -X POST http://localhost:8000/api/scheduler/quick/play-playlist \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_id": "relax-playlist",
    "cron_expression": "0 20 * * 1-5"
  }'
```

### 3. 定时提醒

每2小时提醒喝水：

```bash
curl -X POST http://localhost:8000/api/scheduler/tasks/cron \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reminder",
    "name": "喝水提醒",
    "cron_expression": "0 */2 * * *",
    "params": {
      "message": "该喝水了"
    }
  }'
```

## API 端点

### 基础管理
- `POST /api/scheduler/tasks/cron` - 创建 Cron 定时任务
- `POST /api/scheduler/tasks/date` - 创建一次性定时任务
- `POST /api/scheduler/tasks/delay` - 创建延迟任务
- `GET /api/scheduler/tasks` - 列出所有任务
- `GET /api/scheduler/tasks/{id}` - 获取任务详情
- `PUT /api/scheduler/tasks/{id}` - 更新任务
- `DELETE /api/scheduler/tasks/{id}` - 删除任务

### 快捷操作
- `POST /api/scheduler/quick/reminder` - 快速提醒
- `POST /api/scheduler/quick/play-music` - 快速播放音乐
- `POST /api/scheduler/quick/play-playlist` - 快速播放播放列表

## Cron 表达式速查

格式：`分 时 日 月 周`

| 表达式 | 说明 |
|--------|------|
| `0 7 * * *` | 每天早上7点 |
| `30 20 * * *` | 每天晚上8点30分 |
| `0 */2 * * *` | 每2小时 |
| `0 7 * * 1-5` | 周一到周五早上7点 |
| `0 12 * * 0` | 每周日中午12点 |

## 数据持久化

任务配置保存在：`~/.xiaoai_media/scheduler/tasks.json`

应用重启后会自动恢复所有任务。

## 测试

运行测试套件：

```bash
cd backend
pytest tests/test_scheduler.py -v
```

## API 文档

启动应用后访问 Swagger 文档：

```
http://localhost:8000/docs
```

## 技术栈

- APScheduler 3.10+ - 任务调度
- FastAPI - Web 框架
- Pydantic - 数据验证
- AsyncIO - 异步执行

## 架构

```
用户请求 → API 路由 → 调度服务 → 持久化
                          ↓
                    添加到调度器
                          ↓
                    定时触发执行
                          ↓
                    任务执行器 → 音乐/播放列表/TTS服务
```

## 文件结构

```
backend/src/xiaoai_media/
├── services/
│   └── scheduler_service.py      # 调度服务核心
├── scheduler_executor.py          # 任务执行器
└── api/routes/
    └── scheduler.py               # API 路由

backend/tests/
└── test_scheduler.py              # 单元测试

docs/scheduler/
├── README.md                      # 完整文档
├── QUICK_START.md                 # 快速开始
├── FRONTEND_GUIDE.md              # 前端指南
├── CHANGELOG.md                   # 更新日志
└── IMPLEMENTATION_SUMMARY.md      # 实现总结
```

## 下一步

1. 阅读 [快速开始指南](docs/scheduler/QUICK_START.md) 了解基本用法
2. 查看 [API 文档](docs/scheduler/README.md) 了解所有功能
3. 参考 [前端开发指南](docs/scheduler/FRONTEND_GUIDE.md) 开发管理界面
4. 运行测试验证功能

## 反馈

如有问题或建议，欢迎提交 Issue 或 Pull Request。
