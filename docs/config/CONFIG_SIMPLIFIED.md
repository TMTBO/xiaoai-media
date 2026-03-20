# 配置系统简化说明

## 改进内容

本次改进移除了环境变量配置支持，简化了配置系统，**仅保留 user_config.py 文件配置方式**。

### 移除的功能

- ❌ 环境变量配置支持（MI_USER、MI_PASS、SERVER_BASE_URL 等）
- ❌ XIAOAI_CONFIG 环境变量指定配置文件路径
- ❌ .env.example 环境变量模板文件

### 保留的功能

- ✅ user_config.py 文件配置（**唯一配置方式**）
- ✅ 多位置配置文件查找（项目根目录 / 数据目录）
- ✅ 自定义函数支持（should_handle_command、preprocess_command）
- ✅ 配置文件不存在时使用默认配置
- ✅ Docker 数据目录挂载支持

---

## 配置文件查找顺序

配置系统会按以下优先级查找配置文件：

1. **项目根目录** - `./user_config.py`（开发环境）
2. **数据目录** - `~/.xiaoai-media/user_config.py`（生产环境/Docker）
3. **默认配置** - 如果都不存在，使用内置默认配置

---

## 使用方式

### 开发环境

```bash
# 1. 从模板创建配置文件
cp user_config_template.py user_config.py

# 2. 编辑配置
vim user_config.py

# 3. 启动服务
make dev
```

### 生产环境/Docker

```bash
# 1. 创建数据目录
mkdir -p ~/.xiaoai-media

# 2. 从模板创建配置文件
cp user_config_template.py ~/.xiaoai-media/user_config.py

# 3. 编辑配置
vim ~/.xiaoai-media/user_config.py

# 4. 启动 Docker 服务
docker-compose up -d
```

### Docker 数据目录挂载

在 docker-compose.yml 中已配置数据目录挂载：

```yaml
volumes:
  - ~/.xiaoai-media:/data/.xiaoai-media
```

这样配置文件会自动从挂载的数据目录加载。

---

## 配置示例

```python
# ~/.xiaoai-media/user_config.py

# 小米账号配置
MI_USER = "your_xiaomi_account@example.com"
MI_PASS_TOKEN = "your_token"  # 推荐使用 token
MI_DID = "your_device_id"     # 可选，不填使用第一个设备
MI_REGION = "cn"              # 可选，默认 cn

# 音乐服务配置
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"  # 局域网 IP
MUSIC_DEFAULT_PLATFORM = "tx"  # tx|kw|kg|wy|mg

# 本服务配置
SERVER_BASE_URL = "http://192.168.1.100:8000"  # 局域网 IP，音箱可访问

# 对话监听配置
ENABLE_CONVERSATION_POLLING = True
CONVERSATION_POLL_INTERVAL = 2.0

# 唤醒词配置（可选）
WAKE_WORDS = ["小雅", "播放"]
ENABLE_WAKE_WORD_FILTER = True

# 自定义函数（可选）
def should_handle_command(query: str) -> bool:
    """判断是否处理该指令"""
    return any(word in query for word in WAKE_WORDS)

def preprocess_command(query: str) -> str:
    """预处理指令文本"""
    for word in WAKE_WORDS:
        query = query.replace(word, "")
    return query.strip()
```

---

## 优势

### 1. 更简单

- **单一配置方式**：不需要在环境变量和配置文件之间选择
- **更少的文件**：移除了 .env.example 等文件
- **更清晰的文档**：配置说明更简洁明了

### 2. 更强大

- **Python 语法**：配置文件使用 Python 语法，支持更复杂的逻辑
- **自定义函数**：可以在配置文件中定义自定义处理函数
- **类型安全**：Python 语法提供更好的类型提示和检查

### 3. 更安全

- **文件权限**：配置文件可以设置权限保护敏感信息
- **不暴露在环境**：敏感信息不会暴露在容器环境变量中
- **备份友好**：配置文件更容易备份和版本控制

---

## 迁移指南

### 从环境变量迁移

如果你之前使用环境变量或 .env 文件：

```bash
# 1. 创建配置文件
mkdir -p ~/.xiaoai-media
cat > ~/.xiaoai-media/user_config.py << 'EOF'
# 将你的环境变量转换为 Python 变量
MI_USER = "your_user"
MI_PASS_TOKEN = "your_token"
MI_DID = "your_device_id"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
SERVER_BASE_URL = "http://192.168.1.100:8000"
EOF

# 2. 重启服务
docker-compose restart
# 或
make dev
```

### 从旧版 user_config.py 迁移

如果你之前使用项目根目录的配置文件：

**无需任何操作** - 旧的配置文件仍然可以正常使用。

如果你想迁移到数据目录：

```bash
# 复制到数据目录
mkdir -p ~/.xiaoai-media
cp user_config.py ~/.xiaoai-media/

# 可选：删除项目根目录的配置文件
# rm user_config.py
```

---

## 常见问题

### Q1: 配置文件没有加载？

**A:** 检查日志中的配置加载信息：

```bash
# 开发环境
grep -i "config" backend.log

# Docker 环境
docker logs xiaoai-media | grep -i config
```

日志会显示：
```
INFO: 使用项目根目录的配置文件: /path/to/user_config.py
# 或
INFO: 使用数据目录的配置文件: /data/.xiaoai-media/user_config.py
# 或
WARNING: 未找到用户配置文件，将使用默认配置
```

### Q2: Docker 容器找不到配置文件？

**A:** 检查数据目录是否正确挂载：

```bash
# 检查挂载
docker inspect xiaoai-media | grep -A 10 Mounts

# 应该看到：
# "Source": "/Users/username/.xiaoai-media",
# "Destination": "/data/.xiaoai-media",
```

### Q3: 需要使用环境变量怎么办？

**A:** 本项目不再支持环境变量配置。请使用 user_config.py 文件。

如果你确实需要从环境变量读取，可以在配置文件中这样做：

```python
# ~/.xiaoai-media/user_config.py
import os

MI_USER = os.getenv("MI_USER", "default_user")
MI_PASS_TOKEN = os.getenv("MI_PASS_TOKEN", "")
```

### Q4: 配置文件语法错误怎么办?

**A:** 配置文件是 Python 代码，语法错误会导致加载失败。

检查日志：
```bash
docker logs xiaoai-media | grep -i error
```

修复语法错误后重启服务：
```bash
docker-compose restart
```

---

## 修改的文件

### 核心代码
- `backend/src/xiaoai_media/config.py` - 移除环境变量支持，简化配置加载
- `docker-compose.yml` - 移除环境变量配置项

### 删除的文件
- `.env.example` - 不再需要环境变量模板

### 更新的文档
- `README.md` - 移除环境变量配置相关引用
- `docs/config/DATA_STORAGE.md` - 更新配置文件查找说明
- `docs/config/CONFIG_IMPROVEMENTS.md` - 更新改进说明

---

## 后续工作建议

1. **配置验证** - 启动时验证配置的完整性和正确性
2. **配置模板生成** - 提供命令行工具生成配置文件模板
3. **Web 配置界面** - 通过 Web 界面管理配置（未来）
4. **配置加密** - 支持敏感信息加密存储（未来）

---

**更新时间**: 2026-03-20  
**版本**: 2.0.0  
**向后兼容**: ✅ 兼容旧的 user_config.py 文件  
**重大变更**: ❌ 不再支持环境变量配置
