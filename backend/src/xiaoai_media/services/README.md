# 服务层 (Services Layer)

## 概述

服务层包含了从API路由层分离出来的业务逻辑，提供可复用的服务组件。

## 设计原则

- **单一职责**: 每个服务类只负责一个业务领域
- **无状态**: 所有方法都是静态方法，不依赖实例状态
- **可测试**: 可以独立于HTTP框架进行单元测试
- **可复用**: 可以被多个路由或其他模块使用

## 模块说明

### music_service.py - 音乐服务

处理音乐搜索、排行榜、平台验证等业务逻辑。

**主要功能**:
- 音乐搜索
- 获取排行榜列表
- 获取排行榜歌曲
- 平台验证
- 排行榜命令解析
- 排行榜查找

**使用示例**:
```python
from xiaoai_media.services import MusicService

# 搜索音乐
results = await MusicService.search_music("周杰伦", "tx")

# 获取排行榜
ranks = await MusicService.get_ranks("wy")
```

### config_service.py - 配置服务

处理配置文件的读取、写入和验证。

**主要功能**:
- 读取配置文件
- 写入配置文件
- 获取当前配置
- 验证配置键
- 过滤敏感字段
- 重新加载配置模块

**使用示例**:
```python
from xiaoai_media.services import ConfigService

# 获取配置
config = ConfigService.get_current_config()

# 更新配置
ConfigService.write_user_config({
    "MUSIC_DEFAULT_PLATFORM": "wy"
})

# 重新加载
ConfigService.reload_config_module()
```

### playlist_service.py - 播放列表服务

处理播放列表的CRUD操作和播放控制。

**主要功能**:
- 创建、读取、更新、删除播放列表
- 添加/删除播放列表项
- 播放播放列表
- 语音命令播放
- URL代理和获取

**使用示例**:
```python
from xiaoai_media.services import PlaylistService

# 创建播放列表
playlist = PlaylistService.create_playlist(
    CreatePlaylistRequest(
        name="我的音乐",
        type="music",
        voice_keywords=["音乐", "歌曲"]
    )
)

# 播放播放列表
result = await PlaylistService.play_playlist(
    playlist_id="音乐_1234567890",
    req=PlayPlaylistRequest(device_id="xxx", start_index=0)
)
```

### playlist_storage.py - 播放列表存储

处理播放列表的文件存储和索引管理。

**主要功能**:
- 加载/保存播放列表索引
- 加载/保存播放列表数据
- 删除播放列表文件
- 存储目录管理

**使用示例**:
```python
from xiaoai_media.services import PlaylistStorage

# 加载索引
index = PlaylistStorage.load_index()

# 加载完整播放列表
playlist = PlaylistStorage.load_playlist("音乐_1234567890")

# 保存播放列表
PlaylistStorage.save_playlist(playlist)
```

### playlist_loader.py - 播放列表加载服务

处理从不同来源加载播放列表的业务逻辑。

**主要功能**:
- 从搜索结果加载播放列表
- 从排行榜加载播放列表
- 从保存的播放列表加载
- 解析歌曲数据

**使用示例**:
```python
from xiaoai_media.services import PlaylistLoaderService

# 从搜索加载
result = await PlaylistLoaderService.load_from_search(
    query="周杰伦",
    device_id="xxx",
    auto_play=True
)

# 从排行榜加载
result = await PlaylistLoaderService.load_from_chart(
    chart_keyword="热歌榜",
    device_id="xxx",
    auto_play=True
)

# 从保存的播放列表加载
result = await PlaylistLoaderService.load_from_saved_playlist(
    playlist_id="音乐_1234567890",
    device_id="xxx",
    auto_play=True
)
```

### voice_command_service.py - 语音命令服务

处理自然语言语音命令的解析和执行。

**主要功能**:
- 解析语音命令
- 执行命令（播放排行榜、播放列表、搜索等）
- TTS播报

**支持的命令**:
- "播放/打开 [平台] [排行榜名称]"
- "播放 [播单名称]"
- "搜索 [关键词]"
- 其他原始命令

**使用示例**:
```python
from xiaoai_media.services import VoiceCommandService

# 执行语音命令
result = await VoiceCommandService.execute_command(
    text="播放网易云热歌榜",
    device_id="xxx"
)

# 播报搜索结果
result = await VoiceCommandService.announce_search_results(
    query="周杰伦",
    count=50,
    device_id="xxx"
)
```

### playlist_models.py - 播放列表数据模型

定义播放列表相关的数据结构。

**主要模型**:
- `Playlist`: 完整播放列表
- `PlaylistIndex`: 播放列表索引信息
- `PlaylistItem`: 播放列表项
- `CreatePlaylistRequest`: 创建请求
- `UpdatePlaylistRequest`: 更新请求
- `AddItemRequest`: 添加项请求
- `PlayPlaylistRequest`: 播放请求

## 数据模型

### 音乐相关模型

#### SongItem - 歌曲项
```python
from xiaoai_media.services import SongItem

song = SongItem(
    id="123",
    name="歌曲名",
    singer="歌手名",
    platform="tx",
    qualities=[...],
    interval=240,
    meta={...}
)
```

#### SongQuality - 音质信息
```python
from xiaoai_media.services import SongQuality

quality = SongQuality(
    type="320k",
    format="mp3",
    size="9.15M"
)
```

#### SongMeta - 歌曲元数据
```python
from xiaoai_media.services import SongMeta

meta = SongMeta(
    albumName="专辑名",
    picUrl="https://...",
    songId="123"
)
```

### 播放列表相关模型

#### Playlist - 完整播放列表
```python
from xiaoai_media.services import Playlist

playlist = Playlist(
    id="音乐_1234567890",
    name="我的音乐",
    type="music",
    description="我喜欢的歌曲",
    items=[...],
    voice_keywords=["音乐", "歌曲"],
    created_at="2024-01-01T00:00:00",
    updated_at="2024-01-01T00:00:00"
)
```

#### PlaylistIndex - 播放列表索引
```python
from xiaoai_media.services import PlaylistIndex

index = PlaylistIndex(
    id="音乐_1234567890",
    name="我的音乐",
    type="music",
    description="我喜欢的歌曲",
    voice_keywords=["音乐", "歌曲"],
    item_count=50,
    created_at="2024-01-01T00:00:00",
    updated_at="2024-01-01T00:00:00"
)
```

#### PlaylistItem - 播放列表项
```python
from xiaoai_media.services import PlaylistItem

item = PlaylistItem(
    title="歌曲名",
    artist="歌手名",
    album="专辑名",
    audio_id="123",
    url="https://...",
    custom_params={"key": "value"}
)
```

#### CreatePlaylistRequest - 创建播放列表请求
```python
from xiaoai_media.services import CreatePlaylistRequest

req = CreatePlaylistRequest(
    name="我的音乐",
    type="music",
    description="我喜欢的歌曲",
    voice_keywords=["音乐", "歌曲"]
)
```

#### UpdatePlaylistRequest - 更新播放列表请求
```python
from xiaoai_media.services import UpdatePlaylistRequest

req = UpdatePlaylistRequest(
    name="新名称",
    description="新描述",
    voice_keywords=["新关键词"]
)
```

#### AddItemRequest - 添加项请求
```python
from xiaoai_media.services import AddItemRequest, PlaylistItem

req = AddItemRequest(
    items=[
        PlaylistItem(title="歌曲1", artist="歌手1"),
        PlaylistItem(title="歌曲2", artist="歌手2"),
    ]
)
```

#### PlayPlaylistRequest - 播放请求
```python
from xiaoai_media.services import PlayPlaylistRequest

req = PlayPlaylistRequest(
    device_id="xxx",
    start_index=0,
    announce=True
)
```

## 导入方式

```python
# 导入所有服务
from xiaoai_media.services import (
    # 音乐服务
    MusicService,
    # 配置服务
    ConfigService,
    # 播放列表服务
    PlaylistService,
    PlaylistStorage,
    PlaylistLoaderService,
    # 语音命令服务
    VoiceCommandService,
    # 音乐数据模型
    SongItem,
    SongQuality,
    SongMeta,
    # 播放列表数据模型
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    CreatePlaylistRequest,
    UpdatePlaylistRequest,
    AddItemRequest,
    PlayPlaylistRequest,
)

# 或单独导入
from xiaoai_media.services.music_service import MusicService
from xiaoai_media.services.playlist_service import PlaylistService
```

## 错误处理

所有服务方法都可能抛出 `HTTPException`：

```python
from fastapi import HTTPException

try:
    results = await MusicService.search_music("", "tx")
except HTTPException as e:
    # 处理业务错误
    print(f"错误: {e.detail}")
except Exception as e:
    # 处理其他错误
    print(f"未知错误: {e}")
```

## 测试

服务层可以独立测试，不需要启动HTTP服务器：

```python
import pytest
from xiaoai_media.services import MusicService

@pytest.mark.asyncio
async def test_search_music():
    results = await MusicService.search_music("test", "tx")
    assert results is not None
    assert "data" in results
```

## 相关文档

- [完整重构文档](../../../../docs/refactor/API_SERVICES_REFACTOR.md)
- [快速参考](../../../../docs/refactor/SERVICES_QUICK_REFERENCE.md)
- [API文档](../../../../docs/api/API_REFERENCE.md)

## 架构图

```
┌─────────────────────────────────────────┐
│           API路由层 (Routes)             │
│  - 处理HTTP请求/响应                      │
│  - 参数验证                              │
│  - 错误处理                              │
└──────────────┬──────────────────────────┘
               │ 调用
               ↓
┌─────────────────────────────────────────┐
│          服务层 (Services)               │
│  - 业务逻辑                              │
│  - 数据处理                              │
│  - 外部API调用                           │
│  - 数据转换                              │
└──────────────┬──────────────────────────┘
               │ 使用
               ↓
┌─────────────────────────────────────────┐
│        数据层 (Player, Client)           │
│  - 数据持久化                            │
│  - 外部服务交互                          │
└─────────────────────────────────────────┘
```

## 优势

1. **代码复用**: 服务层可以被多个路由使用
2. **易于测试**: 可以独立测试业务逻辑
3. **职责清晰**: 路由层和业务逻辑分离
4. **易于维护**: 修改业务逻辑不影响路由层
5. **易于扩展**: 新功能可以先在服务层实现

## 最佳实践

1. **保持服务无状态**: 使用静态方法，不依赖实例状态
2. **单一职责**: 每个服务类只负责一个业务领域
3. **错误处理**: 统一使用HTTPException
4. **日志记录**: 在关键操作处添加日志
5. **文档注释**: 为每个方法添加清晰的文档字符串
