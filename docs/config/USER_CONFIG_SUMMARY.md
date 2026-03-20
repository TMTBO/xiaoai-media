# 用户配置系统总结

## 概述

本项目实现了一个灵活的用户配置系统，参考了 [xiaomusic](https://github.com/hanxi/xiaomusic) 的设计理念，允许用户通过挂载外部 Python 文件来自定义配置和处理逻辑。

## 核心特性

### 1. 配置文件支持

- **Python 配置文件** (`user_config.py`) - 推荐方式，支持所有高级功能
- **环境变量文件** (`.env`) - 向后兼容，简单快速

### 2. 唤醒词过滤

- 只处理包含指定唤醒词的指令
- 支持多个唤醒词
- 可完全关闭过滤

### 3. 自定义处理函数

- `should_handle_command()` - 自定义指令过滤逻辑
- `preprocess_command()` - 自定义指令预处理逻辑

### 4. 配置优先级

```
user_config.py > .env > 默认值
```

## 文件结构

```
xiaoai-media/
├── user_config_template.py      # 完整配置模板
├── user_config.example.py       # 简化配置示例
├── user_config.py               # 用户配置（需自行创建，已加入 .gitignore）
├── .env.example                 # 环境变量模板
├── .env                         # 环境变量配置（已加入 .gitignore）
├── backend/src/xiaoai_media/
│   ├── config.py                # 配置加载逻辑
│   └── command_handler.py       # 指令处理（集成唤醒词过滤）
├── test/
│   └── test_user_config.py      # 配置系统测试
└── docs/
    ├── USER_CONFIG_GUIDE.md     # 完整配置指南
    ├── QUICK_CONFIG.md          # 快速配置指南
    └── USER_CONFIG_SUMMARY.md   # 本文件
```

## 实现细节

### 配置加载流程

1. 检查项目根目录是否存在 `user_config.py`
2. 如果存在，动态加载该 Python 模块
3. 如果不存在，从 `.env` 文件加载配置
4. 对于每个配置项，按优先级读取：
   - 首先从 `user_config.py` 读取
   - 其次从环境变量读取
   - 最后使用默认值

### 唤醒词处理流程

```
用户指令 → should_handle_command() → preprocess_command() → 指令解析 → 执行
           ↓                         ↓
           检查唤醒词                 移除唤醒词
           ↓                         ↓
           返回 True/False           返回处理后的指令
```

### 代码示例

#### config.py 核心逻辑

```python
def _load_user_config() -> Any | None:
    """尝试加载用户配置文件"""
    if not _user_config_path.exists():
        return None
    
    spec = importlib.util.spec_from_file_location("user_config", _user_config_path)
    if spec and spec.loader:
        user_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_config)
        return user_config
    return None

def _get_config(key: str, default: Any = "") -> Any:
    """获取配置值，优先从用户配置文件读取"""
    if _user_config is not None and hasattr(_user_config, key):
        return getattr(_user_config, key)
    
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value.strip() or default
    
    return default
```

#### command_handler.py 集成

```python
async def handle_command(self, device_id: str, query: str):
    """处理语音指令"""
    # 检查是否应该处理该指令（唤醒词过滤）
    if not config.should_handle_command(query):
        _log.debug("指令未包含唤醒词，忽略: %s", query)
        return
    
    # 预处理指令（移除唤醒词等）
    processed_query = config.preprocess_command(query)
    
    # 解析并执行指令
    play_info = self._parse_play_command(processed_query)
    if play_info:
        await self._handle_play_command(device_id, play_info["query"])
```

## 配置项说明

### 基础配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `MI_USER` | str | "" | 小米账号 |
| `MI_PASS` | str | "" | 小米密码 |
| `MI_PASS_TOKEN` | str | "" | 小米密码令牌 |
| `MI_DID` | str | "" | 设备 ID |
| `MI_REGION` | str | "cn" | 区域 |
| `MUSIC_API_BASE_URL` | str | "http://localhost:5050" | 音乐服务地址 |
| `MUSIC_DEFAULT_PLATFORM` | str | "tx" | 默认音乐平台 |

### 对话监听配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ENABLE_CONVERSATION_POLLING` | bool | True | 启用对话监听 |
| `CONVERSATION_POLL_INTERVAL` | float | 2.0 | 轮询间隔（秒） |

### 唤醒词配置（新增）

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `WAKE_WORDS` | list[str] | [] | 唤醒词列表 |
| `ENABLE_WAKE_WORD_FILTER` | bool | True | 启用唤醒词过滤 |

### 日志配置（新增）

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `LOG_LEVEL` | str | "INFO" | 日志级别 |
| `VERBOSE_PLAYBACK_LOG` | bool | False | 详细播放日志 |

## 使用场景

### 场景 1: 基础用户

不需要唤醒词过滤，使用 `.env` 文件即可。

```env
# .env
MI_USER=your_account@example.com
MI_PASS=your_password
MUSIC_API_BASE_URL=http://192.168.1.100:5050
```

### 场景 2: 需要唤醒词过滤

创建 `user_config.py`，配置唤醒词。

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"

WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

### 场景 3: 自定义处理逻辑

实现自定义函数，完全控制指令处理。

```python
# user_config.py
WAKE_WORDS = ["小爱同学"]

def should_handle_command(query: str) -> bool:
    """只处理音乐相关指令"""
    if "小爱同学" not in query:
        return False
    return "播放" in query or "音乐" in query

def preprocess_command(query: str) -> str:
    """标准化指令"""
    query = query.replace("小爱同学", "")
    query = query.replace("，", "")
    return query.strip()
```

## 测试

### 运行测试

```bash
# 使用 Makefile
make test-config

# 或直接运行
python3 test/test_user_config.py
```

### 测试输出

```
============================================================
配置加载测试
============================================================

小米账号配置:
  MI_USER: your_account@example.com
  ...

唤醒词配置:
  WAKE_WORDS: ['小爱同学', '小爱']
  ENABLE_WAKE_WORD_FILTER: True

============================================================
唤醒词过滤测试
============================================================

原始指令: 小爱同学，播放周杰伦的晴天
  是否处理: True
  预处理后: 播放周杰伦的晴天

原始指令: 播放周杰伦的晴天
  是否处理: False
  预处理后: (未处理)
```

## 向后兼容

- 如果不创建 `user_config.py`，系统继续使用 `.env` 文件
- 所有现有配置项保持不变
- 新增配置项有合理的默认值
- 不影响现有功能

## 故障排查

### 配置文件未生效

1. 检查文件名是否为 `user_config.py`
2. 检查文件是否在项目根目录
3. 查看启动日志，确认有 "成功加载用户配置文件" 提示
4. 运行 `make test-config` 验证配置

### 唤醒词不工作

1. 确认 `ENABLE_WAKE_WORD_FILTER = True`
2. 确认 `WAKE_WORDS` 不为空
3. 查看日志中的 "预处理后的指令" 信息
4. 运行 `make test-config` 查看唤醒词配置

### 自定义函数报错

1. 检查函数签名是否正确
2. 检查函数内部是否有语法错误
3. 查看日志中的错误信息
4. 系统会在自定义函数失败时回退到默认逻辑

## 参考资料

- [xiaomusic](https://github.com/hanxi/xiaomusic) - 设计灵感来源
- [完整配置指南](USER_CONFIG_GUIDE.md) - 详细使用说明
- [快速配置指南](QUICK_CONFIG.md) - 5分钟快速开始
- [配置模板](../user_config_template.py) - 完整配置选项

## 更新日志

- 2024-XX-XX: 初始实现
  - 支持 Python 配置文件
  - 支持唤醒词过滤
  - 支持自定义处理函数
  - 向后兼容 .env 配置

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT
