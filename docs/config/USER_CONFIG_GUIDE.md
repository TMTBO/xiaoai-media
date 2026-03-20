# 用户配置指南

本项目支持通过挂载外部 Python 文件来自定义配置和逻辑处理，参考了 [xiaomusic](https://github.com/hanxi/xiaomusic) 的设计理念。

## 快速开始

### 1. 创建配置文件

将项目根目录下的 `user_config_template.py` 复制为 `user_config.py`：

```bash
cp user_config_template.py user_config.py
```

### 2. 编辑配置

打开 `user_config.py`，根据需要修改配置项：

```python
# 小米账号配置
MI_USER = "your_account@example.com"
MI_PASS = "your_password"

# 音乐服务配置
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"  # 改为你的局域网IP
MUSIC_DEFAULT_PLATFORM = "tx"  # tx=腾讯, wy=网易云, kg=酷狗等

# 唤醒词配置
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

### 3. 启动服务

配置文件会在服务启动时自动加载：

```bash
make run
```

## 配置说明

### 基础配置

#### 小米账号配置

```python
MI_USER = "your_account@example.com"  # 小米账号
MI_PASS = "your_password"              # 小米密码
MI_PASS_TOKEN = ""                     # 可选，已有 token 可直接使用
MI_DID = ""                            # 可选，设备ID（不填则使用第一个设备）
MI_REGION = "cn"                       # 区域: cn, de, i2, ru, sg, us
```

#### 音乐服务配置

```python
MUSIC_API_BASE_URL = "http://localhost:5050"  # 音乐搜索服务地址
MUSIC_DEFAULT_PLATFORM = "tx"                 # 默认音乐平台
```

支持的音乐平台：
- `tx` - 腾讯音乐
- `wy` - 网易云音乐
- `kg` - 酷狗音乐
- `kw` - 酷我音乐
- `mg` - 咪咕音乐

#### 对话监听配置

```python
ENABLE_CONVERSATION_POLLING = True  # 是否启用对话监听
CONVERSATION_POLL_INTERVAL = 2.0    # 轮询间隔（秒）
```

### 唤醒词配置

#### 基本用法

```python
# 唤醒词列表
WAKE_WORDS = [
    "小爱同学",
    "小爱",
]

# 是否启用唤醒词过滤
ENABLE_WAKE_WORD_FILTER = True
```

- 当 `ENABLE_WAKE_WORD_FILTER = True` 时，只处理包含唤醒词的指令
- 当 `ENABLE_WAKE_WORD_FILTER = False` 时，处理所有指令
- 当 `WAKE_WORDS = []` 时，处理所有指令（即使过滤开启）

#### 工作原理

1. 用户说："小爱同学，播放周杰伦的晴天"
2. 系统检查是否包含唤醒词（"小爱同学" 或 "小爱"）
3. 如果包含，移除唤醒词，得到："播放周杰伦的晴天"
4. 解析并执行播放指令

### 高级功能：自定义处理函数

#### 自定义指令过滤

你可以自定义 `should_handle_command` 函数来实现更复杂的过滤逻辑：

```python
def should_handle_command(query: str) -> bool:
    """判断是否应该处理该指令"""
    
    # 示例1: 只处理包含"播放"的指令
    if "播放" not in query:
        return False
    
    # 示例2: 排除某些关键词
    if any(word in query for word in ["音量", "暂停", "停止"]):
        return False
    
    # 示例3: 时间段过滤（需要 import datetime）
    # from datetime import datetime
    # hour = datetime.now().hour
    # if hour < 8 or hour > 22:  # 只在 8:00-22:00 处理
    #     return False
    
    # 检查唤醒词
    for wake_word in WAKE_WORDS:
        if wake_word in query:
            return True
    
    return False
```

#### 自定义指令预处理

你可以自定义 `preprocess_command` 函数来标准化指令文本：

```python
def preprocess_command(query: str) -> str:
    """预处理指令文本"""
    
    # 移除唤醒词
    for wake_word in WAKE_WORDS:
        query = query.replace(wake_word, "")
    
    # 示例1: 替换同义词
    query = query.replace("放一首", "播放")
    query = query.replace("来一首", "播放")
    
    # 示例2: 标准化空格
    query = " ".join(query.split())
    
    # 示例3: 移除标点符号
    import string
    query = query.translate(str.maketrans("", "", string.punctuation))
    
    return query.strip()
```

### 日志配置

```python
LOG_LEVEL = "INFO"              # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
VERBOSE_PLAYBACK_LOG = False    # 是否显示详细的播放日志
```

## 配置优先级

系统按以下优先级加载配置：

1. **user_config.py** - 用户配置文件（最高优先级）
2. **.env** - 环境变量文件（向后兼容）
3. **默认值** - 代码中的默认值

这意味着：
- 如果存在 `user_config.py`，优先使用其中的配置
- 如果 `user_config.py` 中没有某个配置项，则从 `.env` 读取
- 如果都没有，使用默认值

## 向后兼容

如果你不创建 `user_config.py`，系统会继续使用 `.env` 文件，保持原有的工作方式。

## 使用示例

### 示例1: 只处理特定唤醒词

```python
# user_config.py

WAKE_WORDS = ["小爱同学"]  # 只响应"小爱同学"
ENABLE_WAKE_WORD_FILTER = True

# 其他配置...
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
```

### 示例2: 处理所有指令（不过滤）

```python
# user_config.py

ENABLE_WAKE_WORD_FILTER = False  # 关闭唤醒词过滤

# 其他配置...
```

### 示例3: 自定义复杂过滤逻辑

```python
# user_config.py

WAKE_WORDS = ["小爱同学", "小爱"]

def should_handle_command(query: str) -> bool:
    """只处理音乐相关的指令"""
    
    # 必须包含唤醒词
    has_wake_word = any(word in query for word in WAKE_WORDS)
    if not has_wake_word:
        return False
    
    # 必须包含音乐相关关键词
    music_keywords = ["播放", "放歌", "来首", "音乐"]
    has_music_keyword = any(word in query for word in music_keywords)
    
    return has_music_keyword

def preprocess_command(query: str) -> str:
    """标准化指令"""
    # 移除唤醒词
    for wake_word in WAKE_WORDS:
        query = query.replace(wake_word, "")
    
    # 统一播放指令
    query = query.replace("放歌", "播放")
    query = query.replace("来首", "播放")
    query = query.replace("来一首", "播放")
    
    return query.strip()
```

## 故障排查

### 配置文件未生效

1. 检查文件名是否为 `user_config.py`（不是 `user_config_template.py`）
2. 检查文件是否在项目根目录
3. 查看启动日志，确认是否有 "成功加载用户配置文件" 的提示
4. 检查配置文件语法是否正确（Python 语法）

### 唤醒词不工作

1. 确认 `ENABLE_WAKE_WORD_FILTER = True`
2. 确认 `WAKE_WORDS` 列表不为空
3. 检查唤醒词是否与实际语音指令匹配
4. 查看日志中的 "预处理后的指令" 信息

### 自定义函数报错

1. 检查函数签名是否正确
2. 检查函数内部是否有语法错误
3. 查看日志中的错误信息
4. 系统会在自定义函数失败时回退到默认逻辑

## 更多信息

- 查看 `user_config_template.py` 了解所有可配置项
- 查看 `backend/src/xiaoai_media/config.py` 了解配置加载逻辑
- 查看 `backend/src/xiaoai_media/command_handler.py` 了解指令处理流程
