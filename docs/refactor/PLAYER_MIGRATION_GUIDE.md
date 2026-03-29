# 播放器重构 - 迁移指南

如果你的代码直接使用了 `music.py` 中的内部函数或全局变量，需要进行以下迁移。

## ⚠️ 注意

如果你只是通过 API 端点使用播放器功能，**无需任何修改**，所有 API 接口保持不变。

---

## 迁移内容

### 1. 导入播放器模块

**之前**:
```python
from xiaoai_media.api.routes.music import _playlists
```

**现在**:
```python
from xiaoai_media.player import get_player

player = get_player()
```

---

### 2. 播放列表访问

**之前**:
```python
from xiaoai_media.api.routes.music import _playlists

# 获取播放列表
pl = _playlists.get(device_id)

# 设置播放列表
_playlists[device_id] = {
    "songs": [...],
    "current": 0,
    "device_id": device_id,
}
```

**现在**:
```python
from xiaoai_media.player import get_player

player = get_player()

# 获取播放列表
pl = player.get_playlist(device_id)

# 设置播放列表
player.set_playlist(
    device_id=device_id,
    songs=[...],
    current_index=0,
)
```

---

### 3. URL 代理转换

**之前**:
```python
from xiaoai_media.api.routes.music import _make_proxy_url

proxy_url = _make_proxy_url(original_url)
```

**现在**:
```python
from xiaoai_media.player import get_player

player = get_player()
proxy_url = player._make_proxy_url(original_url)
```

> **注意**: 这是私有方法，建议通过播放器的公共方法来使用。

---

### 4. 获取播放 URL

**之前**:
```python
from xiaoai_media.api.routes.music import _get_play_url_with_fallback

play_info = await _get_play_url_with_fallback(song)
```

**现在**:
```python
from xiaoai_media.player import get_player

player = get_player()
play_info = await player._get_play_url_with_fallback(song)
```

> **注意**: 这是私有方法，建议使用 `player.play_at_index()` 等公共方法。

---

### 5. 播放控制

**之前**:
```python
from xiaoai_media.api.routes.music import _play_song_at_index

result = await _play_song_at_index(
    device_id, index, stop_first=True
)
```

**现在**:
```python
from xiaoai_media.player import get_player

player = get_player()
result = await player.play_at_index(
    device_id, index, stop_first=True
)
```

---

## 完整示例

### 自定义播放逻辑

**之前的代码**:
```python
from xiaoai_media.api.routes.music import (
    _playlists,
    _get_play_url_with_fallback,
    _make_proxy_url,
)
from xiaoai_media.client import XiaoAiClient

async def my_custom_play(device_id: str, songs: list):
    # 设置播放列表
    _playlists[device_id] = {
        "songs": songs,
        "current": 0,
        "device_id": device_id,
    }
    
    # 获取第一首歌的 URL
    first_song = songs[0]
    play_info = await _get_play_url_with_fallback(first_song)
    
    if play_info:
        url = _make_proxy_url(play_info["url"])
        
        # 播放
        async with XiaoAiClient() as client:
            await client.play_url(url, device_id, _type=1)
```

**迁移后的代码**:
```python
from xiaoai_media.player import get_player

async def my_custom_play(device_id: str, songs: list):
    player = get_player()
    
    # 设置播放列表
    player.set_playlist(device_id, songs, current_index=0)
    
    # 播放第一首（内部会自动处理 URL 获取和代理转换）
    await player.play_at_index(device_id, 0, stop_first=True)
```

---

## 推荐做法

### ✅ 使用公共 API

优先使用播放器的公共方法：
```python
player = get_player()

# 播放控制
await player.play_at_index(device_id, index)
await player.play_next(device_id)
await player.play_prev(device_id)
await player.pause(device_id)
await player.resume(device_id)
await player.stop(device_id)

# 状态获取
playlist = player.get_playlist(device_id)
status = await player.get_status(device_id)
```

### ❌ 避免直接访问内部实现

不推荐直接使用私有方法（以 `_` 开头的方法），因为它们的签名可能会在未来版本中改变。

---

## 测试你的代码

重构后，确保运行你的测试套件：

```bash
# 运行所有测试
pytest

# 或运行特定测试
python test/music/test_playlist_player.py
```

---

## 需要帮助？

如果你遇到迁移问题：

1. 查看 [PLAYER_REFACTOR_SUMMARY.md](PLAYER_REFACTOR_SUMMARY.md) 了解详细的重构信息
2. 查看 `player.py` 的源代码和文档字符串
3. 参考 `music.py` 中现有的端点实现

---

**重构版本**: 2026-03-20  
**向后兼容**: API 端点完全兼容，内部实现需要迁移
