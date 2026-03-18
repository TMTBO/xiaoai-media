# URL播放功能实现总结

## 项目背景

实现小爱音箱直接播放从音乐API获取的URL，而不是通过语音命令让小爱自己搜索歌曲。

## 问题历程

### 第一次尝试：使用 player_play_url
- 使用 `ubus_request` 调用 `player_play_url`
- API返回成功，但音箱没有实际播放
- 原因：方法不适用于所有硬件型号

### 调查研究
- 研究了 xiaomusic 开源项目
- 发现使用了 `miservice-fork` 包
- 找到了正确的实现方式

### 最终解决方案
根据硬件型号使用不同的播放方法：
- OH2P 等型号：使用 `player_play_music`
- 其他型号：使用 `player_play_url`

## 技术实现

### 核心代码

```python
async def play_url(self, url: str, device_id: str | None = None, _type: int = 2):
    # 硬件型号列表
    USE_PLAY_MUSIC_API = [
        "LX04", "LX05", "L05B", "L05C", "L06", "L06A",
        "X08A", "X10A", "X08C", "X08E", "X8F", "X4B",
        "OH2", "OH2P", "X6A",
    ]
    
    if hardware in USE_PLAY_MUSIC_API:
        # 使用 player_play_music
        music = {
            "payload": {
                "audio_items": [{
                    "stream": {"url": url}
                }]
            }
        }
        await ubus_request(did, "player_play_music", "mediaplayer", ...)
    else:
        # 使用 player_play_url
        await ubus_request(did, "player_play_url", "mediaplayer",
                         {"url": url, "type": _type, "media": "app_ios"})
```

### API流程

1. **搜索歌曲**
   ```
   POST /api/v3/search
   {"platform": "tx", "query": "稻香", "page": 1, "limit": 1}
   ```

2. **获取播放URL**
   ```
   POST /api/v3/play
   {"songId": "003aAYrm3GE0Ac", "platform": "tx", "quality": "128k"}
   ```

3. **播放URL**
   ```python
   await client.play_url(url, device_id, _type=2)
   ```

## 测试结果

### 测试覆盖
- ✅ 基础播放功能
- ✅ 完整流程（搜索→获取URL→播放）
- ✅ API端点测试
- ✅ 播放列表控制（上一首/下一首）

### 测试设备
- 设备：Xiaomi 智能音箱 Pro
- 硬件：OH2P
- 方法：player_play_music

### 测试文件
- `test_play_url.py` - 基础播放
- `test_complete_flow.py` - 完整流程
- `test_api_play.py` - API端点
- `test_playlist_control.py` - 播放列表

## 关键发现

### 1. 硬件差异
不同的小爱音箱硬件型号需要使用不同的播放API。

### 2. 必需参数
- `media: "app_ios"` - 必须添加
- `_type`: 控制播放模式（1=MUSIC, 2=普通）

### 3. payload结构
对于 `player_play_music`，需要构建完整的音乐播放payload，包括：
- audio_items: 音频项列表
- stream.url: 播放URL
- list_params: 播放列表参数

## 参考资料

### 开源项目
- **xiaomusic**: https://github.com/hanxi/xiaomusic
  - 完整的小爱音箱音乐播放解决方案
  - 使用 miservice-fork 包
  
- **miservice-fork**: https://github.com/hanxi/MiService
  - 扩展的 MiService 库
  - 添加了播放音乐功能

### 关键文件
- device_player.py#L335: 播放实现
- minaservice.py: play_by_url 和 play_by_music_url 方法

## 后续优化

### 可能的改进
1. 添加音质选择（128k, 320k, flac）
2. 添加播放状态查询
3. 添加播放进度控制
4. 优化错误处理和重试机制
5. 支持更多音乐平台

### 已知限制
1. 需要音乐API服务运行
2. URL可能有时效性
3. 依赖网络连接质量

## 结论

成功实现了小爱音箱直接播放URL的功能，解决了原有通过语音命令播放的局限性。现在系统可以：
- 精确控制播放的歌曲版本
- 支持自定义音乐源
- 实现完整的播放列表管理

这为后续功能扩展（如自定义歌单、音质选择等）奠定了基础。
