# Docker 部署 - 快速参考

## 一键部署

### 使用 Docker Compose（推荐）

```bash
# 1. 准备配置
mkdir -p ~/.xiaoai-media
cp user_config_template.py ~/.xiaoai-media/user_config.py
vim ~/.xiaoai-media/user_config.py

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 使用 Docker 命令

```bash
# 1. 构建镜像
docker build -t xiaoai-media .

# 2. 运行容器
docker run -d \
  --name xiaoai-media \
  -p 8000:8000 \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media

# 3. 查看日志
docker logs -f xiaoai-media

# 4. 停止容器
docker stop xiaoai-media
docker rm xiaoai-media
```

---

## 配置方式对比

| 方式 | 优点 | 缺点 | 推荐场景 |
|-----|------|------|----------|
| **配置文件** | • 支持所有功能<br>• 支持自定义函数<br>• 配置持久化 | • 需要挂载目录 | ✅ 生产环境 |
| **环境变量** | • 简单快速<br>• 适合编排工具 | • 不支持自定义函数<br>• 密码明文 | ⚠️ 测试环境 |
| **混合使用** | • 灵活性高 | • 配置分散 | ⚠️ 特殊需求 |

---

## 配置文件示例

最小配置（`~/.xiaoai-media/user_config.py`）：

```python
# 小米账号
MI_USER = "your_mi_user"
MI_PASS_TOKEN = "your_token"  # 推荐使用 token
MI_DID = "your_device_id"

# 服务地址（使用局域网 IP）
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
SERVER_BASE_URL = "http://192.168.1.100:8000"
```

完整配置参考：[user_config_template.py](../../user_config_template.py)

---

## 环境变量示例

创建 `.env` 文件：

```bash
MI_USER=your_mi_user
MI_PASS_TOKEN=your_token
MI_DID=your_device_id
MUSIC_API_BASE_URL=http://192.168.1.100:5050
SERVER_BASE_URL=http://192.168.1.100:8000
```

使用：
```bash
docker-compose --env-file .env up -d
```

---

## 常用命令

### 容器管理

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs --tail 100 xiaoai-media
```

### 配置更新

```bash
# 1. 修改配置文件
vim ~/.xiaoai-media/user_config.py

# 2. 重启容器
docker-compose restart
```

### 数据管理

```bash
# 备份数据
tar -czf backup.tar.gz ~/.xiaoai-media/

# 恢复数据
tar -xzf backup.tar.gz -C ~/
docker-compose restart

# 清空播单
rm ~/.xiaoai-media/playlists.json
docker-compose restart
```

### 调试

```bash
# 进入容器
docker exec -it xiaoai-media /bin/bash

# 查看配置加载情况
docker logs xiaoai-media 2>&1 | grep -i config

# 查看错误
docker logs xiaoai-media 2>&1 | grep -i error

# 检查目录挂载
docker inspect xiaoai-media | grep -A 10 Mounts
```

---

## 故障排查

### 问题 1：配置文件未加载

**症状**：使用默认配置，忽略自定义配置

**解决**：
```bash
# 检查文件是否存在
ls -la ~/.xiaoai-media/user_config.py

# 检查挂载
docker inspect xiaoai-media | grep Mounts

# 重新挂载
docker-compose down
docker-compose up -d
```

### 问题 2：音箱无法播放

**症状**：音箱提示"播放失败"

**解决**：
```bash
# 检查 SERVER_BASE_URL 配置
docker exec xiaoai-media env | grep SERVER_BASE_URL

# 应该是局域网 IP，不是 localhost
# 正确示例：http://192.168.1.100:8000
# 错误示例：http://localhost:8000
```

### 问题 3：播单数据丢失

**症状**：重启后播单不见了

**解决**：
```bash
# 确保数据目录已挂载
docker-compose down
vim docker-compose.yml  # 检查 volumes 配置

# 正确的 volumes 配置：
# volumes:
#   - ~/.xiaoai-media:/data/.xiaoai-media

docker-compose up -d
```

### 问题 4：连接不上音乐 API

**症状**：搜索音乐失败

**解决**：
```bash
# 如果音乐 API 在主机上运行
# Docker Desktop (Mac/Windows)：
MUSIC_API_BASE_URL=http://host.docker.internal:5050

# Linux：使用主机 IP
MUSIC_API_BASE_URL=http://192.168.1.100:5050

# 或使用 host 网络模式（仅 Linux）
docker run --network host ...
```

---

## 性能优化

### 资源限制

```yaml
# docker-compose.yml
services:
  xiaoai-media:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

### 健康检查

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 安全建议

1. **使用 token 而非密码**
   ```python
   MI_PASS_TOKEN = "your_token"  # ✅ 推荐
   MI_PASS = "your_password"     # ❌ 不推荐
   ```

2. **保护配置文件**
   ```bash
   chmod 600 ~/.xiaoai-media/user_config.py
   ```

3. **不要暴露到公网**
   - 仅绑定内网 IP
   - 使用防火墙限制访问

4. **定期备份**
   ```bash
   # Crontab 每天备份
   0 2 * * * tar -czf ~/backups/xiaoai-$(date +\%Y\%m\%d).tar.gz ~/.xiaoai-media/
   ```

---

## 更多信息

- 📖 [完整 Docker 指南](DOCKER_GUIDE.md)
- 💾 [数据存储说明](../config/DATA_STORAGE.md)
- ⚙️ [配置说明](../config/USER_CONFIG_GUIDE.md)
- 🎵 [播放器指南](../playlist/PLAYLIST_PLAYER_GUIDE.md)

---

**更新时间**: 2026-03-20
