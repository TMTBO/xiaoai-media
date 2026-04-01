# 自动播放下一首

## 概述

自动播放下一首功能使用定时器模式，根据音频时长自动设置定时器，在歌曲结束前触发下一曲。

## 配置

播放控制器默认启用，无需额外配置。

## 工作原理

1. 播放控制器在播放开始时获取音频时长
2. 根据时长设置定时器，在歌曲结束前触发
3. 定时器触发时，自动调用 `PlaylistService.play_next_in_playlist()` 播放下一曲
4. 根据播放模式（列表循环、单曲循环、随机播放）选择下一首歌曲

## 播放模式

### 列表循环（Loop）

- 按顺序播放播单中的所有歌曲
- 播放到最后一首后，从第一首重新开始

### 单曲循环（Single）

- 重复播放当前歌曲
- 不会自动切换到下一首

### 随机播放（Random）

- 随机选择播单中的歌曲播放
- 避免连续播放同一首歌曲

## 使用示例

### 1. 创建播放列表

```bash
curl -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的播单",
    "description": "测试播单"
  }'
```

### 2. 添加音频文件

```bash
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/items \
  -H "Content-Type: application/json" \
  -d '{
    "title": "歌曲1",
    "url": "http://example.com/song1.mp3",
    "duration": 180
  }'
```

### 3. 开始播放

```bash
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/play \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "your_device_id",
    "start_index": 0
  }'
```

### 4. 设置播放模式

```bash
curl -X PUT http://localhost:8000/api/playlists/{playlist_id}/play-mode \
  -H "Content-Type: application/json" \
  -d '{
    "play_mode": "loop"
  }'
```

## 注意事项

1. **时长信息准确性**：定时器模式依赖音频文件的时长信息，如果时长不准确，可能导致切换时机不对
2. **缓冲时间**：默认缓冲时间为 1 秒，可以根据实际情况调整
3. **异常处理**：定时器模式无法检测手动停止等异常情况，建议配合前端状态监控使用

## 相关文档

- [播放控制器文档](../PLAYBACK_CONTROLLER.md)
- [播放控制器更新日志](../PLAYBACK_CONTROLLER_CHANGELOG.md)
- [自动播放实现](./AUTO_PLAY_IMPLEMENTATION.md)
