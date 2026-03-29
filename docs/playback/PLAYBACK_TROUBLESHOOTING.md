# 播放问题排查指南

## 问题：API返回成功但音箱没有播放

### 症状
日志显示：
```
INFO: play_by_music_url result: {'code': 0, 'message': 'Msg has been successfully proxy...', 'data': {'code': 0}}
```

但音箱没有声音或播放失败。

### 可能原因和解决方案

#### 1. 音箱正在播放其他内容

**解决方案**: 在播放前先停止当前播放

代码已更新，会在播放新歌曲前自动调用 `player_stop()`：

```python
# 在 music.py 的 play_music 函数中
await client.player_stop(req.device_id)  # 先停止
await client.play_url(url, req.device_id, _type=1)  # 再播放
```

#### 2. URL 格式问题

某些音乐平台的 URL 可能包含特殊字符或需要特定的 headers。

**检查方法**:
```bash
# 测试 URL 是否可访问
curl -I "你的音乐URL"
```

**解决方案**:
- 确保 URL 是直接的音频文件链接
- 检查 URL 是否需要认证或特殊 headers
- 尝试使用不同音质的 URL

#### 3. 音箱网络问题

音箱可能无法访问外部 URL。

**检查方法**:
```python
# 测试播放一个简单的本地 URL
await client.play_url("http://你的本地IP:端口/test.mp3", device_id)
```

**解决方案**:
- 确保音箱和服务器在同一网络
- 检查防火墙设置
- 尝试使用音箱可以访问的公网 URL

#### 4. 音频格式不支持

某些音箱可能不支持特定的音频格式（如 FLAC）。

**解决方案**:
```python
# 在搜索时优先使用 MP3 格式
# 修改 _get_play_url_with_fallback 的质量排序逻辑
```

或者在音乐API配置中设置默认使用 MP3：
```python
# 优先尝试 320k MP3，而不是 FLAC
qualities = [
    {"type": "320k", "format": "mp3"},
    {"type": "128k", "format": "mp3"},
    {"type": "flac", "format": "flac"},
]
```

#### 5. 需要设置循环模式

某些情况下需要先设置循环模式。

**解决方案**:
```python
# 在播放前设置循环模式
await client.player_set_loop(device_id, loop_type=1)  # 列表循环
await client.play_url(url, device_id, _type=1)
```

#### 6. 使用 player_play_url 而非 player_play_music

对于某些硬件，`player_play_url` 可能更可靠。

**测试方法**:
```python
# 直接使用 player_play_url
result = await self._na_service.ubus_request(
    did,
    "player_play_url",
    "mediaplayer",
    {"url": url, "type": _type, "media": "app_ios"},
)
```

## 调试步骤

### 1. 检查设备状态

```python
async with XiaoAiClient() as client:
    status = await client.player_get_status(device_id)
    print(f"播放状态: {status}")
```

### 2. 测试简单的 TTS

```python
async with XiaoAiClient() as client:
    await client.text_to_speech("测试", device_id)
```

如果 TTS 能播报，说明设备连接正常。

### 3. 测试暂停/恢复

```python
async with XiaoAiClient() as client:
    # 先让音箱播放一首歌（通过语音命令）
    await client.send_command("播放音乐", device_id)
    
    # 等待几秒
    await asyncio.sleep(3)
    
    # 测试暂停
    await client.player_pause(device_id)
    
    # 测试恢复
    await client.player_play(device_id)
```

### 4. 查看完整日志

启动服务时启用 DEBUG 日志：

```bash
# 在 .env 中添加
LOG_LEVEL=DEBUG

# 或者在启动时设置
export LOG_LEVEL=DEBUG
python -m uvicorn xiaoai_media.api.main:app --reload
```

### 5. 测试不同的 URL

```python
# 测试一个已知可用的 URL
test_urls = [
    "http://music.163.com/song/media/outer/url?id=447925558.mp3",  # 网易云
    "http://你的本地服务器/test.mp3",  # 本地文件
]

for url in test_urls:
    result = await client.play_url(url, device_id)
    print(f"URL: {url[:50]}... Result: {result}")
```

## 推荐的播放流程

```python
async def play_song_reliably(client, device_id, url):
    """可靠的播放流程"""
    
    # 1. 停止当前播放
    try:
        await client.player_stop(device_id)
        await asyncio.sleep(0.5)  # 等待停止完成
    except:
        pass
    
    # 2. 设置循环模式（可选）
    try:
        await client.player_set_loop(device_id, loop_type=1)
    except:
        pass
    
    # 3. 播放新 URL
    result = await client.play_url(url, device_id, _type=1)
    
    # 4. 等待一下，然后检查状态
    await asyncio.sleep(1)
    status = await client.player_get_status(device_id)
    
    return result, status
```

## 常见错误码

| Code | 含义 | 解决方案 |
|------|------|----------|
| 0 | 成功 | 正常 |
| -1 | 通用错误 | 检查设备连接 |
| 401 | 认证失败 | 检查 MI_USER 和 MI_PASS，删除 .mi.token 重新登录 |
| 404 | 设备不存在 | 检查 device_id |

## 进一步帮助

如果以上方法都无法解决问题：

1. 查看 miservice_fork 的 issues: https://github.com/yihong0618/MiService/issues
2. 检查音箱固件版本是否最新
3. 尝试重启音箱
4. 查看音箱的小米音箱 App 中是否有错误提示

## 成功案例

如果播放成功，日志应该类似：

```
INFO: play_by_music_url result: {'code': 0, 'data': {'code': 0}}
INFO: Playing device xxx: index=0/50 song=歌曲名
```

并且音箱开始播放音乐。
