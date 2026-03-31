# 播放控制器 Bug 修复

## 问题描述

### 问题 1: 配置管理页面监控模式没有根据配置选中

**现象**：
- 打开配置管理页面
- 监控模式的单选按钮没有选中正确的值
- 即使后端配置为 `controller`，前端仍然显示 `monitor`

**原因**：
- `ConfigService.get_current_config()` 方法没有返回 `PLAYBACK_MODE` 字段
- 前端加载配置时，`PLAYBACK_MODE` 字段为 `undefined`
- 单选按钮使用默认值 `'monitor'`

### 问题 2: 保存配置时返回 422 错误

**现象**：
```
PUT http://localhost:5173/api/config 422 (Unprocessable Content)
```

**原因**：
- `ALLOWED_KEYS` 集合中没有包含 `PLAYBACK_MODE`
- 后端验证配置项时，认为 `PLAYBACK_MODE` 是未知的配置项
- 返回 422 错误

## 修复方案

### 修复 1: 在 ConfigService 中添加 PLAYBACK_MODE

**文件**: `backend/src/xiaoai_media/services/config_service.py`

#### 1.1 添加到 ALLOWED_KEYS

```python
# 允许通过API修改的配置项
ALLOWED_KEYS = {
    "MI_USER",
    "MI_PASS",
    "MI_DID",
    "MI_REGION",
    "MUSIC_API_BASE_URL",
    "MUSIC_DEFAULT_PLATFORM",
    "SERVER_BASE_URL",
    "ENABLE_CONVERSATION_POLLING",
    "CONVERSATION_POLL_INTERVAL",
    "ENABLE_PLAYBACK_MONITOR",
    "PLAYBACK_MONITOR_INTERVAL",
    "PLAYBACK_MODE",  # 新增
    "ENABLE_WAKE_WORD_FILTER",
    "WAKE_WORDS",
    "LOG_LEVEL",
    "PROXY_SKIP_AUTH_FOR_LAN",
    "PROXY_LAN_NETWORKS",
}
```

#### 1.2 在 get_current_config() 中返回 PLAYBACK_MODE

```python
@staticmethod
def get_current_config() -> dict:
    """获取当前配置（敏感字段会被掩码）"""
    return {
        "MI_USER": config.MI_USER,
        "MI_PASS": "***" if config.MI_PASS else "",
        "MI_DID": config.MI_DID,
        "MI_REGION": config.MI_REGION,
        "MUSIC_API_BASE_URL": config.MUSIC_API_BASE_URL,
        "MUSIC_DEFAULT_PLATFORM": config.MUSIC_DEFAULT_PLATFORM,
        "SERVER_BASE_URL": config.SERVER_BASE_URL,
        "ENABLE_CONVERSATION_POLLING": config.ENABLE_CONVERSATION_POLLING,
        "CONVERSATION_POLL_INTERVAL": config.CONVERSATION_POLL_INTERVAL,
        "ENABLE_PLAYBACK_MONITOR": config.ENABLE_PLAYBACK_MONITOR,
        "PLAYBACK_MONITOR_INTERVAL": config.PLAYBACK_MONITOR_INTERVAL,
        "PLAYBACK_MODE": getattr(config, "PLAYBACK_MODE", "monitor"),  # 新增
        "ENABLE_WAKE_WORD_FILTER": config.ENABLE_WAKE_WORD_FILTER,
        "WAKE_WORDS": config.WAKE_WORDS,
        "LOG_LEVEL": getattr(config, "LOG_LEVEL", "INFO"),
        "PROXY_SKIP_AUTH_FOR_LAN": getattr(config, "PROXY_SKIP_AUTH_FOR_LAN", True),
        "PROXY_LAN_NETWORKS": getattr(config, "PROXY_LAN_NETWORKS", [
            "192.168.0.0/16",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "127.0.0.0/8",
        ]),
    }
```

## 验证修复

### 测试步骤 1: 验证配置加载

1. 在 `user_config.py` 中设置：
   ```python
   PLAYBACK_MODE = "controller"
   ```

2. 重启服务或重新加载配置

3. 打开浏览器，访问配置管理页面

4. 检查"监控模式"是否选中"定时器模式"

**预期结果**：
- 单选按钮应该选中"定时器模式"
- 如果配置为 `monitor`，应该选中"轮询模式"

### 测试步骤 2: 验证配置保存

1. 在配置管理页面，切换监控模式

2. 点击"保存配置"按钮

3. 检查浏览器控制台和网络请求

**预期结果**：
- 不应该出现 422 错误
- 应该显示"配置保存成功！"
- 配置文件应该被正确更新

### 测试步骤 3: 验证配置持久化

1. 保存配置后，刷新页面

2. 检查监控模式是否保持选中状态

3. 查看 `user_config.py` 文件内容

**预期结果**：
- 页面刷新后，监控模式保持选中
- `user_config.py` 中包含正确的 `PLAYBACK_MODE` 值

## API 测试

### 获取配置

```bash
curl -X GET http://localhost:8000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应**：
```json
{
  "MI_USER": "your_account@example.com",
  "MI_PASS": "***",
  "MI_DID": "",
  "MI_REGION": "cn",
  "MUSIC_API_BASE_URL": "http://localhost:5050",
  "MUSIC_DEFAULT_PLATFORM": "tx",
  "SERVER_BASE_URL": "http://localhost:8000",
  "ENABLE_CONVERSATION_POLLING": true,
  "CONVERSATION_POLL_INTERVAL": 2.0,
  "ENABLE_PLAYBACK_MONITOR": true,
  "PLAYBACK_MONITOR_INTERVAL": 3.0,
  "PLAYBACK_MODE": "monitor",
  "ENABLE_WAKE_WORD_FILTER": true,
  "WAKE_WORDS": [],
  "LOG_LEVEL": "INFO",
  "PROXY_SKIP_AUTH_FOR_LAN": true,
  "PROXY_LAN_NETWORKS": [
    "192.168.0.0/16",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "127.0.0.0/8"
  ]
}
```

### 更新配置

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "PLAYBACK_MODE": "controller"
  }'
```

**预期响应**：
```json
{
  "message": "Configuration updated and reloaded successfully",
  "note": "All services have been updated with new configuration"
}
```

## 修复前后对比

### 修复前

| 操作 | 结果 |
|------|------|
| 加载配置页面 | 监控模式始终显示"轮询模式" |
| 切换到定时器模式并保存 | 返回 422 错误 |
| 查看 user_config.py | 没有 PLAYBACK_MODE 配置 |

### 修复后

| 操作 | 结果 |
|------|------|
| 加载配置页面 | 监控模式正确显示当前配置 |
| 切换到定时器模式并保存 | 保存成功 |
| 查看 user_config.py | 包含 PLAYBACK_MODE = "controller" |

## 相关文件

- `backend/src/xiaoai_media/services/config_service.py` - 配置服务
- `backend/src/xiaoai_media/api/routes/config.py` - 配置 API 路由
- `frontend/src/views/Settings.vue` - 前端配置页面
- `frontend/src/api/index.ts` - 前端 API 类型定义

## 总结

通过在 `ConfigService` 中添加 `PLAYBACK_MODE` 到 `ALLOWED_KEYS` 和 `get_current_config()` 方法，修复了以下问题：

1. ✅ 配置管理页面现在能正确显示当前的监控模式
2. ✅ 保存配置时不再返回 422 错误
3. ✅ 配置能够正确持久化到 `user_config.py`

这两个 bug 都是由于在添加新配置项时，忘记在配置服务中注册导致的。
