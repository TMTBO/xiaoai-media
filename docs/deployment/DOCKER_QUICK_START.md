# Docker 快速开始

5 分钟使用 Docker 部署 XiaoAI Media。

---

## 🚀 一键部署

### 方式 1：Docker Compose（推荐）

```bash
# 1. 克隆仓库（或下载 docker-compose.yml）
git clone https://github.com/tmtbo/xiaoai-media.git
cd xiaoai-media

# 2. 创建配置文件
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
vim ./data/user_config.py  # 填入小米账号信息

# 3. 启动服务
docker-compose up -d
```

### 方式 2：Docker 命令

```bash
# 1. 创建数据目录
mkdir -p ./data

# 2. 创建配置文件
cat > ./data/user_config.py << 'EOF'
MI_USER = "your_xiaomi_account"
MI_PASS = "your_password"
MI_DID = "your_device_id"
EOF

# 3. 运行容器
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

---

## 📦 可用镜像

### GitHub Container Registry（推荐）

```bash
docker pull ghcr.io/tmtbo/xiaoai-media:latest
```

- 镜像地址：`ghcr.io/tmtbo/xiaoai-media:latest`
- 自动构建，与代码仓库同步
- 支持多架构（amd64, arm64）

### Docker Hub

```bash
docker pull thrillerone/xiaoai-media:latest
```

- 镜像地址：`thrillerone/xiaoai-media:latest`
- 备用镜像源
- 国内访问可能更快

---

## ✅ 验证部署

### 1. 检查容器状态

```bash
docker ps | grep xiaoai-media
```

### 2. 查看日志

```bash
# Docker Compose
docker-compose logs -f

# Docker 命令
docker logs -f xiaoai-media
```

### 3. 访问服务

打开浏览器访问：http://localhost:8000

---

## 🔧 常用命令

### 启动/停止

```bash
# Docker Compose
docker-compose up -d      # 启动
docker-compose down       # 停止
docker-compose restart    # 重启

# Docker 命令
docker start xiaoai-media   # 启动
docker stop xiaoai-media    # 停止
docker restart xiaoai-media # 重启
```

### 查看日志

```bash
# Docker Compose
docker-compose logs -f
docker-compose logs --tail 100

# Docker 命令
docker logs -f xiaoai-media
docker logs --tail 100 xiaoai-media
```

### 更新镜像

```bash
# Docker Compose
docker-compose pull
docker-compose up -d

# Docker 命令
docker pull ghcr.io/tmtbo/xiaoai-media:latest
docker stop xiaoai-media
docker rm xiaoai-media
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

---

## 📁 数据目录

容器内数据目录：`/data`
宿主机挂载目录：`./data`

```
./data/
├── user_config.py      # 配置文件
├── conversation.db     # 对话历史
├── playlists/          # 播放列表
└── logs/               # 日志文件
```

---

## ⚠️ 常见问题

### 1. 端口被占用

```bash
# 修改端口映射
docker run -d \
  --name xiaoai-media \
  -p 8080:8000 \  # 改为 8080
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest
```

### 2. 权限问题

```bash
# 修复数据目录权限
chmod -R 755 ./data
```

### 3. 配置文件未找到

```bash
# 检查配置文件是否存在
ls -la ./data/user_config.py

# 检查容器内配置
docker exec xiaoai-media ls -la /data/user_config.py
```

### 4. 容器无法启动

```bash
# 查看详细日志
docker logs xiaoai-media

# 进入容器调试
docker exec -it xiaoai-media sh
```

---

## 🔗 更多信息

- [完整 Docker 指南](DOCKER_GUIDE.md)
- [配置说明](../config/README.md)
- [故障排查](../config/CONFIG_FAQ.md)
- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
