# 快速开始

<div align="center">
  <img src="logo.svg" alt="XiaoAI Media Logo" width="120" />
</div>

## 开发环境

### 1. 安装依赖

```bash
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
# 启动后端和前端
make dev

# 或者分别启动
make backend  # 后端：http://localhost:8000
make frontend # 前端：http://localhost:5173
```

### 数据文件位置

开发环境的数据文件存储在项目根目录：

```
./
├── user_config.py      # 配置文件
├── music_provider.py   # 音乐提供者（必需）
├── conversation.db     # 对话历史
├── playlists/          # 播放列表（多文件存储）
│   ├── index.json      # 播单索引
│   └── {id}.json       # 各播单数据
└── ...
```

这些文件已添加到 `.gitignore`，不会被提交。

**重要提示**：`user_config.py` 和 `music_provider.py` 必须在同一目录。

**从旧版本升级？** 如果你有旧的 `playlists.json` 文件，运行迁移脚本：
```bash
python scripts/migrate_playlists.py
```

详见：[播单存储重构说明](docs/playlist/PLAYLIST_STORAGE_REFACTOR.md)

---

## Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 1. 创建数据目录和配置文件
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
cp music_provider_template.py ./data/music_provider.py
vim ./data/user_config.py

# 2. 启动服务（自动拉取镜像）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 命令

```bash
# 1. 创建数据目录和配置文件
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
cp music_provider_template.py ./data/music_provider.py
vim ./data/user_config.py

# 2. 拉取并运行镜像
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

### 可用镜像

- `ghcr.io/tmtbo/xiaoai-media:latest` (GitHub Container Registry)
- `thrillerone/xiaoai-media:latest` (Docker Hub)

### 数据文件位置

```bash
# 创建数据目录
mkdir -p ./data

# 复制配置文件
cp user_config_template.py ./data/user_config.py

# 编辑配置
vim ./data/user_config.py
```

### 2. 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 数据文件位置

Docker 环境的数据文件存储在挂载的 `/data` 目录：

```
./data/              # 宿主机目录
├── user_config.py   # 配置文件
├── music_provider.py # 音乐提供者（必需）
├── conversation.db  # 对话历史
├── playlists/       # 播放列表
└── ...
```

**重要提示**：`user_config.py` 和 `music_provider.py` 必须在同一目录（`./data/`）。

---

## 常用命令

```bash
# 列出小爱音箱设备
make list-devices

# 验证配置
make verify-config

# 清理缓存
make clean

# 构建 Docker 镜像
make docker-build

# 运行 Docker 容器
make docker-run
```

---

## 环境说明

| 环境 | HOME 设置 | 数据目录 |
|------|-----------|---------|
| 开发 | `HOME=.` | `./` |
| Docker | `HOME=/data` | `/data/` |

开发环境通过 Makefile 自动设置 `HOME=.`，使数据文件存储在项目根目录。

---

## 更多文档

- [完整 README](README.md)
- [配置指南](docs/config/README.md)
- [Docker 部署](docs/deployment/DOCKER_GUIDE.md)
- [开发环境配置](docs/config/DEV_ENVIRONMENT.md)
- [API 文档](docs/api/README.md)
