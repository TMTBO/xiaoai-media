# 项目结构

XiaoAI Media 项目的目录结构说明。

> **最新更新** ✨: 项目已完成架构重构，采用分层架构设计。详见 [重构总览](refactor/REFACTOR_SUMMARY.md)

---

## 架构概览

### 分层架构 ✨

项目采用清晰的三层架构：

```
┌─────────────────────────────────┐
│      API路由层 (Routes)          │  ← HTTP请求处理
└──────────────┬──────────────────┘
               │
┌─────────────────────────────────┐
│       服务层 (Services)          │  ← 业务逻辑处理
└──────────────┬──────────────────┘
               │
┌─────────────────────────────────┐
│    数据层 (Player, Client)       │  ← 数据持久化
└─────────────────────────────────┘
```

### 核心特点

- **关注点分离**: 路由层、服务层、数据层职责清晰
- **代码复用**: 服务层可被多个路由使用
- **易于测试**: 服务层可独立测试
- **易于维护**: 修改影响范围小

详见：[服务层文档](../backend/src/xiaoai_media/services/README.md)

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
│       │
│       ├── services/           # 服务层 ✨
│       │   ├── __init__.py
│       │   ├── README.md       # 服务层文档
│       │   ├── music_service.py          # 音乐服务
│       │   ├── config_service.py         # 配置服务
│       │   ├── playlist_service.py       # 播放列表服务
│       │   ├── playlist_storage.py       # 播放列表存储
│       │   ├── playlist_models.py        # 播放列表模型
│       │   ├── playlist_loader.py        # 播放列表加载
│       │   └── voice_command_service.py  # 语音命令服务
│       │
│       ├── playlist/           # 播放列表（兼容层）
│       │   └── __init__.py     # 转发到 services
│       │
│       └── api/
│           ├── main.py         # FastAPI 应用
│           └── routes/         # API 路由（仅处理HTTP）
│               ├── config.py
│               ├── music.py
│               ├── playlist.py
│               ├── conversation.py
│               └── ...
└── pyproject.toml
```

### 架构说明

#### 分层架构 ✨

```
┌─────────────────────────────────┐
│      API路由层 (Routes)          │
│  - HTTP请求处理                  │
│  - 参数验证                      │
│  - HTTP响应                      │
└──────────────┬──────────────────┘
               │ 调用
               ↓
┌─────────────────────────────────┐
│       服务层 (Services)          │
│  - 业务逻辑                      │
│  - 数据处理                      │
│  - 外部API调用                   │
│  - 数据转换                      │
└──────────────┬──────────────────┘
               │ 使用
               ↓
┌─────────────────────────────────┐
│    数据层 (Player, Client)       │
│  - 数据持久化                    │
│  - 外部服务交互                  │
└─────────────────────────────────┘
```

#### 服务层模块

- **music_service.py**: 音乐搜索、排行榜、平台验证
- **config_service.py**: 配置文件读写、验证
- **playlist_service.py**: 播放列表CRUD、播放控制
- **playlist_storage.py**: 播放列表文件存储
- **playlist_models.py**: 播放列表数据模型
- **playlist_loader.py**: 从不同来源加载播放列表
- **voice_command_service.py**: 语音命令解析和执行

详见：[服务层文档](../backend/src/xiaoai_media/services/README.md)

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
├── migration/              # 迁移指南
│   ├── README.md
│   └── HOME_DIR_MIGRATION.md
└── refactor/               # 重构文档 ✨
    ├── README.md
    ├── API_SERVICES_REFACTOR.md
    ├── API_REFACTOR_SUMMARY.md
    ├── SERVICES_QUICK_REFERENCE.md
    ├── PLAYLIST_SERVICES_MIGRATION.md
    └── PLAYLIST_MIGRATION_COMPLETE.md
```

---

## 数据目录

### 开发环境

```
./                          # 项目根目录（HOME=.）
├── user_config.py          # 配置文件
├── conversation.db         # 对话历史
├── playlists/              # 播放列表（多文件存储）✨
│   ├── index.json          # 播单索引
│   ├── 音乐_1234567890.json # 播单数据
│   └── 有声书_9876543210.json
└── .gitignore              # 已忽略数据文件
```

### Docker 环境

```
/data/                      # 容器内数据目录（HOME=/data）
├── user_config.py          # 配置文件
├── conversation.db         # 对话历史
└── playlists/              # 播放列表（多文件存储）✨
    ├── index.json          # 播单索引
    └── *.json              # 各播单数据
```

### 播放列表存储说明 ✨

从 v1.0 开始，播放列表采用多文件存储：
- `index.json`: 存储所有播单的索引信息（元数据）
- `{playlist_id}.json`: 存储每个播单的详细数据（播放项）

优势：
- 列表加载速度提升 80-90%
- 支持大量播单和播放项
- 减少内存占用

详见：[播单存储重构](playlist/PLAYLIST_STORAGE_REFACTOR.md)

---

## 核心模块

### 配置层

#### config.py
- 配置文件加载
- 环境变量处理
- 数据目录管理

### 服务层 ✨

#### MusicService (services/music_service.py)
- 音乐搜索
- 排行榜查询
- 平台验证
- 命令解析

#### ConfigService (services/config_service.py)
- 配置文件读写
- 配置验证
- 模块重载

#### PlaylistService (services/playlist_service.py)
- 播放列表CRUD
- 播放控制
- 语音命令播放
- URL代理

#### PlaylistStorage (services/playlist_storage.py)
- 文件存储管理
- 索引管理
- 数据持久化

#### PlaylistLoaderService (services/playlist_loader.py)
- 从搜索加载播放列表
- 从排行榜加载播放列表
- 从保存的播放列表加载

#### VoiceCommandService (services/voice_command_service.py)
- 语音命令解析
- 命令执行
- TTS播报

详见：[服务层文档](../backend/src/xiaoai_media/services/README.md)

### 数据层

#### client.py
- 小米 AI 设备通信
- 设备列表管理
- 指令发送

#### player.py
- 音乐播放控制
- 播放列表管理
- 音频流处理

#### conversation.py
- 对话历史监听
- 指令识别
- 自动响应

### 已弃用模块

#### command_handler.py
- ⚠️ 已被服务层替代
- 功能已迁移到 services/

---

## API 路由

所有路由文件位于 `backend/src/xiaoai_media/api/routes/`，只处理HTTP请求/响应，业务逻辑在服务层。

| 路由 | 功能 | 文件 | 服务层 |
|------|------|------|--------|
| `/api/devices` | 设备管理 | routes/devices.py | - |
| `/api/music/*` | 音乐控制 | routes/music.py | MusicService, PlaylistLoaderService |
| `/api/playlists/*` | 播放列表 | routes/playlist.py | PlaylistService |
| `/api/conversation/*` | 对话历史 | routes/conversation.py | - |
| `/api/config` | 配置管理 | routes/config.py | ConfigService |
| `/api/tts` | TTS 语音 | routes/tts.py | - |
| `/api/command` | 命令执行 | routes/command.py | VoiceCommandService |

### 架构特点 ✨

- **路由层**: 只处理HTTP请求/响应、参数验证
- **服务层**: 处理所有业务逻辑、数据处理
- **数据层**: 处理数据持久化、外部服务交互

详见：[API重构文档](refactor/API_SERVICES_REFACTOR.md)

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

## 代码使用示例

### 服务层使用 ✨

```python
# 导入服务
from xiaoai_media.services import (
    MusicService,
    ConfigService,
    PlaylistService,
    PlaylistLoaderService,
    VoiceCommandService,
)

# 使用音乐服务
results = await MusicService.search_music("周杰伦", "tx")

# 使用播放列表服务
playlist = PlaylistService.create_playlist(
    CreatePlaylistRequest(
        name="我的音乐",
        type="music",
        voice_keywords=["音乐"]
    )
)

# 使用配置服务
config = ConfigService.get_current_config()
```

### 路由层使用

```python
# 路由只处理HTTP请求/响应
from fastapi import APIRouter
from xiaoai_media.services import MusicService

router = APIRouter()

@router.get("/search")
async def search_music(query: str):
    # 调用服务层处理业务逻辑
    return await MusicService.search_music(query)
```

详见：[服务层快速参考](refactor/SERVICES_QUICK_REFERENCE.md)

---

## 相关文档

### 快速开始
- [快速开始](../QUICK_START.md)
- [配置指南](config/README.md)
- [Docker 部署](deployment/DOCKER_GUIDE.md)

### 架构文档 ✨
- [重构总览](refactor/REFACTOR_SUMMARY.md)
- [服务层架构](../backend/src/xiaoai_media/services/README.md)
- [API重构文档](refactor/API_SERVICES_REFACTOR.md)
- [服务层快速参考](refactor/SERVICES_QUICK_REFERENCE.md)

### 功能文档
- [API 文档](api/README.md)
- [播放列表功能](playlist/README.md)
- [对话监听功能](conversation/README.md)

### 重构文档
- [重构文档索引](refactor/README.md)
- [播放列表服务迁移](refactor/PLAYLIST_SERVICES_MIGRATION.md)
