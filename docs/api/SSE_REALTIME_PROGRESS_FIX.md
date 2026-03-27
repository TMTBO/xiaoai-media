# SSE 实时播放进度推送修复

## 问题描述

播单信息和音频信息都能正确显示，但是播放进度没有实时推送下来。

## 原因分析

在 `playback_monitor.py` 的 `_check_all_devices` 方法中：

```python
# 检查该设备是否有正在播放的播单
current_playlist_id = self._state_service.get(
    f"current_playlist_{device_id}"
)
if not current_playlist_id:
    continue  # ← 跳过了没有播单的设备！
```

这导致：
1. 通过语音命令播放的设备（没有 `current_playlist_id`）不会被监控
2. playback_monitor 不会检查这些设备的状态
3. 状态变化不会被推送到 SSE
4. 前端播放器栏的进度条不会更新

## 修复方案

### 修改文件
- `backend/src/xiaoai_media/playback_monitor.py`
- `backend/src/xiaoai_media/api/routes/state.py`

### 修复 1：监控所有正在播放的设备

修改 `_check_all_devices` 方法，不再只监控有播单的设备：

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

### 修复 2：初始化语音播放设备的状态

修改 `check_and_resume` 方法，在检测到正在播放的设备时初始化其状态：

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

### 修复 3：支持无播单的自动播放下一曲

修改 `_check_device_status` 方法，让 `playlist_id` 参数变为可选：

```python
async def _check_device_status(
    self,
    client,
    device_id: str,
    playlist_id: str | None = None,  # ← 改为可选
):
    """检查单个设备的播放状态
    
    Args:
        client: XiaoAI 客户端
        device_id: 设备 ID
        playlist_id: 当前播放的播单 ID（可选，如果为空则不自动播放下一曲）
    """
```

在检测到歌曲播放完成时：

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

### 修复 4：回退获取歌曲信息

修改 `state.py` 的 `_build_full_state` 方法，当没有播单信息时从设备状态获取：

```python
# 如果没有从播单获取到歌曲信息，尝试从设备状态获取
if not current_song:
    try:
        # 重新获取完整的设备播放状态（包含 play_song_detail）
        status_result = await client.player_get_status(device_id)
        # ... 从 play_song_detail 提取歌曲信息
        _log.info("从设备状态获取歌曲信息: %s - %s", 
                 current_song.get("name"), current_song.get("singer"))
    except Exception as e:
        _log.warning("获取设备播放状态失败: %s", e)
```

## 工作流程

### 场景 1：通过播单播放
1. 用户通过 API 播放播单
2. `PlaylistService.play_playlist` 保存 `current_playlist_{device_id}`
3. playback_monitor 启动并监控该设备
4. 每 3 秒检查状态，position 变化超过 1 秒时推送
5. SSE 推送完整状态（包含播单信息）
6. 歌曲播放完成时自动播放下一曲

### 场景 2：通过语音播放
1. 用户对设备说"播放音乐"
2. 设备开始播放（没有 `current_playlist_id`）
3. 后端启动时 `check_and_resume` 检测到正在播放
4. 初始化 `_last_status[device_id]`（标记为 playing）
5. playback_monitor 启动并监控该设备
6. 每 3 秒检查状态，position 变化超过 1 秒时推送
7. SSE 推送完整状态（从设备状态获取歌曲信息）
8. 歌曲播放完成时不自动播放下一曲（因为没有播单）

### 场景 3：SSE 连接后开始播放
1. 前端连接 SSE（此时设备未播放）
2. 用户对设备说"播放音乐"
3. 设备开始播放
4. 下一次 playback_monitor 检查时（最多 3 秒）：
   - 检测到新的播放状态
   - 初始化 `_last_status[device_id]`
   - 推送状态变化到 SSE
5. 前端播放器栏显示

## 推送频率

- **轮询间隔**：3 秒
- **推送条件**：
  - 播放状态变化（playing/paused/stopped）
  - audio_id 变化（切换歌曲）
  - **position 变化超过 1 秒**（确保进度实时更新）

## 验证方法

1. 启动后端服务
2. 对设备说"播放音乐"
3. 打开浏览器开发者工具，查看 Network → EventStream
4. 观察 SSE 推送的数据：
   - 应该每 3 秒推送一次（position 变化）
   - `current_song` 应该有完整信息
   - `position` 应该递增

### 预期日志输出

```
2026-03-27 18:36:00 INFO - 检测到设备 xxx 正在播放音乐，恢复监听状态
2026-03-27 18:36:00 INFO - 设备 xxx 没有播单信息（可能是语音播放），将监控状态但不自动播放下一曲
2026-03-27 18:36:00 INFO - 播放监控器已启动 (轮询间隔: 3.0秒)
2026-03-27 18:36:03 INFO - 设备 xxx 播放状态: status=playing(1), audio_id=xxx, position=135139/271107, media_type=3
2026-03-27 18:36:03 INFO - 从设备状态获取歌曲信息: 歌曲名 - 歌手名
2026-03-27 18:36:06 INFO - 设备 xxx 播放状态: status=playing(1), audio_id=xxx, position=138234/271107, media_type=3
```

### 预期 SSE 数据

```
event: state
data: {"device_id":"xxx","play_status":"playing","position":135139,"duration":271107,...}

event: state
data: {"device_id":"xxx","play_status":"playing","position":138234,"duration":271107,...}

event: state
data: {"device_id":"xxx","play_status":"playing","position":141329,"duration":271107,...}
```

## 性能影响

- 监控范围扩大：从"只监控有播单的设备"改为"监控所有正在播放的设备"
- API 调用增加：每个正在播放的设备每 3 秒调用一次 `player_get_status`
- 对于语音播放，额外调用一次 `player_get_status` 获取歌曲信息（仅在构建完整状态时）

## 相关文件

- `backend/src/xiaoai_media/playback_monitor.py` - 播放监控逻辑
- `backend/src/xiaoai_media/api/routes/state.py` - SSE 端点和状态构建
- `frontend/src/composables/useGlobalState.ts` - 前端状态管理
- `frontend/src/components/GlobalPlayerBar.vue` - 播放器栏组件
