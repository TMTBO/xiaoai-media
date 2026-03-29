# 快速开始

<div align="center">
  <img src="logo.svg" alt="XiaoAI Media Logo" width="120" />
</div>

5 分钟快速上手 XiaoAI Media。

---

## 🚀 Docker 部署（推荐）

### 1. 准备配置文件

```bash
# 创建数据目录
mkdir -p ./data

# 复制配置模板
cp user_config_template.py ./data/user_config.py
cp music_provider_template.py ./data/music_provider.py

# 编辑配置（填入小米账号信息）
vim ./data/user_config.py
```

配置示例：
```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
SERVER_BASE_URL = "http://192.168.1.100:8000"  # 改为你的局域网 IP
```

### 2. 启动服务

```bash
# 使用 Docker Compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 访问管理界面

浏览器打开：http://localhost:8000

---

## 💻 本地开发

### 1. 安装依赖

```bash
# 安装后端和前端依赖
make install
```

### 2. 配置服务

```bash
# 复制配置模板
cp user_config_template.py user_config.py
cp music_provider_template.py music_provider.py

# 编辑配置（填入小米账号信息）
vim user_config.py
```

### 3. 启动服务

```bash
# 同时启动后端和前端
make dev

# 或者分别启动
make backend  # 后端：http://localhost:8000
make frontend # 前端：http://localhost:5173
```

---

## 📊 数据存储

### 数据目录说明

| 环境 | HOME 设置 | 数据目录 |
|------|-----------|---------|
| 开发 | `HOME=.` | `./` |
| Docker | `HOME=/data` | `/data/` |

### 开发环境数据文件

```
./                          # 项目根目录
├── user_config.py          # 配置文件
├── music_provider.py       # 音乐提供者（必需）
├── conversation.db         # 对话历史
├── playlists/              # 播放列表（多文件存储）
│   ├── index.json          # 播单索引
│   └── {id}.json           # 各播单数据
└── logs/                   # 日志文件
```

这些文件已添加到 `.gitignore`，不会被提交。

### Docker 环境数据文件

```
./data/                     # 宿主机目录（挂载到容器 /data）
├── user_config.py          # 配置文件
├── music_provider.py       # 音乐提供者（必需）
├── conversation.db         # 对话历史
├── playlists/              # 播放列表
└── logs/                   # 日志文件
```

**重要提示**：
- `user_config.py` 和 `music_provider.py` 必须在同一目录
- 开发环境通过 Makefile 自动设置 `HOME=.`

### 播单存储优化（v1.0+）

从 v1.0 开始，播放列表采用多文件存储：
- `index.json` - 存储所有播单的索引信息
- `{playlist_id}.json` - 存储每个播单的详细数据

优势：
- 列表加载速度提升 80-90%
- 支持大量播单和播放项
- 减少内存占用

**从旧版本升级？** 运行迁移脚本：
```bash
python scripts/migrate_playlists.py
```

详见：[数据存储说明](docs/config/DATA_STORAGE.md) | [播单重构说明](docs/playlist/PLAYLIST_STORAGE_REFACTOR.md)

---

## 🎯 下一步

### 基础使用
1. [查看设备列表](http://localhost:8000) - 确认设备连接
2. [创建播放列表](docs/playlist/README.md) - 创建你的第一个播放列表
3. [设置定时任务](docs/scheduler/README.md) - 设置定时播放

### 进阶功能
1. [批量导入音频](docs/playlist/README_BATCH_IMPORT.md) - 批量导入本地音频
2. [启用对话监听](docs/conversation/README.md) - 自动拦截播放指令
3. [自定义音频源](docs/config/USER_CONFIG_GUIDE.md) - 集成自己的音乐服务

### 开发调试
1. [API 文档](docs/api/README.md) - 查看完整 API
2. [项目结构](docs/STRUCTURE.md) - 了解代码结构
3. [服务层架构](backend/src/xiaoai_media/services/README.md) - 了解架构设计

---

## 🛠️ 常用命令

### 开发命令

```bash
# 列出小爱音箱设备
make list-devices

# 验证配置
make verify-config

# 清理缓存
make clean

# 运行测试
make test
```

### Docker 命令

```bash
# 构建 Docker 镜像
make docker-build

# 运行 Docker 容器
make docker-run

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

---

## 📚 更多文档

- [完整 README](README.md) - 项目完整介绍
- [用户使用指南](docs/USER_GUIDE.md) - 完整使用指南
- [功能特性详解](docs/FEATURES.md) - 所有功能说明
- [配置指南](docs/config/README.md) - 配置详解
- [Docker 部署](docs/deployment/DOCKER_GUIDE.md) - Docker 完整指南
- [API 文档](docs/api/README.md) - API 参考
- [文档中心](docs/README.md) - 所有文档索引

---

**最后更新**：2026-03-28
