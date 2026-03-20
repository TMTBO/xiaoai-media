# 数据存储说明

XiaoAI Media 使用 `~/.xiaoai-media` 作为默认数据存储目录。

---

## 目录结构

**开发环境**：
```
./.xiaoai-media/                # 项目根目录（已加入 .gitignore）
├── user_config.py              # 用户配置文件（可选）
├── playlists.json              # 播单数据（自动生成）
└── logs/                       # 日志文件（可选，未来功能）
```

**生产环境**：
```
~/.xiaoai-media/                # 用户主目录
├── user_config.py              # 用户配置文件（可选）
├── playlists.json              # 播单数据（自动生成）
└── logs/                       # 日志文件（可选，未来功能）
```

---

## 配置文件

### 位置

配置文件按以下优先级查找：

1. **项目根目录** - `./user_config.py`（开发环境）

2. **数据目录** - `~/.xiaoai-media/user_config.py`（生产环境）

3. **默认值** - 如果都不存在，使用内置默认配置

### 创建配置文件

```bash
# 创建数据目录
mkdir -p ~/.xiaoai-media

# 从项目模板复制
cp user_config_template.py ~/.xiaoai-media/user_config.py

# 编辑配置
vim ~/.xiaoai-media/user_config.py
```

### 配置示例

```python
# ~/.xiaoai-media/user_config.py

# 小米账号
MI_USER = "your_mi_user"
MI_PASS_TOKEN = "your_token"
MI_DID = "your_device_id"

# 音乐服务
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
SERVER_BASE_URL = "http://192.168.1.100:8000"

# 其他配置...
```

---

## 播单数据

播单数据自动保存到 `~/.xiaoai-media/playlists.json`。

### 数据格式

```json
{
  "playlist_id_1": {
    "id": "playlist_id_1",
    "name": "我的音乐",
    "type": "music",
    "items": [...],
    "created_at": "2026-03-20T10:00:00",
    "updated_at": "2026-03-20T12:00:00"
  },
  ...
}
```

### 备份播单

```bash
# 备份播单数据
cp ~/.xiaoai-media/playlists.json ~/backups/playlists-$(date +%Y%m%d).json

# 或备份整个数据目录
tar -czf xiaoai-media-backup.tar.gz ~/.xiaoai-media/
```

### 恢复播单

```bash
# 恢复播单数据
cp ~/backups/playlists-20260320.json ~/.xiaoai-media/playlists.json

# 重启服务（如果正在运行）
# systemctl restart xiaoai-media
# 或 docker restart xiaoai-media
```

---

## Docker 环境

在 Docker 环境中，数据目录位于容器内的 `/data/.xiaoai-media`。

### 挂载数据目录

```bash
docker run -d \
  -v ~/.xiaoai-media:/data/.xiaoai-media \
  xiaoai-media
```

这会将主机的 `~/.xiaoai-media` 映射到容器内的 `/data/.xiaoai-media`。

### 在容器中的位置

- 配置文件：`/data/.xiaoai-media/user_config.py`
- 播单数据：`/data/.xiaoai-media/playlists.json`
- HOME 环境变量：`/data`

详见 [Docker 部署指南](../deployment/DOCKER_GUIDE.md)。

---

## 权限设置

### 推荐权限

```bash
# 数据目录
chmod 755 ~/.xiaoai-media

# 配置文件（包含敏感信息）
chmod 600 ~/.xiaoai-media/user_config.py

# 播单数据
chmod 644 ~/.xiaoai-media/playlists.json
```

### 所有者

本地运行时，数据目录所有者应为当前用户：

```bash
chown -R $USER:$USER ~/.xiaoai-media
```

Docker 运行时，容器内会使用 `appuser` 用户（UID 可能不同）。

---

## 迁移数据

### 从旧版本迁移

如果你之前使用的是其他数据目录：

```bash
# 1. 停止服务
# systemctl stop xiaoai-media

# 2. 创建新数据目录
mkdir -p ~/.xiaoai-media

# 3. 复制配置文件
cp /path/to/old/user_config.py ~/.xiaoai-media/

# 4. 复制播单数据（如果有）
cp /path/to/old/playlists.json ~/.xiaoai-media/

# 5. 启动服务
# systemctl start xiaoai-media
```

### 更改数据目录

如果需要使用自定义数据目录：

**方式 1：修改配置文件**

```python
# user_config.py
PLAYLIST_STORAGE_DIR = "/custom/path/to/data"
```

**方式 2：使用环境变量**

```bash
# 指定配置文件位置
export XIAOAI_CONFIG=/custom/path/to/user_config.py

# 或在 systemd service 中
Environment="XIAOAI_CONFIG=/custom/path/to/user_config.py"
```

---

## 清理数据

### 仅删除播单

```bash
rm ~/.xiaoai-media/playlists.json
```

### 删除所有数据

```bash
# 谨慎操作！会删除所有配置和播单
rm -rf ~/.xiaoai-media
```

### 重置到默认状态

```bash
# 备份当前数据
mv ~/.xiaoai-media ~/.xiaoai-media.backup

# 重新创建
mkdir -p ~/.xiaoai-media
cp user_config_template.py ~/.xiaoai-media/user_config.py
```

---

## 故障排查

### 配置文件未加载

**症状**：服务使用默认配置，忽略你的配置文件

**检查**：
```bash
# 1. 确认文件存在
ls -la ~/.xiaoai-media/user_config.py

# 2. 检查文件权限
stat ~/.xiaoai-media/user_config.py

# 3. 验证语法
python -m py_compile ~/.xiaoai-media/user_config.py

# 4. 查看日志
# 日志中会显示配置文件的加载路径
```

### 播单数据丢失

**可能原因**：
1. 数据目录未正确挂载（Docker）
2. 权限问题导致无法写入
3. 服务异常退出未保存

**解决**：
```bash
# 1. 检查目录权限
ls -la ~/.xiaoai-media/

# 2. 确保可写
chmod 755 ~/.xiaoai-media

# 3. 从备份恢复
cp ~/backups/playlists-latest.json ~/.xiaoai-media/playlists.json
```

### Docker 容器中找不到配置

**检查挂载**：
```bash
docker inspect xiaoai-media | grep -A 10 Mounts
```

**正确的挂载示例**：
```json
"Mounts": [
  {
    "Type": "bind",
    "Source": "/Users/username/.xiaoai-media",
    "Destination": "/data/.xiaoai-media",
    "Mode": "",
    "RW": true,
    "Propagation": "rprivate"
  }
]
```

---

## 最佳实践

### 1. 定期备份

创建自动备份脚本：

```bash
#!/bin/bash
# ~/bin/backup-xiaoai-media.sh

BACKUP_DIR=~/backups/xiaoai-media
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/xiaoai-media-$DATE.tar.gz ~/.xiaoai-media/

# 保留最近 7 天的备份
find $BACKUP_DIR -name "xiaoai-media-*.tar.gz" -mtime +7 -delete
```

添加到 crontab（每天凌晨 2 点备份）：
```cron
0 2 * * * ~/bin/backup-xiaoai-media.sh
```

### 2. 版本控制配置文件

将配置文件加入版本控制（注意排除敏感信息）：

```bash
cd ~/.xiaoai-media
git init
echo "user_config.py" >> .gitignore  # 不提交实际配置
cp user_config.py user_config.example.py  # 创建示例配置
git add user_config.example.py
git commit -m "Add example config"
```

### 3. 使用软链接

如果你希望配置文件在其他位置：

```bash
# 将配置文件软链接到数据目录
ln -s /path/to/your/config.py ~/.xiaoai-media/user_config.py
```

---

## 相关文档

- [Docker 部署指南](../deployment/DOCKER_GUIDE.md)
- [配置说明](../config/CONFIG_GUIDE.md)
- [播放列表管理](../playlist/PLAYLIST_GUIDE.md)

---

**更新时间**: 2026-03-20
