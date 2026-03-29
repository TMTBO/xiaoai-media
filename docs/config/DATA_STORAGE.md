# 数据存储说明

XiaoAI Media 使用 HOME 目录作为数据存储根目录。

---

## 数据目录位置

### 开发环境

通过设置 `HOME=.` 环境变量，数据存储在项目根目录：

```
./                              # 项目根目录（HOME=.）
├── user_config.py              # 用户配置文件（可选）
├── conversation.db             # 对话历史数据库（自动生成）
├── playlists/                  # 播放列表目录（自动生成）
│   ├── default.json
│   └── favorites.json
└── logs/                       # 日志文件（未来功能）
```

### Docker 环境

通过设置 `HOME=/data` 环境变量，数据存储在容器内的 `/data` 目录：

```
/data/                          # 容器内数据目录（HOME=/data）
├── user_config.py              # 用户配置文件（可选）
├── conversation.db             # 对话历史数据库（自动生成）
├── playlists/                  # 播放列表目录（自动生成）
└── logs/                       # 日志文件（未来功能）
```

---

## 配置文件查找

系统会在 `$HOME/user_config.py` 查找配置文件：

1. **开发环境** - `./user_config.py`（项目根目录）
2. **Docker 环境** - `/data/user_config.py`（容器内）
3. **默认值** - 如果不存在，使用内置默认配置

---

## 配置文件创建

### 开发环境

```bash
# 复制配置模板
cp user_config_template.py user_config.py

# 编辑配置
vim user_config.py
```

### Docker 环境

```bash
# 创建数据目录
mkdir -p ./data

# 复制配置模板
cp user_config_template.py ./data/user_config.py

# 编辑配置
vim ./data/user_config.py
```

### 配置示例

```python
# user_config.py

# 小米账号
MI_USER = "your_xiaomi_account"
MI_PASS = "your_password"
MI_DID = "your_device_id"

# 音乐 API
MUSIC_API_BASE_URL = "http://localhost:5050"

# 本服务地址（必须使用音箱可访问的局域网 IP）
SERVER_BASE_URL = "http://192.168.1.100:8000"
```

---

## 播放列表数据

播放列表数据自动保存到 `$HOME/playlists/` 目录。

### 数据格式

```json
{
  "name": "我的歌单",
  "songs": [
    {
      "title": "歌曲名",
      "artist": "歌手",
      "url": "http://..."
    }
  ]
}
```

---

## 数据备份

### 开发环境

```bash
# 备份配置文件
cp user_config.py ~/backups/user_config-$(date +%Y%m%d).py

# 备份播放列表
cp -r playlists ~/backups/playlists-$(date +%Y%m%d)

# 备份对话历史
cp conversation.db ~/backups/conversation-$(date +%Y%m%d).db
```

### Docker 环境

```bash
# 备份整个数据目录
tar -czf xiaoai-media-backup-$(date +%Y%m%d).tar.gz ./data/

# 或使用 docker cp
docker cp xiaoai-media:/data ./backup-$(date +%Y%m%d)
```

---

## 数据恢复

### 开发环境

```bash
# 恢复配置文件
cp ~/backups/user_config-20260320.py user_config.py

# 恢复播放列表
cp -r ~/backups/playlists-20260320 playlists

# 重启服务
make dev
```

### Docker 环境

```bash
# 恢复数据目录
tar -xzf xiaoai-media-backup-20260320.tar.gz

# 重启容器
docker-compose restart
```

---

## Docker 挂载

### 挂载数据目录

```bash
# Docker 命令
docker run -d \
  -v $(pwd)/data:/data \
  ghcr.io/tmtbo/xiaoai-media:latest

# Docker Compose
# docker-compose.yml
volumes:
  - ./data:/data
```

这会将主机的 `./data` 目录映射到容器内的 `/data` 目录。

### 在容器中的位置

- 配置文件：`/data/user_config.py`
- 播放列表：`/data/playlists/`
- 对话历史：`/data/conversation.db`

---

## 环境变量

| 环境 | HOME 设置 | 数据目录 | 配置文件路径 |
|------|-----------|---------|-------------|
| 开发 | `HOME=.` | `./` | `./user_config.py` |
| Docker | `HOME=/data` | `/data/` | `/data/user_config.py` |

---

## 数据迁移

如果你从旧版本升级，需要迁移数据：

详见：[HOME 目录迁移说明](../migration/HOME_DIR_MIGRATION.md)

---

## 相关文档

- [配置指南](README.md)
- [开发环境配置](DEV_ENVIRONMENT.md)
- [Docker 部署](../deployment/DOCKER_GUIDE.md)
- [迁移指南](../migration/README.md)
