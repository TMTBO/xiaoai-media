# 统一 Logger 管理

## 概述

为了更好地管理日志，我们将所有模块的 logger 实例统一为一个全局 logger。这样可以：

1. 统一管理日志级别
2. 简化日志配置
3. 更容易实现日志级别热更新
4. 减少 logger 实例的创建开销

## 实现

### Logger 模块 (logger.py)

创建了一个新的 `logger.py` 模块，提供全局 logger 实例：

```python
from xiaoai_media.logger import get_logger

# 获取全局 logger
logger = get_logger()

# 使用 logger
logger.info("这是一条日志")
logger.debug("调试信息")
logger.error("错误信息", exc_info=True)
```

### 主要功能

#### 1. 获取 Logger

```python
from xiaoai_media.logger import get_logger

logger = get_logger()
```

#### 2. 设置日志级别

```python
from xiaoai_media.logger import set_log_level

# 设置为 DEBUG 级别
set_log_level("DEBUG")

# 设置为 INFO 级别
set_log_level("INFO")
```

`set_log_level()` 函数会自动更新：
- 全局 logger 的级别
- 所有 `xiaoai_media.*` 子模块的 logger 级别

#### 3. 便捷函数

也可以直接使用便捷函数：

```python
from xiaoai_media import logger

logger.info("信息日志")
logger.debug("调试日志")
logger.warning("警告日志")
logger.error("错误日志")
logger.exception("异常日志")  # 自动包含堆栈信息
```

## 迁移指南

### 旧代码

```python
import logging

_log = logging.getLogger(__name__)

def some_function():
    _log.info("这是一条日志")
```

### 新代码

```python
import logging
from xiaoai_media.logger import get_logger

_log = get_logger()

def some_function():
    _log.info("这是一条日志")
```

### 自动迁移

我们提供了自动迁移脚本：

```bash
cd backend
python migrate_to_unified_logger.py
```

该脚本会自动：
1. 添加 `from xiaoai_media.logger import get_logger` 导入
2. 替换 `logging.getLogger(__name__)` 为 `get_logger()`
3. 更新所有相关文件

## 优势

### 1. 统一管理

所有模块使用同一个 logger 实例，便于统一配置和管理。

### 2. 热更新支持

配置热重载时，只需调用 `set_log_level()` 即可更新所有模块的日志级别：

```python
from xiaoai_media.logger import set_log_level
from xiaoai_media import config

# 配置变更时
set_log_level(config.LOG_LEVEL)
```

### 3. 性能优化

减少了 logger 实例的创建，提高了性能。

### 4. 简化代码

不需要在每个模块中都写 `logging.getLogger(__name__)`。

## 与配置热重载的集成

在配置热重载时，日志级别会自动更新：

```python
# main.py
async def _handle_config_change():
    # ...
    
    # 更新日志级别
    if hasattr(cfg, 'LOG_LEVEL'):
        from xiaoai_media.logger import set_log_level
        set_log_level(cfg.LOG_LEVEL)
        logger.info("日志级别已更新: %s", cfg.LOG_LEVEL)
```

## 注意事项

1. **导入顺序**: `logger.py` 不应该导入其他应用模块，避免循环依赖
2. **第三方库**: 第三方库的 logger 不受影响，仍然使用各自的 logger
3. **向后兼容**: 旧代码仍然可以工作，但建议迁移到新的方式

## 已迁移的模块

以下模块已经迁移到统一 logger：

- ✅ `client.py`
- ✅ `command_handler.py`
- ✅ `conversation.py`
- ✅ `player.py`
- ✅ `scheduler_executor.py`
- ✅ `config.py`
- ✅ `services/music_service.py`
- ✅ `services/playlist_loader.py`
- ✅ `services/playlist_service.py`
- ✅ `services/playlist_storage.py`
- ✅ `services/scheduler_service.py`
- ✅ `services/state_service.py`
- ✅ `services/voice_command_service.py`
- ✅ `api/routes/music.py`
- ✅ `api/routes/playlist.py`
- ✅ `api/routes/proxy.py`
- ✅ `api/routes/scheduler.py`
- ✅ `api/routes/state.py`

## 示例

### 基本使用

```python
from xiaoai_media.logger import get_logger

logger = get_logger()

def process_data(data):
    logger.info("开始处理数据: %s", data)
    
    try:
        # 处理逻辑
        result = do_something(data)
        logger.debug("处理结果: %s", result)
        return result
    except Exception as e:
        logger.error("处理失败: %s", e, exc_info=True)
        raise
```

### 动态调整日志级别

```python
from xiaoai_media.logger import set_log_level, get_log_level

# 获取当前级别
current_level = get_log_level()
print(f"当前日志级别: {current_level}")

# 设置为 DEBUG
set_log_level("DEBUG")

# 设置为 INFO
set_log_level("INFO")
```

## 相关文档

- [配置热重载](CONFIG_HOT_RELOAD.md)
- [日志配置](../log_config.py)
