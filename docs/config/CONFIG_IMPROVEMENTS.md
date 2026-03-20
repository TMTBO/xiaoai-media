# Docker 配置和数据存储改进总结

## 改进内容

### 1. 配置文件多位置支持

升级了配置加载机制，支持从多个位置读取配置文件：

**优先级顺序**：
1. 项目根目录 `./user_config.py`（开发环境）
2. 数据目录 `~/.xiaoai-media/user_config.py`（生产环境/Docker）
3. 默认配置（如果都不存在）

**优点**：
- ✅ 开发环境使用项目根目录的配置文件
- ✅ 生产环境/Docker 使用数据目录的配置文件
- ✅ 没有配置文件时不再报错，使用默认配置
- ✅ 配置文件支持 Python 代码，功能更强大

### 2. Docker 支持完善

**Dockerfile 改进**：
- 添加数据目录 `/data/.xiaoai-media`
- 设置 `HOME=/data` 环境变量
- 添加 `VOLUME` 声明
- 修正用户权限

**新增文件**：
- `docker-compose.yml` - Docker Compose 配置
- `docs/deployment/DOCKER_GUIDE.md` - 完整 Docker 部署指南
- `docs/deployment/DOCKER_QUICK_START.md` - 快速参考

### 3. 数据目录标准化

**统一数据存储位置**：
- 本地环境：`~/.xiaoai-media`
- Docker 环境：`/data/.xiaoai-media`（映射到主机的 `~/.xiaoai-media`）

**目录结构**：
```
~/.xiaoai-media/
├── user_config.py          # 用户配置文件（可选）
├── playlists.json          # 播单数据（自动生成）
└── logs/                   # 日志文件（未来功能）
```

**新增文档**：
- `docs/config/DATA_STORAGE.md` - 数据存储详细说明

### 4. 文档完善

**更新的文档**：
- `README.md` - 添加 Docker 部署说明和数据存储介绍
- `user_config.py` - 更新注释说明

**新增的文档**：
- `docs/deployment/DOCKER_GUIDE.md` - 完整的 Docker 部署指南
- `docs/deployment/DOCKER_QUICK_START.md` - 快速参考文档
- `docs/config/DATA_STORAGE.md` - 数据存储说明

---

## 配置方式

### 使用配置文件

**位置**：`~/.xiaoai-media/user_config.py`

**优点**：
- ✅ 支持所有配置选项
- ✅ 支持自定义函数（如 `should_handle_command`、`preprocess_command`）
- ✅ 配置持久化
- ✅ 更安全（敏感信息不暴露在环境变量中）
- ✅ 使用 Python 语法，更灵活

**开发环境示例**：
```bash
# 在项目根目录创建配置文件
cp user_config_template.py user_config.py
vim user_config.py

# 启动服务
make dev
```

**Docker 环境示例**：
```bash
# 在数据目录创建配置文件
mkdir -p ~/.xiaoai-media
cp user_config_template.py ~/.xiaoai-media/user_config.py
vim ~/.xiaoai-media/user_config.py

# 启动 Docker 服务
docker-compose up -d
```

---

## 迁移指南

### 从旧版本迁移

如果你之前使用项目根目录的配置文件：

**无需任何操作** - 旧的配置文件仍然可以正常使用。

如果你想迁移到数据目录：

```bash
# 1. 创建数据目录
mkdir -p ~/.xiaoai-media

# 2. 复制配置文件
cp user_config.py ~/.xiaoai-media/

# 3. 删除旧配置文件（可选）
# mv user_config.py user_config.py.backup
```

---

## 使用示例

### 开发环境

```bash
# 使用项目根目录的配置文件
cp user_config_template.py user_config.py
vim user_config.py

# 启动开发服务器
make dev
```

### Docker 环境

```bash
# 使用数据目录的配置文件
mkdir -p ~/.xiaoai-media
cp user_config_template.py ~/.xiaoai-media/user_config.py
vim ~/.xiaoai-media/user_config.py

# 启动 Docker 服务
docker-compose up -d
```



---

## 常见问题

### Q1: 配置文件没有加载成功？

**A:** 检查日志中的配置加载信息：

```bash
# 开发环境
grep -i "config" backend.log

# Docker 环境
docker logs xiaoai-media | grep -i config
```

日志会显示：
```
INFO: 使用项目根目录的配置文件: /app/user_config.py
# 或
INFO: 使用数据目录的配置文件: /data/.xiaoai-media/user_config.py
# 或
WARNING: 未找到用户配置文件，将使用默认配置
```

### Q2: Docker 容器中找不到配置文件？

**A:** 检查数据目录是否正确挂载：

```bash
# 检查挂载
docker inspect xiaoai-media | grep -A 10 Mounts

# 应该看到：
# "Source": "/Users/username/.xiaoai-media",
# "Destination": "/data/.xiaoai-media",
```

### Q3: 修改配置后不生效？

**A:** 重启服务：

```bash
# 开发环境 - 如果使用 --reload 会自动重载
# 否则需要重启

# Docker 环境
docker-compose restart
```

### Q4: 播单数据保存在哪里？

**A:** 
- 本地环境：`~/.xiaoai-media/playlists.json`
- Docker 环境：主机的 `~/.xiaoai-media/playlists.json`（通过挂载）

### Q5: 如何备份数据？

**A:**
```bash
# 备份整个数据目录
tar -czf xiaoai-backup-$(date +%Y%m%d).tar.gz ~/.xiaoai-media/

# 仅备份配置和播单
cp ~/.xiaoai-media/user_config.py ~/backups/
cp ~/.xiaoai-media/playlists.json ~/backups/
```

---

## 修改的文件

### 核心代码
- `backend/src/xiaoai_media/config.py` - 简化配置加载，仅支持文件方式
- `Dockerfile` - 添加数据目录支持
- `user_config.py` - 更新注释

### 新增文件
- `docker-compose.yml` - Docker Compose 配置
- `docs/deployment/DOCKER_GUIDE.md` - Docker 完整指南
- `docs/deployment/DOCKER_QUICK_START.md` - 快速参考
- `docs/config/DATA_STORAGE.md` - 数据存储说明

### 更新文档
- `README.md` - 添加 Docker 和数据存储说明
- `docs/refactor/PLAYER_REFACTOR_SUMMARY.md` - 播放器重构总结

---

## 后续工作建议

1. **日志持久化** - 将日志保存到数据目录
2. **配置热重载** - 支持不重启服务更新配置
3. **Web 配置界面** - 通过 Web 界面管理配置
4. **配置验证** - 启动时验证配置的完整性和正确性
5. **Kubernetes 部署** - 提供 K8s 部署文档和配置

---

**更新时间**: 2026-03-20  
**版本**: 1.0.0  
**向后兼容**: ✅ 完全兼容旧版本
