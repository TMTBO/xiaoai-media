# PLAYBACK_MODE 配置保存问题修复

## 问题描述

从配置管理页面更新 `PLAYBACK_MODE` 时，配置没有保存成功，刷新后还是 `monitor` 模式。

## 根本原因

在 `backend/src/xiaoai_media/config.py` 的 `reload_config()` 函数中，`PLAYBACK_MODE` 变量没有被声明为 `global`，导致：

1. 配置文件被正确更新
2. 但是重新加载配置时，`PLAYBACK_MODE` 被当作局部变量处理
3. 全局的 `PLAYBACK_MODE` 变量没有被更新
4. 下次读取配置时，仍然返回旧值

## 修复方案

### 修改 1: 在 reload_config() 中声明 PLAYBACK_MODE 为 global

**文件**: `backend/src/xiaoai_media/config.py`

**修改前**:
```python
def reload_config() -> None:
    global _user_config
    global MI_USER, MI_PASS, MI_DID, MI_REGION
    global MUSIC_API_BASE_URL, MUSIC_DEFAULT_PLATFORM
    global SERVER_BASE_URL
    global ENABLE_CONVERSATION_POLLING, CONVERSATION_POLL_INTERVAL
    global ENABLE_PLAYBACK_MONITOR, PLAYBACK_MONITOR_INTERVAL  # 缺少 PLAYBACK_MODE
    global WAKE_WORDS, ENABLE_WAKE_WORD_FILTER
    global LOG_LEVEL
    global PROXY_SKIP_AUTH_FOR_LAN, PROXY_LAN_NETWORKS
```

**修改后**:
```python
def reload_config() -> None:
    global _user_config
    global MI_USER, MI_PASS, MI_DID, MI_REGION
    global MUSIC_API_BASE_URL, MUSIC_DEFAULT_PLATFORM
    global SERVER_BASE_URL
    global ENABLE_CONVERSATION_POLLING, CONVERSATION_POLL_INTERVAL
    global ENABLE_PLAYBACK_MONITOR, PLAYBACK_MONITOR_INTERVAL, PLAYBACK_MODE  # 添加 PLAYBACK_MODE
    global WAKE_WORDS, ENABLE_WAKE_WORD_FILTER
    global LOG_LEVEL
    global PROXY_SKIP_AUTH_FOR_LAN, PROXY_LAN_NETWORKS
```

### 修改 2: 在 write_user_config() 中添加配置项不存在时的处理

**文件**: `backend/src/xiaoai_media/services/config_service.py`

**修改前**:
```python
if found:
    content = "\n".join(new_content)
```

**修改后**:
```python
if found:
    content = "\n".join(new_content)
else:
    # 如果配置项不存在，添加到文件末尾
    content += f"\n{key} = {val_str}\n"
```

这个修改确保即使配置文件中没有某个配置项，也能正确添加。

## 验证测试

### 测试脚本

创建了 `test_config_update.py` 测试脚本，验证配置更新功能：

```bash
python3 test_config_update.py
```

### 测试结果

```
============================================================
测试更新 PLAYBACK_MODE 配置
============================================================

1. 读取当前配置:
   PLAYBACK_MODE = controller

2. 更新配置为 'monitor':
   ✓ 配置写入成功

3. 重新加载配置:
   ✓ 配置重新加载成功

4. 验证配置:
   PLAYBACK_MODE = monitor
   ✓ 配置更新成功！

5. 恢复配置为 'controller':
   PLAYBACK_MODE = controller
   ✓ 配置已恢复

============================================================
✓ 所有测试通过！
============================================================
```

## 手动验证步骤

### 步骤 1: 更新配置

1. 打开浏览器，访问配置管理页面
2. 找到"播放监控"部分
3. 切换"监控模式"为"定时器模式"
4. 点击"保存配置"按钮

**预期结果**:
- 显示"配置保存成功！"
- 不出现 422 错误

### 步骤 2: 验证配置文件

```bash
grep "PLAYBACK_MODE" user_config.py
```

**预期输出**:
```
PLAYBACK_MODE = "controller"
```

### 步骤 3: 验证配置加载

1. 刷新配置管理页面
2. 检查"监控模式"是否选中"定时器模式"

**预期结果**:
- 单选按钮应该选中"定时器模式"

### 步骤 4: 验证配置生效

1. 查看服务日志
2. 应该看到类似的日志：

```
播放控制器已启动（定时器模式）
```

或者

```
播放监控器已启动（轮询模式）
```

## API 测试

### 获取配置

```bash
curl -X GET http://localhost:8000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应** (部分):
```json
{
  "PLAYBACK_MODE": "controller",
  ...
}
```

### 更新配置

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "PLAYBACK_MODE": "monitor"
  }'
```

**预期响应**:
```json
{
  "message": "Configuration updated and reloaded successfully",
  "note": "All services have been updated with new configuration"
}
```

### 再次获取配置验证

```bash
curl -X GET http://localhost:8000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应** (部分):
```json
{
  "PLAYBACK_MODE": "monitor",
  ...
}
```

## 相关问题修复

在修复这个问题的过程中，还发现并修复了以下相关问题：

1. ✅ `ConfigService.get_current_config()` 没有返回 `PLAYBACK_MODE`
2. ✅ `ALLOWED_KEYS` 中没有包含 `PLAYBACK_MODE`
3. ✅ `reload_config()` 中 `PLAYBACK_MODE` 没有声明为 `global`
4. ✅ `write_user_config()` 不能添加新的配置项

## 修改文件清单

1. `backend/src/xiaoai_media/config.py` - 添加 PLAYBACK_MODE 到 global 声明
2. `backend/src/xiaoai_media/services/config_service.py` - 添加 PLAYBACK_MODE 支持和新配置项添加逻辑
3. `test_config_update.py` - 新增测试脚本

## 总结

通过在 `reload_config()` 函数中将 `PLAYBACK_MODE` 声明为 `global` 变量，修复了配置保存后无法生效的问题。

现在配置管理页面可以正常保存和加载 `PLAYBACK_MODE` 配置了！

## 清理

测试完成后，可以删除测试脚本：

```bash
rm test_config_update.py
```
