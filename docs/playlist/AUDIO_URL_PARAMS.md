# 音频 URL 获取参数说明

## 参数传递机制

当播单项（PlaylistItem）没有预设的 `url` 字段时，系统会调用 `user_config.py` 中的 `get_audio_url` 函数动态获取播放 URL。

### 参数构建过程

1. **PlaylistItem 基础字段**：
   ```python
   {
       "title": "歌曲名",
       "artist": "歌手",
       "album": "专辑",
       "audio_id": "音频ID",
       "interval": 240,
       "pic_url": "https://..."
   }
   ```

2. **custom_params 覆盖**：
   ```python
   {
       "type": "music",
       "id": "001ABC",
       "platform": "tx",
       "name": "歌曲名",
       "singer": "歌手",
       "qualities": [...],
       "meta": {...}
   }
   ```

3. **最终合并结果**（传递给 `get_audio_url`）：
   ```python
   {
       # 基础字段（会被 custom_params 覆盖）
       "title": "歌曲名",
       "artist": "歌手",
       "album": "专辑",
       "audio_id": "音频ID",
       "interval": 240,
       "pic_url": "https://...",
       
       # custom_params 字段（优先级更高）
       "type": "music",
       "id": "001ABC",           # 覆盖 audio_id
       "platform": "tx",
       "name": "歌曲名",          # 覆盖 title
       "singer": "歌手",          # 覆盖 artist
       "qualities": [...],
       "meta": {...}
   }
   ```

## 音乐类型参数

对于音乐类型（`type: "music"`），`get_music_url` 函数期望以下参数：

### 必需参数
- `id` 或 `song_id`: 歌曲ID
- `platform`: 平台代码（tx, wy, kg, kw, mg）

### 可选参数
- `name`: 歌曲名称
- `singer`: 歌手名称
- `interval`: 播放间隔（秒）
- `qualities`: 音质列表
  ```python
  [
      {"type": "flac", "format": "flac", "size": "27.3M"},
      {"type": "320k", "format": "mp3", "size": "9.15M"},
      {"type": "128k", "format": "mp3", "size": "3.2M"}
  ]
  ```
- `meta`: 元数据
  ```python
  {
      "albumName": "专辑名",
      "picUrl": "封面URL",
      "songId": 123456
  }
  ```

## 示例

### 示例 1: 从音乐搜索结果创建播单项

音乐搜索返回的 song 对象：
```python
{
    "id": "001ABC",
    "name": "七里香",
    "singer": "周杰伦",
    "platform": "tx",
    "interval": 293,
    "qualities": [
        {"type": "flac", "format": "flac", "size": "27.3M"},
        {"type": "320k", "format": "mp3", "size": "9.15M"}
    ],
    "meta": {
        "albumName": "七里香",
        "picUrl": "https://...",
        "songId": 123456
    }
}
```

转换为 PlaylistItem：
```python
PlaylistItem(
    title="七里香",
    artist="周杰伦",
    album="七里香",
    audio_id="001ABC",
    url=None,  # 不预设 URL，动态获取
    custom_params={
        "type": "music",
        "id": "001ABC",
        "platform": "tx",
        "name": "七里香",
        "singer": "周杰伦",
        "interval": 293,
        "qualities": [...],
        "meta": {...}
    },
    interval=293,
    pic_url="https://..."
)
```

传递给 `get_audio_url` 的参数：
```python
{
    "title": "七里香",
    "artist": "周杰伦",
    "album": "七里香",
    "audio_id": "001ABC",
    "interval": 293,
    "pic_url": "https://...",
    # custom_params 覆盖
    "type": "music",
    "id": "001ABC",        # 覆盖 audio_id
    "platform": "tx",
    "name": "七里香",       # 覆盖 title
    "singer": "周杰伦",     # 覆盖 artist
    "qualities": [...],
    "meta": {...}
}
```

### 示例 2: 手动创建播单项（仅基础信息）

```python
PlaylistItem(
    title="我的歌曲",
    artist="某歌手",
    album="某专辑",
    audio_id="",
    url=None,
    custom_params={
        "type": "music",
        "platform": "tx",
        "id": "002XYZ"
    },
    interval=None,
    pic_url=None
)
```

传递给 `get_audio_url` 的参数：
```python
{
    "title": "我的歌曲",
    "artist": "某歌手",
    "album": "某专辑",
    "audio_id": "",
    "interval": None,
    "pic_url": None,
    # custom_params 覆盖
    "type": "music",
    "platform": "tx",
    "id": "002XYZ"
}
```

## 音质降级逻辑

`get_music_url` 会按照音质从高到低尝试获取 URL：

1. 按文件大小排序 qualities（大文件 = 高音质）
2. 依次尝试每个音质
3. 返回第一个成功获取的 URL
4. 如果所有音质都失败，抛出异常

## 自定义音频类型

如果要支持其他音频类型（如有声书、播客），需要在 `user_config.py` 的 `get_audio_url` 中添加相应的处理逻辑：

```python
async def get_audio_url(params: dict) -> str:
    audio_type = params.get("type", "")
    
    if audio_type == "music":
        return await get_music_url(params, MUSIC_API_BASE_URL)
    
    elif audio_type == "audiobook":
        # 有声书逻辑
        book_id = params.get("book_id")
        chapter = params.get("chapter")
        # 调用有声书 API...
        return audiobook_url
    
    elif audio_type == "podcast":
        # 播客逻辑
        podcast_id = params.get("podcast_id")
        episode = params.get("episode")
        # 调用播客 API...
        return podcast_url
    
    else:
        raise ValueError(f"Unsupported audio type: {audio_type}")
```

## 注意事项

1. **字段覆盖优先级**：`custom_params` 中的字段会覆盖 PlaylistItem 的基础字段
2. **返回值**：`get_audio_url` 应返回原始 URL，系统会自动包装为代理 URL
3. **异步支持**：`get_audio_url` 可以是同步或异步函数
4. **错误处理**：如果获取失败，应抛出异常并提供清晰的错误信息
5. **日志记录**：建议在 `get_audio_url` 中添加日志，便于调试

## 调试技巧

如果遇到参数问题，可以在 `user_config.py` 中添加调试日志：

```python
async def get_audio_url(params: dict) -> str:
    print(f"[DEBUG] get_audio_url called with params: {params}")
    
    audio_type = params.get("type", "")
    print(f"[DEBUG] audio_type: {audio_type}")
    
    if audio_type == "music":
        song_id = params.get("id") or params.get("song_id")
        platform = params.get("platform")
        print(f"[DEBUG] song_id: {song_id}, platform: {platform}")
        
        return await get_music_url(params, MUSIC_API_BASE_URL)
    
    # ...
```

或者查看系统日志（设置 `LOG_LEVEL = "DEBUG"`）：
```
DEBUG:xiaoai_media.services.playlist_service:Calling get_audio_url with params: {'title': '七里香', 'type': 'music', 'id': '001ABC', 'platform': 'tx', ...}
```
