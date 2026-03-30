# 播放器能力抽离重构总结

## 重构目标

将播放器相关的能力从 `music.py` 抽离为独立的 `player.py` 模块，提高代码的可维护性、可测试性和可复用性。

---

## 变更总览

### 1. **新增文件**

#### `backend/src/xiaoai_media/player.py`
全新的播放器模块，封装了所有播放列表管理和播放控制逻辑：

**核心类: `PlaylistPlayer`**
- 播放列表管理（按设备ID索引存储）
- 播放控制方法
- URL获取和代理逻辑
- 音质降级重试机制

**主要方法**:
```python
class PlaylistPlayer:
    # 播放列表管理
    def get_playlist(device_id) -> dict | None
    def set_playlist(device_id, songs, current_index=0, **metadata) -> dict
    def clear_playlist(device_id) -> None
    
    # 播放控制
    async def play_at_index(device_id, index, stop_first=False) -> dict
    async def play_next(device_id) -> dict
    async def play_prev(device_id) -> dict
    async def pause(device_id) -> dict
    async def resume(device_id) -> dict
    async def stop(device_id) -> dict
    async def get_status(device_id) -> dict
    
    # 内部辅助方法
    def _make_proxy_url(original_url) -> str
    async def _get_play_url_with_fallback(song) -> dict | None
    async def _proxy_music_api(method, path, **kwargs) -> dict
    @staticmethod
    def _parse_size(size) -> int
```

**全局实例**:
```python
def get_player() -> PlaylistPlayer
```

---

### 2. **修改的文件**

#### `backend/src/xiaoai_media/api/routes/music.py`

**移除的内容**:
- ❌ `_playlists` 全局变量
- ❌ `_make_proxy_url()` 函数
- ❌ `_parse_size()` 函数
- ❌ `_get_play_url_with_fallback()` 函数  
- ❌ `_play_song_at_index()` 函数

**新增的内容**:
- ✅ 导入 `from xiaoai_media.player import get_player`

**更新的端点**:
所有使用旧逻辑的端点都已更新为使用播放器实例：

| 端点 | 更新内容 |
|-----|---------|
| `POST /playlist` | 使用 `player.set_playlist()` |
| `GET /playlist` | 使用 `player.get_playlist()` |
| `POST /play` | 使用 `player.play_at_index()` |
| `POST /next` | 使用 `player.play_next()` |
| `POST /prev` | 使用 `player.play_prev()` |
| `POST /pause` | 使用 `player.pause()` |
| `POST /resume` | 使用 `player.resume()` |
| `POST /stop` | 使用 `player.stop()` |
| `GET /status` | 使用 `player.get_status()` |
| `POST /load-from-search` | 使用 `player.set_playlist()` 和 `player.play_at_index()` |
| `POST /load-from-chart` | 使用 `player.set_playlist()` 和 `player.play_at_index()` |
| `POST /load-from-playlist` | 使用 `player.set_playlist()` 和 `player.play_at_index()` |

#### `backend/src/xiaoai_media/command_handler.py`

**移除的内容**:
所有不再使用的旧方法（因为已经重构为统一调用 `/api/music/voice-command`）：
- ❌ `_parse_playlist_command()`
- ❌ `_handle_playlist_command()`
- ❌ `_parse_play_command()`
- ❌ `_handle_play_command()`
- ❌ `_search_music()`
- ❌ `_sync_playlist()`
- ❌ `_play_song()`

**保留的内容**:
- ✅ `handle_command()` - 统一调用 voice-command 端点

---

## 架构改进

### 之前的架构
```
music.py
  ├── 全局变量 _playlists
  ├── 辅助函数 (_make_proxy_url, _parse_size, etc.)
  ├── 播放逻辑 (_play_song_at_index)
  └── API 端点 (play, next, prev, etc.)

command_handler.py
  ├── 重复的播放逻辑
  ├── 重复的播放列表操作
  └── 直接导入 music.py 的内部函数
```

### 现在的架构
```
player.py (新模块)
  └── PlaylistPlayer 类
      ├── 播放列表存储和管理
      ├── 播放控制逻辑
      └── URL 处理和代理

music.py
  ├── 导入 player 模块
  ├── API 端点（使用播放器）
  └── 其他音乐相关功能（搜索、排行榜等）

command_handler.py
  └── 统一调用 voice-command 端点
```

---

## 优势

### 1. **单一职责原则**
- `player.py`: 专注于播放列表管理和播放控制
- `music.py`: 专注于API端点和业务逻辑
- `command_handler.py`: 专注于语音命令处理

### 2. **代码复用**
- 播放器逻辑集中在一处，避免重复
- 所有需要使用播放器的地方都调用同一个实例

### 3. **更好的测试性**
- 播放器逻辑可以独立测试
- Mock更容易实现
- 单元测试更简洁

### 4. **易于维护**
- 播放器逻辑修改只需要更新 `player.py`
- 清晰的接口定义
- 更少的循环依赖

### 5. **可扩展性**
- 可以轻松添加新的播放器功能
- 可以实现多种播放器策略
- 支持更复杂的播放列表操作

---

## 向后兼容性

✅ **完全向后兼容** - 所有API端点的签名和行为保持不变：
- 相同的请求参数
- 相同的响应格式
- 相同的错误处理

从外部调用者的角度来看，没有任何变化。

---

## 使用示例

### 在代码中使用播放器

```python
from xiaoai_media.player import get_player

# 获取播放器实例
player = get_player()

# 设置播放列表
player.set_playlist(
    device_id="xxx",
    songs=[...],
    current_index=0,
    source="search",  # 额外元数据
)

# 播放歌曲
result = await player.play_at_index("xxx", 0, stop_first=True)

# 播放控制
await player.play_next("xxx")
await player.pause("xxx")
await player.resume("xxx")
await player.stop("xxx")

# 获取状态
status = await player.get_status("xxx")
playlist = player.get_playlist("xxx")
```

---

## 测试

运行现有的测试套件验证功能：

```bash
source .venv/bin/activate
python test/music/test_playlist_player.py
```

所有现有测试应该继续通过，因为API接口没有改变。

---

## 后续工作建议

1. **添加单元测试**: 为 `player.py` 添加专门的单元测试
2. **添加播放器状态**: 可以在播放器中维护更多状态（如播放模式、重复模式等）
3. **支持多种播放器**: 可以创建不同的播放器实现（如本地播放器、流媒体播放器等）
4. **播放历史记录**: 在播放器中添加历史记录功能
5. **播放队列管理**: 支持更复杂的队列操作（插入、删除、重排序等）

---

**重构完成时间**: 2026-03-20  
**影响范围**: 后端播放器架构  
**破坏性变更**: 无
