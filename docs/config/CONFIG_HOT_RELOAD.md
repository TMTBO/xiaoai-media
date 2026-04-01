# 配置热重载功能

## 概述

配置热重载功能允许在更新 `user_config.py` 后，无需手动重启服务即可使所有配置立即生效。

## 工作原理

### 1. 配置变更回调机制

在 `config.py` 中实现了配置变更回调机制：

- `register_config_change_callback(callback)`: 注册配置变更回调函数
- `unregister_config_change_callback(callback)`: 取消注册回调函数
- `reload_config()`: 重新加载配置并通知所有监听者

### 2. 自动重启相关服务

当配置更新时，系统会自动：

1. **重新加载配置文件**: 读取最新的 `user_config.py` 内容
2. **更新配置变量**: 更新所有全局配置变量
3. **通知监听者**: 调用所有注册的回调函数
4. **重启相关服务**:
   - 对话监听器 (ConversationPoller)
   - 播放控制器 (PlaybackController)
   - 日志级别

### 3. Uvicorn Reload 排除

为了避免 uvicorn 的自动重载机制与配置热重载冲突，在开发模式下配置了 `reload_excludes`：

```python
reload_excludes = [
    "user_config.py",      # 配置文件由热重载机制处理
    ".xiaoai_media/*",     # 数据目录
    "*.json",              # JSON 数据文件
    ".mi.token",           # Token 文件
]
```

这样可以确保：
- 修改 `user_config.py` 不会触发服务重启
- 配置热重载机制正常工作
- 其他代码文件的修改仍然会触发自动重载（开发模式）

### 4. 支持的配置项

所有通过 API 可修改的配置项都支持热重载：

- 小米账号配置: `MI_USER`, `MI_PASS`, `MI_DID`, `MI_REGION`
- 音乐服务配置: `MUSIC_API_BASE_URL`, `MUSIC_DEFAULT_PLATFORM`
- 服务器配置: `SERVER_BASE_URL`
- 对话监听配置: `ENABLE_CONVERSATION_POLLING`, `CONVERSATION_POLL_INTERVAL`
- 播放模式配置: `PLAYBACK_MODE`
- 唤醒词配置: `ENABLE_WAKE_WORD_FILTER`, `WAKE_WORDS`
- 日志配置: `LOG_LEVEL`
- 代理访问控制: `PROXY_SKIP_AUTH_FOR_LAN`, `PROXY_LAN_NETWORKS`

## 使用方法

### 通过 API 更新配置

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "CONVERSATION_POLL_INTERVAL": 3.0,
    "PLAYBACK_MODE": "controller",
    "LOG_LEVEL": "DEBUG"
  }'
```

响应：
```json
{
  "message": "Configuration updated and reloaded successfully",
  "note": "All services have been updated with new configuration"
}
```

### 配置变更流程

1. API 接收配置更新请求
2. 验证配置项是否允许修改
3. 写入 `user_config.py` 文件
4. 调用 `reload_config()` 重新加载配置
5. 触发所有注册的回调函数
6. 相关服务自动重启并应用新配置

### 技术实现

### 配置模块 (config.py)

```python
# 配置变更回调函数列表
_config_change_callbacks: list[Callable[[], None]] = []

def reload_config() -> None:
    """重新加载配置并通知所有监听者"""
    global _user_config
    global MI_USER, MI_PASS, MI_DID, MI_REGION
    # ... 更新所有配置变量
    
    # 重新加载用户配置
    _user_config = _load_user_config()
    
    # 更新所有配置变量
    MI_USER = _get_config("MI_USER", "")
    # ...
    
    # 通知所有监听者
    for callback in _config_change_callbacks:
        try:
            callback()
        except Exception as e:
            _log.error("配置变更回调执行失败: %s", e)
```

### 应用启动 (main.py)

```python
def on_config_changed():
    """配置变更回调：重启相关服务"""
    asyncio.create_task(_handle_config_change())

async def _handle_config_change():
    """异步处理配置变更"""
    # 1. 重启对话监听器
    if cfg.ENABLE_CONVERSATION_POLLING:
        conversation_poller.poll_interval = cfg.CONVERSATION_POLL_INTERVAL
        # ...
    
    # 2. 重启播放控制器
    from xiaoai_media.playback_controller import get_controller
    controller = get_controller()
    # ...
    
    # 3. 更新日志级别（更新所有已存在的 logger）
    log_level = cfg.LOG_LEVEL.upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 更新所有应用的 logger
    for name in logging.root.manager.loggerDict:
        if name.startswith(('xiaoai_media', 'uvicorn', 'fastapi')):
            logging.getLogger(name).setLevel(log_level)

# 注册回调
app_config.register_config_change_callback(on_config_changed)
```
```

## 注意事项

1. **配置文件格式**: 确保 `user_config.py` 格式正确，否则重载可能失败
2. **异常处理**: 如果某个回调函数执行失败，不会影响其他回调的执行
3. **异步操作**: 配置变更处理是异步的，不会阻塞 API 响应
4. **服务重启**: 某些服务（如对话监听器）会在配置变更时自动重启
5. **开发模式**: 在开发模式下（RELOAD=true），uvicorn 会排除 `user_config.py` 的监控，避免与热重载冲突
6. **生产模式**: 在生产模式下（RELOAD=false），配置热重载是唯一的配置更新方式
7. **日志级别**: 日志级别更新会应用到所有已存在的应用 logger（xiaoai_media, uvicorn, fastapi）

## 测试

运行测试验证配置热重载功能：

```bash
cd backend
pytest tests/test_config_reload.py -v
```

## 优势

1. **无需重启**: 配置更新后立即生效，无需手动重启服务
2. **零停机**: 服务持续运行，不会中断正在进行的操作
3. **自动化**: 所有相关服务自动感知配置变更并重启
4. **可扩展**: 其他模块可以注册自己的回调函数来响应配置变更

## 与旧版本的区别

### 旧版本
- 更新配置后需要手动重启服务
- 使用 `importlib.reload()` 重载模块（不可靠）
- 其他模块持有旧的配置引用

### 新版本
- 配置更新后自动生效
- 使用回调机制通知所有监听者
- 所有服务自动重启并应用新配置
