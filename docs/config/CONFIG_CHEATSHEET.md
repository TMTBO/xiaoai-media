# 配置速查表

快速参考配置系统的常用操作。

## 快速开始

```bash
# 1. 复制配置模板
cp user_config_template.py user_config.py

# 2. 编辑配置
vim user_config.py

# 3. 测试配置
make test-config

# 4. 启动服务
make dev
```

## 最小配置

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
```

## 唤醒词配置

### 启用唤醒词过滤

```python
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

### 禁用唤醒词过滤

```python
ENABLE_WAKE_WORD_FILTER = False
```

## 自定义函数

### 自定义指令过滤

```python
def should_handle_command(query: str) -> bool:
    """只处理音乐相关指令"""
    if not any(word in query for word in WAKE_WORDS):
        return False
    return "播放" in query
```

### 自定义指令预处理

```python
def preprocess_command(query: str) -> str:
    """移除唤醒词和标点"""
    for wake_word in WAKE_WORDS:
        query = query.replace(wake_word, "")
    query = query.replace("，", "").replace(",", "")
    return query.strip()
```

## 常用配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `MI_USER` | 小米账号 | `"user@example.com"` |
| `MI_PASS` | 小米密码 | `"password"` |
| `MI_DID` | 设备ID | `""` (留空自动选择) |
| `MUSIC_API_BASE_URL` | 音乐服务地址 | `"http://192.168.1.100:5050"` |
| `MUSIC_DEFAULT_PLATFORM` | 默认音乐平台 | `"tx"` (腾讯) |
| `WAKE_WORDS` | 唤醒词列表 | `["小爱同学", "小爱"]` |
| `ENABLE_WAKE_WORD_FILTER` | 启用唤醒词过滤 | `True` / `False` |

## 音乐平台代码

| 代码 | 平台 |
|------|------|
| `tx` | 腾讯音乐 |
| `wy` | 网易云音乐 |
| `kg` | 酷狗音乐 |
| `kw` | 酷我音乐 |
| `mg` | 咪咕音乐 |

## 测试命令

```bash
# 测试配置加载
make test-config

# 查看设备列表
make list-devices

# 启动后端
make backend

# 启动前端
make frontend

# 同时启动
make dev
```

## 故障排查

### 配置未生效

```bash
# 1. 检查文件名
ls -la user_config.py

# 2. 检查语法
python3 -m py_compile user_config.py

# 3. 测试配置
make test-config

# 4. 查看日志
make backend  # 观察启动日志
```

### 唤醒词不工作

```bash
# 1. 测试配置
make test-config

# 2. 检查配置
python3 -c "
import sys
sys.path.insert(0, 'backend/src')
from xiaoai_media import config
print('WAKE_WORDS:', config.WAKE_WORDS)
print('ENABLE_WAKE_WORD_FILTER:', config.ENABLE_WAKE_WORD_FILTER)
"
```

## 配置优先级

```
user_config.py > .env > 默认值
```

## 文件位置

```
项目根目录/
├── user_config.py           # 用户配置（需创建）
├── user_config_template.py  # 完整模板
├── user_config.example.py   # 简化示例
└── .env                     # 环境变量（向后兼容）
```

## 完整文档

- [快速配置指南](QUICK_CONFIG.md) - 5分钟快速开始
- [完整配置指南](USER_CONFIG_GUIDE.md) - 详细说明
- [配置系统总结](USER_CONFIG_SUMMARY.md) - 技术细节

## 示例配置

### 示例 1: 基础配置

```python
MI_USER = "user@example.com"
MI_PASS = "password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
WAKE_WORDS = ["小爱同学"]
```

### 示例 2: 多唤醒词

```python
WAKE_WORDS = ["小爱同学", "小爱", "小米"]
ENABLE_WAKE_WORD_FILTER = True
```

### 示例 3: 不过滤

```python
ENABLE_WAKE_WORD_FILTER = False
```

### 示例 4: 自定义逻辑

```python
def should_handle_command(query: str) -> bool:
    return "播放" in query and any(w in query for w in WAKE_WORDS)

def preprocess_command(query: str) -> str:
    for w in WAKE_WORDS:
        query = query.replace(w, "")
    return query.strip()
```

## 快速链接

- 📖 [文档导航](NAVIGATION.md)
- ⚙️ [配置模板](../user_config_template.py)
- 🧪 [测试脚本](../test/test_user_config.py)
- 📝 [更新日志](../CHANGELOG.md)
