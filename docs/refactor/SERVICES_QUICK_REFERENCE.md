# 服务层快速参考

## 导入

```python
from xiaoai_media.services import (
    MusicService,
    ConfigService,
    PlaylistLoaderService,
    VoiceCommandService,
    SongItem,
    SongQuality,
    SongMeta,
)
```

## MusicService - 音乐服务

### 搜索音乐
```python
results = await MusicService.search_music(
    query="周杰伦",
    platform="tx",  # tx|kw|kg|wy|mg
    page=1,
    limit=20
)
```

### 获取排行榜列表
```python
ranks = await MusicService.get_ranks(platform="wy")
```

### 获取排行榜歌曲
```python
songs = await MusicService.get_rank_songs(
    rank_id="123",
    platform="tx",
    page=1,
    limit=50
)
```

### 验证平台
```python
platform = MusicService.validate_platform("tx")  # 返回 "tx"
platform = MusicService.validate_platform(None)  # 返回默认平台
```

### 解析排行榜命令
```python
platform, keyword = MusicService.parse_chart_command("播放腾讯热歌榜")
# 返回: ("tx", "热歌榜")
```

### 查找排行榜
```python
chart = MusicService.find_chart(chart_list, "热歌")
# 返回匹配的排行榜字典
```

## ConfigService - 配置服务

### 获取当前配置
```python
config = ConfigService.get_current_config()
# 返回: {"MI_USER": "...", "MI_PASS": "***", ...}
```

### 读取配置文件
```python
config_dict = ConfigService.read_user_config()
# 返回: {"MI_USER": "user@example.com", ...}
```

### 写入配置文件
```python
ConfigService.write_user_config({
    "MUSIC_DEFAULT_PLATFORM": "wy",
    "LOG_LEVEL": "DEBUG",
    "WAKE_WORDS": ["小爱", "小艾"]
})
```

### 验证配置键
```python
ConfigService.validate_config_keys({"MI_USER": "test"})  # 通过
ConfigService.validate_config_keys({"INVALID_KEY": "test"})  # 抛出异常
```

### 过滤敏感字段
```python
filtered = ConfigService.filter_sensitive_fields({
    "MI_PASS": "***",  # 会被过滤掉
    "MI_USER": "user@example.com"  # 保留
})
```

### 重新加载配置
```python
ConfigService.reload_config_module()
```

## PlaylistLoaderService - 播放列表加载服务

### 从搜索加载
```python
result = await PlaylistLoaderService.load_from_search(
    query="周杰伦",
    device_id="xxx",
    platform="tx",
    auto_play=True
)
# 返回: {
#     "action": "load_from_search",
#     "query": "周杰伦",
#     "platform": "tx",
#     "total": 50,
#     "songs": [...],
#     "play_result": {...}  # 如果auto_play=True
# }
```

### 从排行榜加载
```python
result = await PlaylistLoaderService.load_from_chart(
    chart_keyword="热歌榜",
    device_id="xxx",
    platform="wy",
    auto_play=True
)
# 或使用chart_id
result = await PlaylistLoaderService.load_from_chart(
    chart_id="123",
    device_id="xxx",
    platform="wy",
    auto_play=False
)
```

### 从保存的播放列表加载
```python
result = await PlaylistLoaderService.load_from_saved_playlist(
    playlist_id="音乐_1234567890",
    device_id="xxx",
    auto_play=True
)
```

### 解析歌曲列表
```python
songs = PlaylistLoaderService.parse_songs_from_api_response(
    songs_raw=[{"id": "1", "name": "歌曲", "singer": "歌手", ...}],
    platform="tx"
)
# 返回: [SongItem(...), ...]
```

## VoiceCommandService - 语音命令服务

### 执行语音命令
```python
result = await VoiceCommandService.execute_command(
    text="播放网易云热歌榜",
    device_id="xxx"
)
# 自动识别命令类型并执行相应操作
```

### 支持的命令模式

#### 播放排行榜
```python
result = await VoiceCommandService.execute_command(
    text="播放腾讯热歌榜",
    device_id="xxx"
)
# 返回: {"action": "play_chart", "chart_name": "热歌榜", ...}
```

#### 播放播单
```python
result = await VoiceCommandService.execute_command(
    text="播放音乐播单",
    device_id="xxx"
)
# 返回: {"action": "play_playlist", "playlist_name": "音乐", ...}
```

#### 搜索并播放
```python
result = await VoiceCommandService.execute_command(
    text="搜索周杰伦",
    device_id="xxx"
)
# 返回: {"action": "search_and_play", "query": "周杰伦", ...}
```

#### 原始命令
```python
result = await VoiceCommandService.execute_command(
    text="今天天气怎么样",
    device_id="xxx"
)
# 返回: {"action": "command", "command": "今天天气怎么样", ...}
```

### 播报搜索结果
```python
result = await VoiceCommandService.announce_search_results(
    query="周杰伦",
    count=50,
    device_id="xxx"
)
# 发送TTS: "搜索到50首周杰伦的歌曲，是否播放？"
```

## 数据模型

### SongItem - 歌曲项
```python
song = SongItem(
    id="123",
    name="歌曲名",
    singer="歌手名",
    platform="tx",
    qualities=[
        SongQuality(type="320k", format="mp3", size="9.15M")
    ],
    interval=240,  # 时长（秒）
    meta=SongMeta(
        albumName="专辑名",
        picUrl="https://...",
        songId="123"
    )
)
```

### SongQuality - 音质信息
```python
quality = SongQuality(
    type="320k",  # 128k, 320k, flac等
    format="mp3",
    size="9.15M"  # 可以是字节数或字符串
)
```

### SongMeta - 歌曲元数据
```python
meta = SongMeta(
    albumName="专辑名",
    picUrl="https://封面图片URL",
    songId="123"
)
```

## 常见用法示例

### 完整的搜索和播放流程
```python
from xiaoai_media.services import MusicService, PlaylistLoaderService

# 1. 搜索音乐
search_results = await MusicService.search_music("周杰伦", "tx")

# 2. 加载到播放列表并播放
result = await PlaylistLoaderService.load_from_search(
    query="周杰伦",
    device_id="device_123",
    platform="tx",
    auto_play=True
)

print(f"已加载 {result['total']} 首歌曲")
```

### 更新配置并重新加载
```python
from xiaoai_media.services import ConfigService

# 1. 读取当前配置
current = ConfigService.get_current_config()

# 2. 更新配置
ConfigService.write_user_config({
    "MUSIC_DEFAULT_PLATFORM": "wy",
    "ENABLE_CONVERSATION_POLLING": True,
    "WAKE_WORDS": ["小爱", "小艾", "小爱同学"]
})

# 3. 重新加载
ConfigService.reload_config_module()
```

### 处理语音命令
```python
from xiaoai_media.services import VoiceCommandService

# 用户说: "播放网易云热歌榜"
result = await VoiceCommandService.execute_command(
    text="播放网易云热歌榜",
    device_id="device_123"
)

if result["action"] == "play_chart":
    print(f"正在播放: {result['chart_name']}")
elif result["action"] == "play_playlist":
    print(f"正在播放播单: {result['playlist_name']}")
```

## 错误处理

所有服务方法都可能抛出 `HTTPException`，需要在调用时处理：

```python
from fastapi import HTTPException

try:
    results = await MusicService.search_music("", "tx")
except HTTPException as e:
    print(f"错误: {e.detail}")
    # 在路由层可以直接 raise，FastAPI会自动处理
    raise
except Exception as e:
    print(f"未知错误: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

## 平台代码

支持的音乐平台：
- `tx`: 腾讯音乐/QQ音乐
- `wy`: 网易云音乐
- `kw`: 酷我音乐
- `kg`: 酷狗音乐
- `mg`: 咪咕音乐

## 相关文档

- [完整重构文档](./API_SERVICES_REFACTOR.md)
- [API参考](../api/API_REFERENCE.md)
