# 项目结构

XiaoAI Media 项目的目录结构说明。

---

## 项目根目录

```
xiaoai-media/
├── backend/                # 后端代码
├── frontend/               # 前端代码
├── docs/                   # 文档目录
├── scripts/                # 工具脚本
├── test/                   # 测试代码
├── Makefile               # 开发命令
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile             # Docker 镜像构建
├── README.md              # 项目说明
├── QUICK_START.md         # 快速开始
└── user_config_template.py # 配置模板
```

---

## 后端结构

```
backend/
├── src/
│   └── xiaoai_media/
│       ├── __init__.py
│       ├── config.py           # 配置管理
│       ├── client.py           # 小米 AI 客户端
│       ├── player.py           # 播放器
│       ├── conversation.py     # 对话监听
│       ├── command_handler.py  # 指令处理
│       └── api/
│           ├── main.py         # FastAPI 应用
│           └── routes/         # API 路由
│               ├── config.py
│               ├── playlist.py
│               ├── conversation.py
│               └── ...
└── pyproject.toml
```

---

## 前端结构

```
frontend/
├── src/
│   ├── App.vue             # 主应用
│   ├── main.ts             # 入口文件
│   ├── api/                # API 客户端
│   ├── composables/        # 组合式函数
│   ├── router/             # 路由配置
│   └── views/              # 页面组件
│       ├── DeviceList.vue
│       ├── PlaylistManager.vue
│       ├── ConversationHistory.vue
│       └── ...
├── package.json
└── vite.config.ts
```

---

## 文档结构

```
docs/
├── README.md               # 文档中心
├── STRUCTURE.md            # 项目结构（本文件）
├── api/                    # API 文档
│   ├── README.md
│   └── API_REFERENCE.md
├── config/                 # 配置文档
│   ├── README.md
│   ├── DEV_ENVIRONMENT.md
│   └── DATA_STORAGE.md
├── deployment/             # 部署文档
│   ├── DOCKER_GUIDE.md
│   └── DOCKER_QUICK_START.md
├── playlist/               # 播放列表文档
├── conversation/           # 对话监听文档
├── playback/               # 音乐播放文档
├── tts/                    # TTS 文档
└── migration/              # 迁移指南
    ├── README.md
    └── HOME_DIR_MIGRATION.md
```

---

## 数据目录

### 开发环境

```
./                          # 项目根目录（HOME=.）
├── user_config.py          # 配置文件
├── conversation.db         # 对话历史
├── playlists/              # 播放列表
│   ├── default.json
│   └── favorites.json
└── .gitignore              # 已忽略数据文件
```

### Docker 环境

```
/data/                      # 容器内数据目录（HOME=/data）
├── user_config.py          # 配置文件
├── conversation.db         # 对话历史
└── playlists/              # 播放列表
```

---

## 核心模块

### config.py
- 配置文件加载
- 环境变量处理
- 数据目录管理

### client.py
- 小米 AI 设备通信
- 设备列表管理
- 指令发送

### player.py
- 音乐播放控制
- 播放列表管理
- 音频流处理

### conversation.py
- 对话历史监听
- 指令识别
- 自动响应

### command_handler.py
- 指令解析
- 音乐搜索
- 播放控制

---

## API 路由

| 路由 | 功能 | 文件 |
|------|------|------|
| `/api/devices` | 设备管理 | routes/devices.py |
| `/api/playlists` | 播放列表 | routes/playlist.py |
| `/api/conversation` | 对话历史 | routes/conversation.py |
| `/api/config` | 配置管理 | routes/config.py |
| `/api/tts` | TTS 语音 | routes/tts.py |

---

## 开发工具

### Makefile 命令

```bash
make install        # 安装依赖
make dev            # 启动开发环境
make backend        # 启动后端
make frontend       # 启动前端
make list-devices   # 列出设备
make clean          # 清理缓存
```

### 脚本工具

```bash
scripts/verify_config.sh              # 验证配置
scripts/diagnose_docker_storage.sh    # Docker 诊断
```

---

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLite
- aiohttp

### 前端
- Vue 3
- TypeScript
- Vite
- Element Plus

### 部署
- Docker
- Docker Compose
- Nginx（可选）

---

## 相关文档

- [快速开始](../QUICK_START.md)
- [配置指南](config/README.md)
- [API 文档](api/README.md)
- [Docker 部署](deployment/DOCKER_GUIDE.md)
