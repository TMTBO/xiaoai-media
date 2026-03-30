# SSE 歌曲信息显示修复

## 问题描述

SSE 推送的数据中 `current_song` 字段为空：
```json
{
  "current_song": {
    "name": "",
    "singer": "",
    "album": "",
    "cover": "",
    "audio_id": "1774607406199261"
  },
  "playlist": null
}
```

## 原因分析

1. 设备通过语音命令播放，没有通过播放列表系统
2. `StateService` 中 `current_playlist_{device_id}` 为 null
3. `_build_full_state` 函数中的回退逻辑（从设备状态获取歌曲信息）没有正确执行

## 修复方案

### 修改文件
`backend/src/xiaoai_media/api/routes/state.py`

### 修复内容

1. **添加完整的回退逻辑**
   - 当 `current_playlist_id` 为空时，重新调用 `client.player_get_status(device_id)` 获取完整的设备状态
   - 从 `play_song_detail` 中提取歌曲信息（name, singer, album_name, cover, audio_id）
   - 添加日志记录，便于调试

2. **移除不必要的导入**
   - 移除了 `from xiaoai_media.player import get_player`（未使用，且可能导致循环导入）

### 修复后的代码

```python
# 如果没有从播单获取到歌曲信息，尝试从设备状态获取
if not current_song:
    try:
        # 重新获取完整的设备播放状态（包含 play_song_detail）
        status_result = await client.player_get_status(device_id)
        status_data = status_result.get("status", {})
        data = status_data.get("data", {})
        info_str = data.get("info", "{}")
        
        try:
            info = json.loads(info_str)
        except (json.JSONDecodeError, TypeError):
            info = {}
        
        play_song_detail = info.get("play_song_detail", {})
        if play_song_detail:
            current_song = {
                "name": play_song_detail.get("name", ""),
                "singer": play_song_detail.get("singer", ""),
                "album": play_song_detail.get("album_name", ""),
                "cover": play_song_detail.get("cover", ""),
                "audio_id": play_song_detail.get("audio_id", ""),
            }
            _log.info("从设备状态获取歌曲信息: %s - %s", 
                     current_song.get("name"), current_song.get("singer"))
    except Exception as e:
        _log.warning("获取设备播放状态失败: %s", e)
```

## 验证方法

### 场景 1：通过播放列表播放
1. 通过 API 播放播单：`POST /api/playlists/{id}/play`
2. 连接 SSE：`GET /api/state/stream?device_id={deviceId}`
3. 验证返回的 `current_song` 包含完整信息（从播单获取）
4. 验证 `playlist` 包含播单信息

### 场景 2：通过语音命令播放
1. 对设备说："小爱同学，播放音乐"
2. 连接 SSE：`GET /api/state/stream?device_id={deviceId}`
3. 验证返回的 `current_song` 包含完整信息（从设备状态获取）
4. `playlist` 为 null（正常）

### 场景 3：实时状态更新
1. 播放音乐
2. 观察 SSE 推送的数据（每 3 秒或状态变化时）
3. 验证 `position` 实时更新
4. 验证切歌时 `current_song` 更新

## 预期结果

### 通过播单播放
```json
{
  "device_id": "xxx",
  "play_status": "playing",
  "position": 135139,
  "duration": 271107,
  "current_song": {
    "name": "歌曲名",
    "singer": "歌手名",
    "album": "专辑名",
    "cover": "https://...",
    "audio_id": "1774607406199261"
  },
  "playlist": {
    "id": "playlist_xxx",
    "name": "我的播单",
    "current": 2,
    "total": 10,
    "play_mode": "loop"
  }
}
```

### 通过语音播放
```json
{
  "device_id": "xxx",
  "play_status": "playing",
  "position": 135139,
  "duration": 271107,
  "current_song": {
    "name": "歌曲名",
    "singer": "歌手名",
    "album": "专辑名",
    "cover": "https://...",
    "audio_id": "1774607406199261"
  },
  "playlist": null
}
```

## 相关文件

- `backend/src/xiaoai_media/api/routes/state.py` - SSE 端点实现
- `backend/src/xiaoai_media/playback_monitor.py` - 播放监控和状态推送
- `frontend/src/composables/useGlobalState.ts` - 前端状态管理
- `frontend/src/components/GlobalPlayerBar.vue` - 播放器栏组件

## 注意事项

1. **性能考虑**：回退逻辑会额外调用一次 `player_get_status` API，但只在没有播单信息时才会调用
2. **日志记录**：添加了日志记录，便于调试和监控
3. **错误处理**：所有 API 调用都有 try-catch 保护，确保不会因为单个错误导致整个 SSE 连接断开
