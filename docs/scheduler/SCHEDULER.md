# 定时任务功能

## 概述

已集成完整的定时任务功能，支持通过 Web 界面管理定时任务。

## 功能特性

- ✅ 定时播放音乐
- ✅ 定时播放播放列表
- ✅ 定时提醒（如：10分钟后提醒我）
- ✅ 任务持久化到 Home 目录
- ✅ Web 管理界面
- ✅ 应用重启后自动恢复任务

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -e .
```

### 2. 启动服务

```bash
# 启动后端
cd backend
python run.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 3. 访问管理界面

打开浏览器访问：http://localhost:5173

在左侧菜单点击 **"定时任务"**

## 快速测试

运行自动化测试脚本：

```bash
./scripts/test_scheduler.sh
```

## 使用示例

### 创建 10 分钟后的提醒

在"快速提醒"卡片中：
- 提醒内容：`该喝水了`
- 延迟分钟数：`10`
- 点击"创建提醒"

### 每天早上 7 点播放音乐

在"定时播放音乐"卡片中：
- 歌曲名称：`晴天`
- 歌手：`周杰伦`
- Cron 表达式：`0 7 * * *`
- 点击"创建任务"

## Cron 表达式速查

格式：`分 时 日 月 周`

| 表达式 | 说明 |
|--------|------|
| `0 7 * * *` | 每天早上7点 |
| `30 20 * * *` | 每天晚上8点30分 |
| `0 */2 * * *` | 每2小时 |
| `0 7 * * 1-5` | 周一到周五早上7点 |
| `0 12 * * 0` | 每周日中午12点 |

## 文档导航

| 文档 | 说明 |
|------|------|
| [使用说明](docs/scheduler/SCHEDULER_README.md) | 详细使用指南 |
| [快速开始](docs/scheduler/QUICK_START.md) | 5分钟上手 |
| [完整指南](docs/scheduler/COMPLETE_GUIDE.md) | 完整功能说明 |
| [API 文档](docs/scheduler/README.md) | API 参考 |
| [前端测试](docs/scheduler/FRONTEND_TEST.md) | 测试步骤 |
| [功能概览](docs/scheduler/SCHEDULER_FEATURE.md) | 功能介绍 |
| [实现总结](docs/scheduler/SCHEDULER_IMPLEMENTATION_COMPLETE.md) | 实现细节 |

## API 端点

```
POST   /api/scheduler/tasks/cron           创建 Cron 任务
POST   /api/scheduler/tasks/date           创建一次性任务
POST   /api/scheduler/tasks/delay          创建延迟任务
GET    /api/scheduler/tasks                列出所有任务
GET    /api/scheduler/tasks/{id}           获取任务详情
PUT    /api/scheduler/tasks/{id}           更新任务
DELETE /api/scheduler/tasks/{id}           删除任务
POST   /api/scheduler/quick/reminder       快速提醒
POST   /api/scheduler/quick/play-music     快速播放音乐
POST   /api/scheduler/quick/play-playlist  快速播放播放列表
```

完整 API 文档：http://localhost:8000/docs

## 技术栈

- **后端**：Python 3.9+, FastAPI, APScheduler 3.10+
- **前端**：Vue 3, TypeScript, Element Plus

## 文件位置

```
backend/src/xiaoai_media/
├── services/scheduler_service.py      # 调度服务
├── scheduler_executor.py              # 任务执行器
└── api/routes/scheduler.py            # API 路由

frontend/src/
├── api/scheduler.ts                   # API 客户端
└── views/SchedulerManager.vue         # 管理页面

docs/scheduler/                        # 完整文档
scripts/test_scheduler.sh              # 测试脚本
```

## 数据存储

任务配置保存在：`~/.xiaoai_media/scheduler/tasks.json`

## 故障排查

### 任务不执行
- 检查任务是否启用
- 检查 Cron 表达式是否正确
- 查看后端日志

### 页面空白
- 检查后端是否运行（http://localhost:8000）
- 检查浏览器控制台错误
- 检查 API 请求状态

详细故障排查：[完整指南](docs/scheduler/COMPLETE_GUIDE.md)

## 版本信息

- **版本**：v0.1.0
- **状态**：✅ 完成并可用
- **更新时间**：2024-03-20

---

更多信息请查看 [详细文档](docs/scheduler/)
