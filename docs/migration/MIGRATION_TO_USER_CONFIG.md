# 迁移到 user_config.py

本项目已从 `.env` 配置方式迁移到 `user_config.py` 配置方式。

## 变更说明

### 之前（使用 .env）

```env
# .env
MI_USER=your_account@example.com
MI_PASS=your_password
MUSIC_API_BASE_URL=http://localhost:5050
```

### 现在（使用 user_config.py）

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://localhost:5050"

# 新增功能：唤醒词过滤
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

## 为什么迁移？

1. **更灵活** - Python 配置文件支持复杂逻辑
2. **更强大** - 支持自定义处理函数
3. **更清晰** - 类型明确，IDE 支持更好
4. **新功能** - 支持唤醒词过滤等新特性

## 迁移步骤

### 如果你已经有 .env 文件

1. **复制配置模板**
```bash
cp user_config_template.py user_config.py
```

2. **将 .env 中的配置复制到 user_config.py**

```env
# .env (旧配置)
MI_USER=your_account@example.com
MI_PASS=your_password
MI_DID=device_id
MUSIC_API_BASE_URL=http://192.168.1.100:5050
```

↓ 迁移到 ↓

```python
# user_config.py (新配置)
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MI_DID = "device_id"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"

# 配置唤醒词（新功能）
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

3. **验证配置**
```bash
make verify-config
```

4. **启动服务**
```bash
make dev
```

5. **删除 .env（可选）**
```bash
# 备份
cp .env .env.backup

# 删除
rm .env
```

### 如果你是新用户

直接创建 `user_config.py`：

```bash
cp user_config_template.py user_config.py
vim user_config.py  # 编辑配置
make verify-config  # 验证
make dev            # 启动
```

## 配置对照表

| .env 格式 | user_config.py 格式 | 说明 |
|-----------|---------------------|------|
| `MI_USER=value` | `MI_USER = "value"` | 字符串需要引号 |
| `MI_DID=` | `MI_DID = ""` | 空值用空字符串 |
| `ENABLE_CONVERSATION_POLLING=true` | `ENABLE_CONVERSATION_POLLING = True` | 布尔值首字母大写 |
| `CONVERSATION_POLL_INTERVAL=2.0` | `CONVERSATION_POLL_INTERVAL = 2.0` | 数字不需要引号 |

## 新增配置项

### 唤醒词配置

```python
# 唤醒词列表
WAKE_WORDS = ["小爱同学", "小爱"]

# 是否启用唤醒词过滤
ENABLE_WAKE_WORD_FILTER = True
```

### 自定义处理函数

```python
def should_handle_command(query: str) -> bool:
    """自定义指令过滤逻辑"""
    # 你的逻辑
    return True

def preprocess_command(query: str) -> str:
    """自定义指令预处理逻辑"""
    # 你的逻辑
    return query
```

### 日志配置

```python
# 日志级别
LOG_LEVEL = "INFO"

# 详细播放日志
VERBOSE_PLAYBACK_LOG = False
```

## 常见问题

### Q: 必须迁移吗？

A: 是的。新版本只支持 `user_config.py`，不再支持 `.env` 文件。

### Q: 迁移会影响现有功能吗？

A: 不会。所有现有配置项都保持不变，只是配置方式改变了。

### Q: 可以保留 .env 文件吗？

A: 可以保留作为备份，但系统不会读取它。

### Q: 如何验证迁移成功？

A: 运行 `make verify-config` 和 `make test-config`。

### Q: 迁移后启动失败怎么办？

A: 检查以下几点：
1. `user_config.py` 是否在项目根目录
2. 配置项是否有语法错误（引号、逗号等）
3. 运行 `python3 -m py_compile user_config.py` 检查语法

## 示例配置

### 最小配置

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
WAKE_WORDS = ["小爱同学"]
```

### 完整配置

参考 `user_config_template.py` 文件。

## 获取帮助

- [用户配置指南](docs/USER_CONFIG_GUIDE.md)
- [快速配置指南](docs/QUICK_CONFIG.md)
- [配置常见问题](docs/CONFIG_FAQ.md)

## 技术细节

### 配置加载流程

```
1. 启动服务
   ↓
2. 导入 config.py
   ↓
3. 查找 user_config.py
   ↓
4. 加载配置
   ↓
5. 如果不存在，抛出错误
```

### 为什么不再支持 .env？

1. **简化代码** - 移除了 dotenv 依赖和类型转换逻辑
2. **更好的类型支持** - Python 配置文件类型明确
3. **更强大的功能** - 支持函数、逻辑判断等
4. **统一配置方式** - 只有一种配置方式，更容易维护

---

**迁移完成后，请删除此文件。**
