# Docker 部署指南

本指南说明如何使用 Docker 部署 XiaoAI Media 服务。

---

## 快速开始

### 1. 构建镜像

```bash
docker build -t xiaoai-media .
```

### 2. 准备配置文件

创建数据目录并复制配置文件模板：

```bash
# 创建数据目录
mkdir -p ~/.xiaoai-media

# 复制配置文件模板
cp user_config_template.py ~/.xiaoai-media/user_config.py

# 编辑配置文件
vim ~/.xiaoai-media/user_config.py
```

### 3. 运行容器

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

访问 http://localhost:8000 即可使用。

---

## 详细配置

### 数据目录结构

容器内的数据目录位于 `/data/.xiaoai-media`，建议挂载到主机的 `~/.xiaoai-media`。

```
~/.xiaoai-media/
├── user_config.py          # 用户配置文件（可选）
├── playlists.json          # 播单数据（自动生成）
└── logs/                   # 日志文件（可选）
```

### 配置方式

有三种方式配置服务：

#### 方式 1：挂载配置文件（推荐）

创建并编辑 `~/.xiaoai-media/user_config.py`，然后挂载数据目录：

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
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
  -e MI_USER="your_mi_user" \
  -e MI_PASS="your_mi_password" \
  -e MI_DID="your_device_id" \
  -e MUSIC_API_BASE_URL="http://your-music-api:5050" \
  -e SERVER_BASE_URL="http://your-host-ip:8000" \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

**优点**：
- 简单快速
- 适合容器编排工具（如 Docker Compose、Kubernetes）

**缺点**：
- 只支持基本配置，不能使用自定义函数
- 密码等敏感信息会出现在容器环境中

#### 方式 3：环境变量文件

创建 `.env` 文件：

```bash
# .env
MI_USER=your_mi_user
MI_PASS=your_mi_password
MI_DID=your_device_id
MUSIC_API_BASE_URL=http://your-music-api:5050
SERVER_BASE_URL=http://your-host-ip:8000
```

使用 `--env-file` 加载：

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  --env-file .env \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

### 配置优先级

当同时使用多种配置方式时，优先级如下（从高到低）：

1. **环境变量 `XIAOAI_CONFIG`** - 指定配置文件路径
2. **挂载的配置文件** - `/data/.xiaoai-media/user_config.py`
3. **环境变量** - `-e MI_USER=xxx` 等
4. **默认值** - 内置的默认配置

---

## Docker Compose 部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  xiaoai-media:
    build: .
    container_name: xiaoai-media
    ports:
      - "8000:8000"
    volumes:
      # 数据目录（配置、播单等）
      - ~/.xiaoai-media:/data/.xiaoai-media
    environment:
      # 基本配置（如果不使用配置文件）
      MI_USER: "${MI_USER}"
      MI_PASS: "${MI_PASS}"
      MI_DID: "${MI_DID}"
      MI_REGION: "cn"
      MUSIC_API_BASE_URL: "http://music-api:5050"
      SERVER_BASE_URL: "http://192.168.1.100:8000"
    restart: unless-stopped
    # 如果需要连接到其他服务（如音乐 API）
    # depends_on:
    #   - music-api

  # 可选：音乐下载服务
  # music-api:
  #   image: your-music-api-image
  #   ports:
  #     - "5050:5050"
```

启动服务：

```bash
docker-compose up -d
```

---

## 配置文件示例

`~/.xiaoai-media/user_config.py` 完整示例：

```python
# 小米账号配置
MI_USER = "your_mi_user"
MI_PASS = ""  # 有 token 可以留空
MI_PASS_TOKEN = "your_pass_token"
MI_DID = "your_device_id"
MI_REGION = "cn"

# 音乐服务配置
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
MUSIC_DEFAULT_PLATFORM = "tx"

# 本服务配置（注意：使用容器外部可访问的 IP）
SERVER_BASE_URL = "http://192.168.1.100:8000"

# 对话监听配置
ENABLE_CONVERSATION_POLLING = False
CONVERSATION_POLL_INTERVAL = 2

# 唤醒词配置
WAKE_WORDS = ["播放"]
ENABLE_WAKE_WORD_FILTER = True

# 播单存储目录（默认即可，会自动保存到挂载的数据目录）
PLAYLIST_STORAGE_DIR = "~/.xiaoai-media"

# 日志配置
LOG_LEVEL = "INFO"
VERBOSE_PLAYBACK_LOG = False
```

---

## 常见问题

### Q1: 配置文件修改后不生效？

**A:** 需要重启容器：

```bash
docker restart xiaoai-media
```

### Q2: 提示找不到配置文件？

**A:** 检查以下几点：
1. 确认数据目录已正确挂载：`docker inspect xiaoai-media | grep Mounts`
2. 确认配置文件存在：`ls -la ~/.xiaoai-media/user_config.py`
3. 查看容器日志：`docker logs xiaoai-media`

### Q3: 音箱无法播放音乐？

**A:** 检查 `SERVER_BASE_URL` 配置：
- ❌ 错误：`http://localhost:8000`（容器内部地址）
- ❌ 错误：`http://127.0.0.1:8000`（容器内部地址）
- ✅ 正确：`http://192.168.1.100:8000`（主机局域网 IP）

获取主机 IP：
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# 或者
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### Q4: 播单数据丢失？

**A:** 确保数据目录已正确挂载：
```bash
# 检查挂载
docker inspect xiaoai-media | grep -A 10 Mounts

# 如果没有挂载，重新创建容器（记得备份数据）
docker stop xiaoai-media
docker rm xiaoai-media
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

### Q5: 如何查看日志？

**A:** 使用 docker logs 命令：

```bash
# 查看最新日志
docker logs xiaoai-media

# 实时跟踪日志
docker logs -f xiaoai-media

# 查看最近 100 行
docker logs --tail 100 xiaoai-media
```

### Q6: 容器无法访问主机上的服务？

**A:** 使用主机网络模式（仅限 Linux）：

```bash
docker run -d \
  --name xiaoai-media \
  --network host \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

或者使用特殊域名（Docker Desktop on Mac/Windows）：
- `host.docker.internal` - 指向主机

```python
# 配置文件中
MUSIC_API_BASE_URL = "http://host.docker.internal:5050"
```

---

## 数据备份

### 备份数据目录

```bash
# 备份整个数据目录
tar -czf xiaoai-media-backup-$(date +%Y%m%d).tar.gz ~/.xiaoai-media/

# 仅备份配置和播单
cp ~/.xiaoai-media/user_config.py ~/backups/
cp ~/.xiaoai-media/playlists.json ~/backups/
```

### 恢复数据

```bash
# 停止容器
docker stop xiaoai-media

# 恢复数据
tar -xzf xiaoai-media-backup-20260320.tar.gz -C ~/

# 重启容器
docker start xiaoai-media
```

---

## 更新升级

### 更新到最新版本

```bash
# 1. 备份数据
tar -czf xiaoai-media-backup.tar.gz ~/.xiaoai-media/

# 2. 停止并删除旧容器
docker stop xiaoai-media
docker rm xiaoai-media

# 3. 拉取/构建新镜像
docker build -t xiaoai-media .

# 4. 启动新容器（使用相同的数据目录）
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media

# 5. 检查日志确认启动成功
docker logs xiaoai-media
```

---

## 性能优化

### 限制资源使用

```bash
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  --memory="512m" \
  --cpus="1.0" \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

### 使用多阶段构建（已内置）

项目的 Dockerfile 已经使用了多阶段构建，最终镜像体积较小。

---

## 安全建议

1. **不要在公网暴露服务** - 仅在局域网内使用
2. **使用 token 而非密码** - `MI_PASS_TOKEN` 比 `MI_PASS` 更安全
3. **保护配置文件** - 设置合适的文件权限：
   ```bash
   chmod 600 ~/.xiaoai-media/user_config.py
   ```
4. **定期备份数据** - 避免播单数据丢失

---

## 故障排查

### 检查容器状态

```bash
# 容器是否运行
docker ps | grep xiaoai-media

# 查看容器详细信息
docker inspect xiaoai-media

# 进入容器内部
docker exec -it xiaoai-media /bin/bash
```

### 检查日志

```bash
# 查看应用日志
docker logs xiaoai-media

# 查看配置加载情况
docker logs xiaoai-media 2>&1 | grep -i config

# 查看错误信息
docker logs xiaoai-media 2>&1 | grep -i error
```

### 测试配置

```bash
# 测试配置文件语法
docker exec xiaoai-media python -m py_compile /data/.xiaoai-media/user_config.py

# 测试服务是否响应
curl http://localhost:8000/api/health
```

---

## 相关文档

- [项目主文档](../README.md)
- [配置说明](../config/README.md)
- [播放列表管理](../playlist/PLAYLIST_GUIDE.md)
- [API 文档](../api/API_REFERENCE.md)

---

**更新时间**: 2026-03-20
