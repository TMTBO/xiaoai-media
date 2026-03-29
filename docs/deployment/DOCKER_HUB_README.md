# XiaoAI Media

<div align="center">
  <p><strong>小爱音箱媒体控制系统 - 让你的小爱音箱更智能</strong></p>
</div>

一个功能强大的小米/小爱音箱控制系统，提供 Web 管理界面和 REST API，支持音乐播放、播放列表管理、定时任务、语音命令等功能。

[![GitHub stars](https://img.shields.io/github/stars/tmtbo/xiaoai-media?style=social)](https://github.com/tmtbo/xiaoai-media)
[![Docker Pulls](https://img.shields.io/docker/pulls/thrillerone/xiaoai-media)](https://hub.docker.com/r/thrillerone/xiaoai-media)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/tmtbo/xiaoai-media/blob/main/LICENSE)

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

### 管理界面
- 🖥️ **Web 界面** - 现代化的 Vue 3 管理界面
- 📊 **实时状态** - 实时显示设备状态和播放信息
- 🎨 **响应式设计** - 支持桌面和移动设备

---

## 🚀 快速开始

### 使用 Docker Compose（推荐）

```bash
# 1. 创建项目目录
mkdir xiaoai-media && cd xiaoai-media

# 2. 下载 docker-compose.yml
wget https://raw.githubusercontent.com/tmtbo/xiaoai-media/main/docker-compose.yml

# 3. 创建配置文件
mkdir -p ./data
wget -O ./data/user_config.py https://raw.githubusercontent.com/tmtbo/xiaoai-media/main/user_config_template.py
wget -O ./data/music_provider.py https://raw.githubusercontent.com/tmtbo/xiaoai-media/main/music_provider_template.py

# 4. 编辑配置（填入小米账号信息）
vim ./data/user_config.py

# 5. 启动服务
docker-compose up -d

# 6. 访问管理界面
# 浏览器打开 http://localhost:8000
```

### 使用 Docker Run

```bash
# 1. 创建数据目录
mkdir -p ./data

# 2. 下载配置模板
wget -O ./data/user_config.py https://raw.githubusercontent.com/tmtbo/xiaoai-media/main/user_config_template.py
wget -O ./data/music_provider.py https://raw.githubusercontent.com/tmtbo/xiaoai-media/main/music_provider_template.py

# 3. 编辑配置
vim ./data/user_config.py

# 4. 运行容器
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  --restart unless-stopped \
  thrillerone/xiaoai-media:latest

# 5. 查看日志
docker logs -f xiaoai-media
```

---

## ⚙️ 配置说明

### 基础配置

在 `./data/user_config.py` 中配置小米账号信息：

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

在 `./data/music_provider.py` 中配置音乐 API：

```python
# 音乐 API 地址（如使用 NeteaseCloudMusicApi）
MUSIC_API_BASE_URL = "http://localhost:5050"
```

### 数据持久化

容器使用 `/data` 目录存储所有数据：

```
/data/
├── user_config.py      # 配置文件
├── music_provider.py   # 音乐服务配置
├── conversation.db     # 对话历史
├── playlists/          # 播放列表
└── logs/               # 日志文件
```

确保挂载 `-v $(pwd)/data:/data` 以持久化数据。

---

## 🐳 镜像信息

### 镜像仓库

- **Docker Hub**: `thrillerone/xiaoai-media:latest`
- **GitHub Container Registry**: `ghcr.io/tmtbo/xiaoai-media:latest`

### 镜像标签

- `latest` - 最新稳定版本
- `v1.x.x` - 特定版本号

### 镜像大小

约 200MB（基于 Python 3.11 Alpine）

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

---

## 📚 文档

完整文档请访问 GitHub 仓库：

- [快速开始指南](https://github.com/tmtbo/xiaoai-media/blob/main/QUICK_START.md)
- [用户使用指南](https://github.com/tmtbo/xiaoai-media/blob/main/docs/USER_GUIDE.md)
- [Docker 部署指南](https://github.com/tmtbo/xiaoai-media/blob/main/docs/deployment/DOCKER_GUIDE.md)
- [API 完整文档](https://github.com/tmtbo/xiaoai-media/blob/main/docs/api/README.md)
- [配置指南](https://github.com/tmtbo/xiaoai-media/blob/main/docs/config/README.md)

---

## 🔗 相关链接

- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
- [问题反馈](https://github.com/tmtbo/xiaoai-media/issues)
- [更新日志](https://github.com/tmtbo/xiaoai-media/blob/main/CHANGELOG.md)
- [MiService Fork](https://github.com/yihong0618/MiService)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详见：[贡献指南](https://github.com/tmtbo/xiaoai-media/blob/main/docs/CONTRIBUTING.md)

---

## 📄 许可证

MIT License

---

## ⭐ Star History

如果这个项目对你有帮助，欢迎给个 Star！

[![Star History Chart](https://api.star-history.com/svg?repos=tmtbo/xiaoai-media&type=Date)](https://star-history.com/#tmtbo/xiaoai-media&Date)
