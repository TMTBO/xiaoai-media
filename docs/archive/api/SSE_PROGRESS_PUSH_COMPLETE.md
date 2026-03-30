# SSE 实时进度推送完整修复

## 问题描述

前端只在刷新页面时收到一次 SSE 数据，之后没有持续的进度更新。

## 根本原因

playback_monitor 没有监控通过语音命令播放的设备，导致状态变化不会被推送。

### 问题链路

1. 用户通过语音命令播放音乐
2. 设备开始播放（没有 `current_playlist_id`）
3. 用户打开/刷新页面，SSE 连接建立
4. `_get_initial_state` 返回当前状态（一次性）✅
5. playback_monitor 的 `_check_all_devices` 检查设备：
   ```python
   current_playlist_id = self._state_service.get(f"current_playlist_{device_id}")
   if not current_playlist_id:
       continue  # ← 跳过该设备！
   ```
6. 该设备不被监控 ❌
7. 状态变化不会触发 `_notify_status_change` ❌
8. SSE 不会推送新数据 ❌
9. 前端进度条不更新 ❌

## 完整修复方案

### 修复 1：扩大监控范围

**文件**：`backend/src/xiaoai_media/playback_monitor.py`

**修改**：`_check_all_devices` 方法

```python
# 检查设备上次的播放状态
last_status = self._last_status.get(device_id, {})
last_play_status = last_status.get("status", "stopped")

# 如果设备有播单，或者上次在播放/暂停状态，则检查状态
# 这样可以监控所有正在播放的设备，不管是否通过播单系统
should_check = (
    current_playlist_id or  # 有播单
    last_play_status in ["playing", "paused"]  # 上次在播放
)

if not should_check:
    continue
```

**效果**：
- 有播单的设备：继续监控 ✅
- 语音播放的设备：如果 `_last_status` 中有记录，也会监控 ✅

### 修复 2：初始化语音播放设备的状态

**文件**：`backend/src/xiaoai_media/playback_monitor.py`

**修改**：`check_and_resume` 方法

```python
if status_code == 1 and media_type == 3 and duration > 0:
    _log.info("检测到设备 %s 正在播放音乐，恢复监听状态", device_id)
    
    has_active_playback = True
    
    # 初始化该设备的状态（这样 _check_all_devices 就会监控它）
    position = play_song_detail.get("position", 0)
    audio_id = play_song_detail.get("audio_id", "")
    self._last_status[device_id] = {
        "status": "playing",
        "audio_id": audio_id,
        "position": position,
        "duration": duration,
        "media_type": media_type,
    }
```

**效果**：
- 应用启动时检测到正在播放的设备
- 初始化 `_last_status`，标记为 playing
- 后续轮询会继续监控该设备 ✅

### 修复 3：SSE 连接时启动 monitor

**文件**：`backend/src/xiaoai_media/api/routes/state.py`

**修改**：`event_generator` 函数

```python
# 注册回调
monitor = get_monitor()
monitor.add_status_callback(status_callback)
_log.info("SSE 全局状态客户端已连接: device_id=%s", device_id)

# 检查并启动 playback monitor（如果设备正在播放）
try:
    if not monitor.running:
        _log.info("playback_monitor 未运行，检查是否需要启动...")
        await monitor.check_and_resume()
except Exception as e:
    _log.warning("检查 playback_monitor 状态失败: %s", e)
```

**效果**：
- 如果 monitor 没有运行，在 SSE 连接时检查并启动
- 这样即使应用启动时设备没有播放，后来通过语音播放后，刷新页面也能启动 monitor ✅

### 修复 4：支持无播单的监控

**文件**：`backend/src/xiaoai_media/playback_monitor.py`

**修改**：`_check_device_status` 方法签名

```python
async def _check_device_status(
    self,
    client,
    device_id: str,
    playlist_id: str | None = None,  # ← 改为可选
):
```

**修改**：播放完成处理逻辑

```python
if position_rollback:
    # 只有在有播单时才自动播放下一曲
    if playlist_id:
        # ... 播放下一曲
    else:
        _log.debug(
            "检测到设备 %s 歌曲播放完成，但没有播单信息，不自动播放下一曲",
            device_id
        )
```

**效果**：
- 有播单：监控 + 自动播放下一曲 ✅
- 无播单：只监控，不自动播放下一曲 ✅

### 修复 5：回退获取歌曲信息

**文件**：`backend/src/xiaoai_media/api/routes/state.py`

**修改**：`_build_full_state` 方法

```python
# 如果没有从播单获取到歌曲信息，尝试从设备状态获取
if not current_song:
    try:
        # 重新获取完整的设备播放状态（包含 play_song_detail）
        status_result = await client.player_get_status(device_id)
        # ... 提取 play_song_detail
        _log.info("从设备状态获取歌曲信息: %s - %s", ...)
    except Exception as e:
        _log.warning("获取设备播放状态失败: %s", e)
```

**效果**：
- 有播单：从播单获取歌曲信息 ✅
- 无播单：从设备状态获取歌曲信息 ✅

## 完整工作流程

### 场景 1：应用启动时设备正在播放

1. 应用启动 → `startup_event`
2. 调用 `playback_monitor.check_and_resume()`
3. 检测到设备正在播放
4. 初始化 `_last_status[device_id]` = playing
5. 启动 playback_monitor
6. 每 3 秒检查状态，推送变化

### 场景 2：应用启动后通过语音播放

1. 应用启动 → monitor 未启动（没有设备在播放）
2. 用户对设备说"播放音乐"
3. 设备开始播放
4. 用户打开浏览器 → SSE 连接
5. `event_generator` 检查 monitor 状态
6. 调用 `monitor.check_and_resume()`
7. 检测到设备正在播放
8. 初始化 `_last_status[device_id]` = playing
9. 启动 playback_monitor
10. 每 3 秒检查状态，推送变化

### 场景 3：SSE 连接后通过语音播放

1. 用户打开浏览器 → SSE 连接
2. monitor 未启动（没有设备在播放）
3. 用户对设备说"播放音乐"
4. 设备开始播放
5. 下一次 `check_and_resume` 检查时（由其他 SSE 连接触发）
6. 检测到设备正在播放
7. 初始化 `_last_status[device_id]` = playing
8. 启动 playback_monitor
9. 每 3 秒检查状态，推送变化

**注意**：场景 3 可能有延迟，因为需要等待下一次 SSE 连接或其他触发。

## 优化建议（可选）

为了解决场景 3 的延迟问题，可以考虑：

### 方案 A：定期检查所有设备（不推荐）
- 在 `_check_all_devices` 中定期检查所有设备
- 缺点：增加 API 调用，性能开销大

### 方案 B：首次检查所有设备（推荐）
- 在 monitor 启动后的第一次轮询中，检查所有设备
- 之后只检查已知正在播放的设备
- 平衡性能和响应速度

### 方案 C：SSE 连接时触发检查（当前方案）
- 每次 SSE 连接时调用 `check_and_resume`
- 简单有效，延迟最多 3 秒

## 验证方法

### 测试步骤

1. **启动后端服务**
   ```bash
   cd backend && python run.py
   ```

2. **对设备说"播放音乐"**

3. **打开浏览器开发者工具**
   - Network → EventStream
   - 查看 `/api/state/stream` 连接

4. **观察 SSE 数据**
   - 应该每 3 秒收到一次 `event: state`
   - `position` 应该递增
   - `current_song` 应该有完整信息

### 预期日志

```
2026-03-27 18:40:00 INFO - SSE 全局状态客户端已连接: device_id=xxx
2026-03-27 18:40:00 INFO - playback_monitor 未运行，检查是否需要启动...
2026-03-27 18:40:00 INFO - 检测到设备 xxx 正在播放音乐，恢复监听状态
2026-03-27 18:40:00 INFO - 设备 xxx 没有播单信息（可能是语音播放），将监控状态但不自动播放下一曲
2026-03-27 18:40:00 INFO - 播放监控器已启动 (轮询间隔: 3.0秒)
2026-03-27 18:40:03 INFO - 设备 xxx 播放状态: status=playing(1), audio_id=xxx, position=135139/271107, media_type=3
2026-03-27 18:40:03 INFO - 从设备状态获取歌曲信息: 歌曲名 - 歌手名
2026-03-27 18:40:06 INFO - 设备 xxx 播放状态: status=playing(1), audio_id=xxx, position=138234/271107, media_type=3
```

### 预期 SSE 数据流

```
// 首次连接
event: state
data: {"device_id":"xxx","position":135139,"duration":271107,"current_song":{...}}

// 3 秒后（position 变化超过 1 秒）
event: state
data: {"device_id":"xxx","position":138234,"duration":271107,"current_song":{...}}

// 再 3 秒后
event: state
data: {"device_id":"xxx","position":141329,"duration":271107,"current_song":{...}}

// 30 秒后（如果没有状态变化）
event: heartbeat
data: {"timestamp":1743084030.123}
```

## 关键改进

1. ✅ **监控所有正在播放的设备**（不管是否有播单）
2. ✅ **SSE 连接时自动启动 monitor**（如果设备正在播放）
3. ✅ **初始化语音播放设备的状态**（在 `check_and_resume` 中）
4. ✅ **支持无播单的监控**（只监控，不自动播放下一曲）
5. ✅ **回退获取歌曲信息**（从设备状态获取）

## 相关文件

- `backend/src/xiaoai_media/playback_monitor.py` - 播放监控逻辑
- `backend/src/xiaoai_media/api/routes/state.py` - SSE 端点
- `frontend/src/composables/useGlobalState.ts` - 前端状态管理
- `frontend/src/components/GlobalPlayerBar.vue` - 播放器栏组件
