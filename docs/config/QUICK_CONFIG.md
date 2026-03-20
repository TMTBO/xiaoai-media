# 快速配置指南

5 分钟快速配置 XiaoAi Media

## 1. 选择配置方式

### 方式 A: Python 配置文件（推荐）

适合需要自定义唤醒词和处理逻辑的用户。

**重要：使用此方式后，不再需要 .env 文件！**

```bash
# 复制模板
cp user_config_template.py user_config.py

# 编辑配置
vim user_config.py  # 或使用你喜欢的编辑器
```

最小配置：
```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"  # 改为你的局域网IP

# 唤醒词配置
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

### 方式 B: 环境变量文件（简单）

适合快速开始，不需要唤醒词过滤。

```bash
# 复制模板
cp .env.example .env

# 编辑配置
vim .env
```

最小配置：
```env
MI_USER=your_account@example.com
MI_PASS=your_password
MUSIC_API_BASE_URL=http://192.168.1.100:5050
```

### 配置优先级

```
user_config.py > .env > 默认值
```

- 如果存在 `user_config.py`，优先使用
- 如果 `user_config.py` 中某项未设置，从 `.env` 读取
- 如果都没有，使用默认值

## 2. 测试配置

```bash
# 测试配置加载
make test-config

# 查看设备列表
make list-devices
```

## 3. 启动服务

配置文件会在启动时**自动加载**，无需额外配置。

```bash
# 启动后端和前端
make dev

# 或分别启动
make backend   # 后端: http://localhost:8000
make frontend  # 前端: http://localhost:5173
```

### 验证配置加载

启动后查看日志，应该看到：

```
INFO:xiaoai_media.config:成功加载用户配置文件: /path/to/user_config.py
```

或（如果使用 .env）：

```
INFO:xiaoai_media.config:未找到用户配置文件 user_config.py，使用默认配置
```

## 4. 验证功能

访问 http://localhost:5173，测试：

1. 设备列表是否显示
2. TTS 播报是否正常
3. 音乐播放是否正常

## 常见问题

### 使用 user_config.py 后还需要 .env 吗？

**不需要**。使用 `user_config.py` 后，`.env` 文件不再必需。

配置优先级：`user_config.py` > `.env` > 默认值

详见：[配置常见问题](CONFIG_FAQ.md#q1-使用-userconfigpy-后还需要-env-文件吗)

### Makefile 启动时如何加载配置？

**自动加载**。使用 `make backend` 或 `make dev` 启动时，配置会自动加载。

详见：[配置常见问题](CONFIG_FAQ.md#q2-使用-makefile-启动时配置如何加载)

### 音箱播放失败

将 `MUSIC_API_BASE_URL` 中的 `localhost` 改为本机局域网 IP：

```python
# 查看本机 IP
ifconfig  # macOS/Linux
ipconfig  # Windows

# 修改配置
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"  # 替换为你的 IP
```

### 唤醒词不工作

检查配置：
```python
WAKE_WORDS = ["小爱同学", "小爱"]  # 确保不为空
ENABLE_WAKE_WORD_FILTER = True     # 确保为 True
```

查看日志：
```bash
make backend
# 观察日志中的 "预处理后的指令" 信息
```

### 配置未生效

1. 确认文件名为 `user_config.py`（不是 `user_config_template.py`）
2. 确认文件在项目根目录
3. 重启服务
4. 查看启动日志，确认有 "成功加载用户配置文件" 提示

## 下一步

- [完整配置指南](USER_CONFIG_GUIDE.md) - 了解所有配置选项
- [TTS 功能文档](tts/README.md) - 文本转语音功能
- [对话监听功能](conversation/README.md) - 自动拦截播放指令

## 配置示例

### 示例 1: 基础配置

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
WAKE_WORDS = ["小爱同学"]
```

### 示例 2: 多唤醒词

```python
# user_config.py
WAKE_WORDS = [
    "小爱同学",
    "小爱",
    "小米",
]
```

### 示例 3: 不过滤唤醒词

```python
# user_config.py
ENABLE_WAKE_WORD_FILTER = False  # 处理所有指令
```

### 示例 4: 自定义过滤逻辑

```python
# user_config.py
def should_handle_command(query: str) -> bool:
    """只处理音乐相关指令"""
    if "播放" not in query and "音乐" not in query:
        return False
    return any(word in query for word in WAKE_WORDS)
```

## 获取帮助

- 查看 [完整文档](README.md)
- 提交 [Issue](https://github.com/your-repo/issues)
- 查看 [更新日志](../CHANGELOG.md)
