# Docker 部署指南

本指南说明如何使用 Docker 部署 XiaoAI Media 服务。

---

## 🐳 Docker 镜像

### 可用镜像

- **GitHub Container Registry**: `ghcr.io/tmtbo/xiaoai-media:latest`
- **Docker Hub**: `thrillerone/xiaoai-media:latest`

### 镜像标签

- `latest` - 最新稳定版本
- `v1.x.x` - 特定版本号

---

## 快速开始

### 方式 1：使用预构建镜像（推荐）

#### 1. 准备配置文件

```bash
# 创建数据目录
mkdir -p ./data

# 复制配置文件模板
cp user_config_template.py ./data/user_config.py

# 编辑配置文件
vim ./data/user_config.py
```

#### 2. 拉取镜像

```bash
# 从 GitHub Container Registry（推荐）
docker pull ghcr.io/tmtbo/xiaoai-media:latest

# 或从 Docker Hub
docker pull thrillerone/xiaoai-media:latest
```

#### 3. 运行容器

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

### 方式 2：本地构建镜像

如果需要自定义或开发：

```bash
# 1. 构建镜像
docker build -t xiaoai-media .

# 2. 运行容器
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  xiaoai-media
```

---

## 详细配置

### 数据目录结构

容器内的数据目录位于 `/data`，建议挂载到主机的 `./data` 目录。

```
./data/
├── user_config.py          # 用户配置文件（可选）
├── playlists/              # 播放列表目录（自动生成）
├── conversation.db         # 对话历史数据库（自动生成）
└── logs/                   # 日志文件（可选）
```

### 配置方式

有三种方式配置服务：

#### 方式 1：挂载配置文件（推荐）

创建并编辑 `./data/user_config.py`，然后挂载数据目录：

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  xiaoai-media
```

**优点**：
- 配置持久化，容器重启后保留
- 支持所有配置选项（包括自定义函数）
- 播单数据自动保存到同一目录

#### 方式 2：环境变量（适合基本配置）

使用环境变量传递基本配置：

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e MI_USER=your_xiaomi_account \
  -e MI_PASS=your_password \
  -e MI_DID=your_device_id \
  xiaoai-media
```

**优点**：
- 快速启动，无需创建配置文件
- 适合简单场景

**限制**：
- 不支持自定义函数
- 不支持复杂配置（如唤醒词列表）

#### 方式 3：使用 Docker Compose（推荐生产环境）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  xiaoai-media:
    image: ghcr.io/tmtbo/xiaoai-media:latest
    container_name: xiaoai-media
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    restart: unless-stopped
    environment:
      - MI_USER=${MI_USER}
      - MI_PASS=${MI_PASS}
      - MI_DID=${MI_DID}
```

启动服务：

```bash
docker-compose up -d
```

---

## 环境变量说明

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| `MI_USER` | 小米账号 | 是 | - |
| `MI_PASS` | 小米密码 | 是 | - |
| `MI_DID` | 设备 ID | 是 | - |
| `MI_REGION` | 服务器区域 | 否 | `cn` |
| `MUSIC_API_BASE_URL` | 音乐 API 地址 | 否 | `http://localhost:5050` |
| `SERVER_BASE_URL` | 本服务地址 | 否 | `http://localhost:8000` |
| `LOG_LEVEL` | 日志级别 | 否 | `INFO` |

---

## 常见问题

### 1. 权限问题

如果遇到权限错误，确保数据目录有正确的权限：

```bash
chmod -R 755 ./data
```

### 2. 数据持久化

确保挂载了数据目录，否则容器重启后数据会丢失：

```bash
-v $(pwd)/data:/data
```

### 3. 查看日志

```bash
docker logs xiaoai-media
```

### 4. 进入容器调试

```bash
docker exec -it xiaoai-media sh
```

---

## 更新服务

### 使用预构建镜像

```bash
# 停止并删除旧容器
docker stop xiaoai-media
docker rm xiaoai-media

# 拉取最新镜像
docker pull ghcr.io/tmtbo/xiaoai-media:latest

# 启动新容器
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

### 使用 Docker Compose

```bash
# 拉取最新镜像并重启
docker-compose pull
docker-compose up -d
```

### 本地构建

```bash
# 停止并删除旧容器
docker stop xiaoai-media
docker rm xiaoai-media

# 重新构建镜像
docker build -t xiaoai-media .

# 启动新容器
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  xiaoai-media
```

---

## 诊断工具

使用诊断脚本检查 Docker 存储配置：

```bash
bash scripts/diagnose_docker_storage.sh
```

该脚本会检查：
- 容器状态
- 数据目录权限
- 写入权限
- 容器日志
