# 播放功能快速指南

## 使用新的 miservice_fork API

### 基本播放流程

```python
from xiaoai_media.client import XiaoAiClient

async with XiaoAiClient() as client:
    # 1. 停止当前播放（确保干净状态）
    await client.player_stop(device_id)
    
    # 2. 播放新 URL
    result = await client.play_url(url, device_id, _type=1)
    
    # 3. 检查结果
    if result["result"]:
        print("✓ 播放成功")
    else:
        print("✗ 播放失败")
```

### 完整的播放控制

```python
# 播放
await client.play_url(url, device_id, _type=1)

# 暂停
await client.player_pause(device_id)

# 恢复
await client.player_play(device_id)

# 停止
await client.player_stop(device_id)

# 获取状态
status = await client.player_get_status(device_id)

# 设置循环模式
await client.player_set_loop(device_id, loop_type=1)  # 0=单曲, 1=列表
```

## API 接口使用

### 播放歌曲

```bash
POST /api/music/play
Content-Type: application/json

{
  "index": 0,
  "device_id": "设备ID"
}
```

**内部流程**:
1. 从播放列表获取歌曲
2. 获取播放 URL（带质量降级）
3. 停止当前播放
4. 调用 `play_url` 播放新歌曲

### 暂停

```bash
POST /api/music/pause
Content-Type: application/json

{
  "device_id": "设备ID"
}
```

使用 `player_pause()` API，比语音命令更可靠。

### 恢复

```bash
POST /api/music/resume
Content-Type: application/json

{
  "device_id": "设备ID"
}
```

使用 `player_play()` API。

### 停止

```bash
POST /api/music/stop
Content-Type: application/json

{
  "device_id": "设备ID"
}
```

使用 `player_stop()` API。

### 获取状态

```bash
GET /api/music/status?device_id=设备ID
```

返回当前播放状态。

## 关键改进

### 1. 自动停止当前播放

在 `play_music` 函数中，播放新歌曲前会自动停止：

```python
# 停止当前播放
await client.player_stop(req.device_id)

# 播放新歌曲
await client.play_url(url, req.device_id, _type=1)
```

### 2. 使用 play_by_music_url

所有播放都使用 `play_by_music_url`，这是最兼容的方法：

```python
result = await self._na_service.play_by_music_url(
    did, url, _type, audio_id, cp_id
)
```

### 3. 改进的结果检查

检查嵌套的 code 字段：

```python
data_code = result.get("data", {}).get("code")
result_code = result.get("code")
success = (data_code == 0) or (result_code == 0)
```

## 调试工具

### 运行调试测试

```bash
python test/music/test_playback_debug.py
```

这个脚本会：
1. 列出设备
2. 检查当前状态
3. 测试 TTS（验证连接）
4. 测试播放/暂停/恢复/停止
5. 提供详细的调试日志

### 查看详细日志

在 `.env` 中设置：
```env
LOG_LEVEL=DEBUG
```

或启动时：
```bash
export LOG_LEVEL=DEBUG
python -m uvicorn xiaoai_media.api.main:app --reload
```

## 常见问题

### Q: API 返回成功但音箱没有播放？

**A**: 可能的原因：
1. URL 无法访问（音箱网络问题）
2. 音频格式不支持（尝试 MP3 而非 FLAC）
3. 音箱正在执行其他任务
4. 需要先停止当前播放

**解决方案**:
- 代码已添加自动停止逻辑
- 运行 `test_playback_debug.py` 诊断
- 检查 URL 是否可以从音箱访问

### Q: 如何确认播放是否真的成功？

**A**: 检查播放状态：
```python
status = await client.player_get_status(device_id)
print(status)
```

### Q: 某些歌曲能播放，某些不能？

**A**: 可能是音频格式或 URL 问题：
- 优先使用 MP3 格式
- 检查 URL 是否需要认证
- 确保 URL 是直接的音频文件链接

## 最佳实践

1. **播放前先停止** - 确保音箱处于干净状态
2. **使用 _type=1** - 开启音乐模式（灯光效果）
3. **检查返回结果** - 验证 `result["result"]` 是否为 True
4. **添加错误处理** - 捕获异常并提供友好提示
5. **使用 MP3 格式** - 兼容性最好

## 示例：完整的播放流程

```python
async def play_song_example():
    async with XiaoAiClient() as client:
        device_id = "你的设备ID"
        url = "http://music.example.com/song.mp3"
        
        try:
            # 停止当前播放
            await client.player_stop(device_id)
            await asyncio.sleep(0.5)
            
            # 播放新歌曲
            result = await client.play_url(url, device_id, _type=1)
            
            if result["result"]:
                print(f"✓ 正在播放: {url}")
                
                # 等待几秒后检查状态
                await asyncio.sleep(2)
                status = await client.player_get_status(device_id)
                print(f"播放状态: {status}")
            else:
                print(f"✗ 播放失败: {result}")
                
        except Exception as e:
            print(f"错误: {e}")
```

## 参考

- [播放问题排查](PLAYBACK_TROUBLESHOOTING.md)
- [API 接口参考](API_REFERENCE.md)
- [MiService Fork GitHub](https://github.com/yihong0618/MiService)
