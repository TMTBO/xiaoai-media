# PlaybackController 重构总结

**日期**: 2026-03 (历史记录)  
**类型**: 代码重构  
**影响范围**: playback_controller.py

## 重构目标

整理和抽离 `playback_controller.py` 中的重复或相近代码，提高代码复用性和可维护性。

## 问题背景

在重构前，`playback_controller.py` 中存在多处重复的代码模式：
1. 设备状态更新 + 通知订阅者的模式重复出现
2. 播单 ID 获取逻辑在多处重复
3. 播放信息获取和解析逻辑重复
4. 停止播放的操作序列重复

## 解决方案

### 新增辅助方法

#### 1. `_update_device_status(device_id, status_update)`

**作用**: 统一处理设备状态更新和通知订阅者

**替代模式**:
```python
# 之前的重复代码
self._device_status[device_id].update(status_update)
await self._notify_status_change(device_id, self._device_status[device_id])
```

**使用位置**:
- `on_play_started()`
- `on_play_paused()`
- `on_play_stopped()`

**优势**: 确保状态更新和通知的一致性，避免遗漏通知

---

#### 2. `_get_current_playlist_id(device_id)`

**作用**: 统一获取设备当前播单 ID 的逻辑

**替代模式**:
```python
# 之前的重复代码
state_service = get_state_service()
playlist_id = state_service.get(f"current_playlist_{device_id}")
```

**使用位置**:
- `check_and_resume()`
- `_on_playback_finished()`

**优势**: 播单 ID 获取逻辑集中管理，便于修改键名格式

---

#### 3. `_get_device_playback_info(device_id)`

**作用**: 统一获取设备播放信息（duration, position, status_code, media_type）

**替代模式**:
```python
# 之前的重复代码
client = get_client_sync()
status_result = await client.player_get_status(device_id)
status_data = status_result.get("status", {})
data = status_data.get("data", {})
info_str = data.get("info", "{}")
# ... 解析 JSON ...
```

**使用位置**:
- `check_and_resume()`
- `on_play_resumed()`

**优势**: 播放状态解析逻辑集中，便于维护和调试

**注意**: 此方法在后续的 `player_get_status` 重构中得到进一步简化

---

#### 4. `_stop_current_playback(device_id)`

**作用**: 统一停止当前播放的逻辑

**替代模式**:
```python
# 之前的重复代码
_log.info("停止当前播放...")
client = get_client_sync()
await client.player_stop(device_id)
await asyncio.sleep(0.5)
```

**使用位置**:
- `_play_next()`

**优势**: 停止播放的操作序列（包括等待时间）集中管理

---

## 重构效果

### 代码量
- 原代码: ~500 行
- 重构后: ~480 行
- **减少约 20 行重复代码**

### 可维护性提升

1. **状态更新逻辑统一**: 所有状态更新都通过 `_update_device_status()` 进行，确保状态更新和通知的一致性
2. **播放信息获取统一**: 播放状态解析逻辑集中在 `_get_device_playback_info()` 中，便于维护和调试
3. **播单 ID 获取统一**: 避免在多处重复相同的获取逻辑
4. **停止播放逻辑统一**: 停止播放的操作序列集中管理

### 可读性提升

- 方法职责更加清晰
- 减少了代码重复，降低了认知负担
- 辅助方法命名清晰，易于理解

### 维护成本降低

- 修改状态更新逻辑时，只需修改一处
- 修改播放信息获取逻辑时，只需修改一处
- 减少了因多处修改导致的不一致风险

## 测试验证

- ✓ 语法检查通过
- ✓ 所有关键方法存在
- ✓ 代码结构完整

## 兼容性

- 保持所有公共接口不变
- 不影响现有调用代码
- 向后兼容

## 后续改进

此重构为后续的 `player_get_status` 解析逻辑重构奠定了基础。在 2026-04-01 的重构中，`_get_device_playback_info()` 方法得到了进一步简化，从 30+ 行减少到 7 行。

参见：[PLAYER_STATUS_REFACTOR_2026_04_01.md](./PLAYER_STATUS_REFACTOR_2026_04_01.md)

## 相关文件

- `backend/src/xiaoai_media/playback_controller.py`
