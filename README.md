# XiaoAI Media

<div align="center">
  <img src="logo.svg" alt="XiaoAI Media Logo" width="150" />
  <p><strong>小爱音箱媒体控制系统 - 让你的小爱音箱更智能</strong></p>
</div>

---

## ✨ 功能特性

- 🎵 音乐播放控制
- 🔊 音量控制
- 💬 TTS 文本转语音
- 🎤 语音命令执行
- 📱 设备管理
- 🎧 对话监听 - 自动拦截音箱播放指令
- 📋 播放列表管理
- 📁 批量导入 - 从目录批量导入音频文件

---

## 🚀 快速开始

### Docker 部署（推荐）

#### 方式 1：使用预构建镜像

```bash
# 1. 创建数据目录和配置文件
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
vim ./data/user_config.py  # 编辑配置

# 2. 拉取并运行镜像
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

可用镜像：
- `ghcr.io/tmtbo/xiaoai-media:latest` (GitHub Container Registry)
- `thrillerone/xiaoai-media:latest` (Docker Hub)

#### 方式 2：使用 Docker Compose

```bash
# 1. 创建数据目录和配置文件
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
vim ./data/user_config.py  # 编辑配置

# 2. 启动服务
docker-compose up -d
```

访问 http://localhost:8000 即可使用。

详见：[Docker 部署指南](docs/deployment/DOCKER_GUIDE.md)

### 本地开发

```bash
# 1. 安装依赖
make install

# 2. 配置服务
cp user_config_template.py user_config.py
vim user_config.py  # 编辑配置

# 3. 启动服务
make dev
```

详见：[快速开始指南](QUICK_START.md)

---

## ⚙️ 配置说明

### 必填配置

```python
# user_config.py
MI_USER = "你的小米账号"
MI_PASS = "你的密码"
MI_DID = "设备ID"  # 可选
```

### 可选配置

```python
# 音乐 API 地址
MUSIC_API_BASE_URL = "http://localhost:5050"

# 本服务地址（必须使用音箱可访问的局域网 IP）
SERVER_BASE_URL = "http://192.168.1.100:8000"

# 唤醒词配置
WAKE_WORDS = ["小爱", "播放"]
ENABLE_WAKE_WORD_FILTER = True
```

详见：[配置指南](docs/config/README.md)

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

## 📚 文档

### 核心文档
- [快速开始](QUICK_START.md) - 5 分钟快速上手
- [文档中心](docs/README.md) - 完整文档索引
- [配置指南](docs/config/README.md) - 配置文件详解
- [项目结构](docs/STRUCTURE.md) - 代码结构说明

### 功能文档
- [播放列表管理](docs/playlist/README.md) - 播放列表功能
- [批量导入功能](docs/playlist/README_BATCH_IMPORT.md) - 从目录批量导入音频文件 ⭐
- [对话监听](docs/conversation/README.md) - 对话监听功能
- [TTS 语音](docs/tts/README.md) - 文字转语音
- [音乐播放](docs/playback/README.md) - 音乐播放功能

### 部署文档
- [Docker 部署](docs/deployment/DOCKER_GUIDE.md) - Docker 完整指南
- [开发环境](docs/config/DEV_ENVIRONMENT.md) - 本地开发配置

### 开发文档
- [API 参考](docs/api/README.md) - REST API 文档
- [迁移指南](docs/migration/README.md) - 版本升级说明
- [重构总结](REFACTOR_SUMMARY.md) - 架构重构说明 ✨
- [重构文档](docs/refactor/README.md) - 详细重构文档

---

## 🔌 API 示例

### TTS 播报
```bash
POST /api/tts
{
  "text": "您好",
  "device_id": "xxx"
}
```

### 执行命令
```bash
POST /api/command
{
  "text": "播放音乐",
  "device_id": "xxx",
  "silent": false
}
```

### 音量控制
```bash
POST /api/volume
{
  "volume": 50,
  "device_id": "xxx"
}
```

### 设备列表
```bash
GET /api/devices
```

详见：[API 文档](docs/api/README.md)

---

## 🛠️ 技术栈

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

---

## 📱 支持的设备

支持所有小米/小爱音箱系列：
- 小米智能音箱 Pro (OH2P)
- 小爱音箱系列 (LX06, LX01, LX04)
- Redmi 小爱音箱系列 (X10A, X6A)

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

## 🔗 相关链接

- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
- [更新日志](CHANGELOG.md)
- [问题反馈](https://github.com/tmtbo/xiaoai-media/issues)
- [MiService Fork](https://github.com/yihong0618/MiService)

---

## 📄 许可证

MIT License
