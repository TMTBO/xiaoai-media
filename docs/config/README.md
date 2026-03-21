# 配置指南

XiaoAI Media 的配置系统说明。

---

## 快速配置

### 开发环境

```bash
# 1. 复制配置模板
cp user_config_template.py user_config.py

# 2. 编辑配置
vim user_config.py

# 3. 启动服务
make dev
```

### Docker 环境

```bash
# 1. 创建数据目录
mkdir -p ./data

# 2. 复制配置模板
cp user_config_template.py ./data/user_config.py

# 3. 编辑配置
vim ./data/user_config.py

# 4. 启动服务
docker-compose up -d
```

---

## 配置文件位置

### 数据目录

| 环境 | HOME 设置 | 数据目录 | 配置文件路径 |
|------|-----------|---------|-------------|
| 开发 | `HOME=.` | `./` | `./user_config.py` |
| Docker | `HOME=/data` | `/data/` | `/data/user_config.py` |

### 查找顺序

系统会在 `$HOME/user_config.py` 查找配置文件：
- 开发环境：`./user_config.py`（项目根目录）
- Docker 环境：`/data/user_config.py`（挂载卷）

---

## 配置项说明

### 必填配置

```python
# 小米账号配置
MI_USER = "your_xiaomi_account"
MI_PASS = "your_password"
MI_DID = "your_device_id"
```

### 可选配置

```python
# 服务器区域（默认：cn）
MI_REGION = "cn"

# 音乐 API 地址（默认：http://localhost:5050）
MUSIC_API_BASE_URL = "http://localhost:5050"

# 本服务地址（必须使用音箱可访问的局域网 IP）
SERVER_BASE_URL = "http://192.168.1.100:8000"

# 对话监听配置
ENABLE_CONVERSATION_POLLING = True
CONVERSATION_POLL_INTERVAL = 2.0

# 唤醒词配置
WAKE_WORDS = ["小爱", "播放"]
ENABLE_WAKE_WORD_FILTER = True

# 日志配置
LOG_LEVEL = "INFO"
VERBOSE_PLAYBACK_LOG = False
```

---

## 高级配置

### 自定义指令处理

```python
def should_handle_command(query: str) -> bool:
    """判断是否应该处理该指令"""
    # 自定义逻辑
    if "播放" in query or "来一首" in query:
        return True
    return False

def preprocess_command(query: str) -> str:
    """预处理指令文本"""
    # 移除唤醒词
    query = query.replace("小爱", "").replace("同学", "")
    return query.strip()
```

---

## 环境变量配置

除了配置文件，也可以使用环境变量（优先级低于配置文件）：

```bash
# Docker 运行时
docker run -d \
  -e MI_USER=your_account \
  -e MI_PASS=your_password \
  -e MI_DID=your_device_id \
  -v ./data:/data \
  xiaoai-media
```

---

## 数据存储

### 目录结构

```
$HOME/
├── user_config.py      # 配置文件
├── conversation.db     # 对话历史数据库
├── playlists/          # 播放列表目录
│   ├── default.json
│   └── favorites.json
└── logs/               # 日志文件（未来）
```

### 数据持久化

- **开发环境**：数据存储在项目根目录，已添加到 `.gitignore`
- **Docker 环境**：数据存储在挂载的 `/data` 目录

详见：[数据存储说明](DATA_STORAGE.md)

---

## 相关文档

- [开发环境配置](DEV_ENVIRONMENT.md) - 本地开发环境设置
- [数据存储说明](DATA_STORAGE.md) - 数据目录详解
- [用户配置指南](USER_CONFIG_GUIDE.md) - 配置文件详细说明
- [配置 FAQ](CONFIG_FAQ.md) - 常见问题解答

---

## 故障排查

### 配置文件未找到

```bash
# 检查配置文件是否存在
ls -la user_config.py  # 开发环境
ls -la ./data/user_config.py  # Docker 环境

# 查看日志
docker logs xiaoai-media  # Docker 环境
```

### 权限问题

```bash
# 修复权限
chmod 644 user_config.py  # 开发环境
chmod -R 755 ./data  # Docker 环境
```

### 验证配置

```bash
# 使用验证脚本
make verify-config

# 或手动验证
HOME=. python -c "from xiaoai_media.config import *; print(MI_USER, MI_DID)"
```
