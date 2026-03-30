# XiaoAI Media

<div align="center">
  <img src="logo.svg" alt="XiaoAI Media Logo" width="150" />
  <p><strong>小爱音箱媒体控制系统 - 让你的小爱音箱更智能</strong></p>
</div>

一个功能强大的小米/小爱音箱控制系统，提供 Web 管理界面和 REST API，支持音乐播放、播放列表管理、定时任务、语音命令等功能。

[![GitHub stars](https://img.shields.io/github/stars/tmtbo/xiaoai-media?style=social)](https://github.com/tmtbo/xiaoai-media)
[![Docker Pulls](https://img.shields.io/docker/pulls/thrillerone/xiaoai-media)](https://hub.docker.com/r/thrillerone/xiaoai-media)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ 功能特性

### 核心功能
- 🎵 **音乐播放** - 搜索和播放音乐，支持多平台（QQ音乐、网易云等）
- 📋 **播放列表** - 创建和管理播放列表，支持语音命令播放
- 📁 **批量导入** - 从目录批量导入音频文件，支持自然排序
- ⏰ **定时任务** - 定时播放音乐、播放列表，定时提醒
- 🎤 **语音命令** - 执行自定义语音命令，支持智能解析

### 控制功能
- 🔊 **音量控制** - 调节设备音量
- 💬 **TTS 播报** - 文本转语音播报
- 🎧 **对话监听** - 自动拦截和处理音箱播放指令
- 📱 **设备管理** - 管理多个小爱音箱设备

### 安全功能
- 🔐 **用户认证** - 基于JWT的用户登录系统
- 👥 **用户管理** - 管理员可以创建和管理用户账户
- 🛡️ **权限控制** - 基于角色的访问控制（管理员/普通用户）

### 管理界面
- 🖥️ **Web 界面** - 现代化的 Vue 3 管理界面
- 📊 **实时状态** - 实时显示设备状态和播放信息
- 🎨 **响应式设计** - 支持桌面和移动设备

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

使用 Docker Compose 一键启动：

```bash
# 1. 克隆项目
git clone https://github.com/tmtbo/xiaoai-media.git
cd xiaoai-media

# 2. 创建配置文件
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
cp music_provider_template.py ./data/music_provider.py

# 3. 编辑配置（填入小米账号信息）
vim ./data/user_config.py

# 4. 启动服务
docker-compose up -d

# 5. 访问管理界面
# 浏览器打开 http://localhost:8000
# 默认账号: admin / admin123
```

也可以直接使用预构建镜像：

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

可用镜像：
- `ghcr.io/tmtbo/xiaoai-media:latest` (GitHub Container Registry)
- `thrillerone/xiaoai-media:latest` (Docker Hub)

详见：[Docker 部署指南](docs/deployment/DOCKER_GUIDE.md)

### 方式二：本地开发

```bash
# 1. 克隆项目
git clone https://github.com/tmtbo/xiaoai-media.git
cd xiaoai-media

# 2. 安装依赖
make install

# 3. 配置服务
cp user_config_template.py user_config.py
cp music_provider_template.py music_provider.py
vim user_config.py  # 编辑配置

# 4. 启动服务
make dev

# 5. 访问管理界面
# 后端：http://localhost:8000
# 前端：http://localhost:5173
# 默认账号: admin / admin123
```

详见：[快速开始指南](QUICK_START.md)

---

## ⚙️ 配置说明

### 基础配置

在 `user_config.py` 中配置小米账号信息：

```python
# 小米账号（必填）
MI_USER = "your_account@example.com"
MI_PASS = "your_password"

# 默认设备ID（可选，不填则使用第一个设备）
MI_DID = "123456789"

# 本服务地址（必填，必须使用音箱可访问的局域网 IP）
SERVER_BASE_URL = "http://192.168.1.100:8000"
```

### 音乐服务配置

在 `music_provider.py` 中配置音乐 API：

```python
# 音乐 API 地址（如使用 NeteaseCloudMusicApi）
MUSIC_API_BASE_URL = "http://localhost:5050"

# 或使用其他音乐服务
# MUSIC_API_BASE_URL = "http://your-music-api.com"
```

### 高级配置

```python
# 唤醒词配置
WAKE_WORDS = ["小爱", "播放"]
ENABLE_WAKE_WORD_FILTER = True

# 日志配置
LOG_LEVEL = "INFO"

# 自定义音频 URL 获取（可选）
def get_audio_url(audio_id: str, custom_params: dict = None) -> str:
    """自定义音频 URL 获取逻辑"""
    return f"http://your-music-api.com/song/{audio_id}"
```

详见：[配置指南](docs/config/README.md) | [用户配置详解](docs/config/USER_CONFIG_GUIDE.md)

---

## 📊 数据存储

| 环境 | HOME 设置 | 数据目录 |
|------|-----------|---------|
| 开发 | `HOME=.` | `./` |
| Docker | `HOME=/data` | `/data/` |

```
$HOME/
├── user_config.py      # 配置文件
├── conversation.db     # 对话历史
├── playlists/          # 播放列表（多文件存储）
│   ├── index.json      # 播单索引
│   └── {id}.json       # 各播单数据
└── logs/               # 日志文件
```

**播单存储优化**（v1.0+）：
- 采用多文件存储，提升性能
- 列表加载速度提升 80-90%
- 支持自动迁移：`python scripts/migrate_playlists.py`

详见：[数据存储说明](docs/config/DATA_STORAGE.md) | [播单重构说明](docs/playlist/PLAYLIST_STORAGE_REFACTOR.md)

---

## 📚 文档导航

### 🚀 快速上手
- [入门指南](docs/GETTING_STARTED.md) - 快速了解和开始使用
- [快速开始](QUICK_START.md) - 5 分钟快速上手
- [用户使用指南](docs/USER_GUIDE.md) - 完整使用指南
- [Docker 部署](docs/deployment/DOCKER_GUIDE.md) - Docker 完整指南
- [配置指南](docs/config/README.md) - 配置文件详解
- [用户认证](docs/USER_AUTH_QUICKSTART.md) - 登录和用户管理快速开始

### 📖 功能文档
- [功能特性详解](docs/FEATURES.md) - 所有功能的详细说明
- [用户认证系统](docs/USER_AUTH.md) - 用户登录和权限管理
- [播放列表管理](docs/playlist/README.md) - 创建和管理播放列表
- [批量导入功能](docs/playlist/README_BATCH_IMPORT.md) - 从目录批量导入音频文件
- [定时任务](docs/scheduler/README.md) - 定时播放和提醒功能
- [对话监听](docs/conversation/README.md) - 自动拦截播放指令
- [TTS 语音](docs/tts/README.md) - 文字转语音播报
- [音乐播放](docs/playback/README.md) - 音乐搜索和播放

### 💻 开发文档
- [API 参考](docs/api/README.md) - REST API 完整文档
- [项目结构](docs/STRUCTURE.md) - 代码结构说明
- [服务层架构](backend/src/xiaoai_media/services/README.md) - 服务层设计
- [前端开发](docs/frontend/README.md) - 前端开发文档
- [重构文档](docs/refactor/README.md) - 架构重构说明

### 🔄 升级指南
- [迁移指南](docs/migration/README.md) - 版本升级说明
- [更新日志](CHANGELOG.md) - 版本更新记录

### 📑 完整索引
- [文档中心](docs/README.md) - 所有文档的完整索引
- [文档索引表](docs/INDEX.md) - 文档快速查找表

---

## 🔌 API 示例

### 基础控制

```bash
# TTS 播报
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "您好", "device_id": "xxx"}'

# 执行语音命令
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"text": "播放周杰伦的歌", "device_id": "xxx"}'

# 音量控制
curl -X POST http://localhost:8000/api/volume \
  -H "Content-Type: application/json" \
  -d '{"volume": 50, "device_id": "xxx"}'

# 获取设备列表
curl http://localhost:8000/api/devices
```

### 播放列表

```bash
# 创建播放列表
curl -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的音乐",
    "type": "music",
    "voice_keywords": ["音乐", "歌曲"]
  }'

# 播放播放列表
curl -X POST http://localhost:8000/api/playlists/{id}/play \
  -H "Content-Type: application/json" \
  -d '{"device_id": "xxx", "start_index": 0}'
```

### 定时任务

```bash
# 创建定时播放任务
curl -X POST http://localhost:8000/api/scheduler/quick/play-music \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "晴天",
    "artist": "周杰伦",
    "cron_expression": "0 7 * * *"
  }'

# 创建延迟提醒
curl -X POST http://localhost:8000/api/scheduler/quick/reminder \
  -H "Content-Type: application/json" \
  -d '{"message": "该喝水了", "delay_minutes": 30}'
```

详见：[API 完整文档](docs/api/README.md)

---

## 🛠️ 技术栈

### 后端
- **Python 3.11+** - 现代 Python 特性
- **FastAPI** - 高性能 Web 框架
- **SQLite** - 轻量级数据库
- **aiohttp** - 异步 HTTP 客户端
- **APScheduler** - 定时任务调度

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Element Plus** - UI 组件库
- **Vue Router** - 路由管理

### 部署
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排

### 架构设计
- **分层架构** - 路由层、服务层、数据层分离
- **服务化设计** - 可复用的服务组件
- **RESTful API** - 标准化接口设计

详见：[项目结构](docs/STRUCTURE.md) | [服务层架构](backend/src/xiaoai_media/services/README.md)

---

## 📱 支持的设备

支持所有小米/小爱音箱系列设备：

- 小米智能音箱 Pro (OH2P)
- 小米智能音箱 (LX06)
- 小爱音箱 Play (LX01)
- 小爱音箱 mini (LX04)
- Redmi 小爱音箱 Play (X10A)
- Redmi 小爱音箱 (X6A)
- 其他小米生态链音箱设备

通过 MiService 协议与设备通信，理论上支持所有小米 IoT 音箱设备。

---

## 💡 使用场景

### 场景 1：智能音乐播放
创建多个播放列表（音乐、有声书、播客等），通过语音命令快速切换：
- "小爱，播放音乐播单"
- "小爱，播放有声书"

### 场景 2：定时播放
设置定时任务，让音箱在指定时间自动播放：
- 每天早上 7 点播放起床音乐
- 工作日晚上 8 点播放放松音乐
- 每 2 小时提醒喝水

### 场景 3：批量导入音频
从本地目录批量导入音频文件，自动创建播放列表：
- 导入有声书章节（支持自然排序）
- 导入播客节目
- 导入音乐专辑

### 场景 4：自定义音频源
通过 `get_audio_url()` 函数集成任意音频源：
- 本地 NAS 音乐库
- 自建音乐服务
- 第三方音频平台

---

## 🐳 Docker 镜像

### 镜像仓库

- **GitHub Container Registry**: `ghcr.io/tmtbo/xiaoai-media:latest`
- **Docker Hub**: `thrillerone/xiaoai-media:latest`

### 镜像标签

- `latest` - 最新稳定版本
- `v1.x.x` - 特定版本号

### 拉取镜像

```bash
# 从 GitHub Container Registry
docker pull ghcr.io/tmtbo/xiaoai-media:latest

# 从 Docker Hub
docker pull thrillerone/xiaoai-media:latest
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

在提交 PR 之前，请确保：
- 代码通过类型检查和测试
- 遵循项目的代码风格
- 更新相关文档

详见：[贡献指南](docs/CONTRIBUTING.md)

---

## 🔗 相关链接

- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
- [问题反馈](https://github.com/tmtbo/xiaoai-media/issues)
- [更新日志](CHANGELOG.md)
- [MiService Fork](https://github.com/yihong0618/MiService)

---

## 📄 许可证

MIT License

---

## ⭐ Star History

如果这个项目对你有帮助，欢迎给个 Star！
