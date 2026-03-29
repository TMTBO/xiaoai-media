# API服务层重构文档

## 概述

本次重构将API路由层的业务逻辑拆分到独立的服务层（services），实现了关注点分离，提高了代码的可维护性和可测试性。

## 重构目标

1. **关注点分离**: 路由层只处理HTTP请求/响应，业务逻辑移至服务层
2. **代码复用**: 服务层可以被多个路由或其他模块复用
3. **易于测试**: 服务层可以独立于HTTP框架进行单元测试
4. **清晰的架构**: 明确的分层结构，便于理解和维护

## 目录结构

```
backend/src/xiaoai_media/
├── api/
│   └── routes/
│       ├── music.py          # 音乐API路由（仅处理HTTP请求）
│       ├── config.py         # 配置API路由（仅处理HTTP请求）
│       └── playlist.py       # 播放列表API路由
└── services/                 # 新增：服务层
    ├── __init__.py
    ├── music_service.py      # 音乐服务（搜索、排行榜等）
    ├── config_service.py     # 配置服务（读写配置文件）
    ├── playlist_loader.py    # 播放列表加载服务
    └── voice_command_service.py  # 语音命令服务
```

## 服务层模块说明

### 1. MusicService (music_service.py)

**职责**: 处理音乐搜索、排行榜、平台验证等业务逻辑

**主要方法**:
- `proxy_request()`: 代理请求到音乐下载服务
- `validate_platform()`: 验证并返回有效的平台代码
- `parse_chart_command()`: 解析排行榜播放命令
- `find_chart()`: 根据关键词查找最匹配的排行榜
- `search_music()`: 搜索音乐
- `get_ranks()`: 获取平台的排行榜列表
- `get_rank_songs()`: 获取指定排行榜的歌曲列表

**使用示例**:
```python
from xiaoai_media.services import MusicService

# 搜索音乐
results = await MusicService.search_music("周杰伦", platform="tx", page=1, limit=20)

# 获取排行榜
ranks = await MusicService.get_ranks(platform="wy")

# 验证平台
platform = MusicService.validate_platform("tx")  # 返回 "tx"
```

### 2. ConfigService (config_service.py)

**职责**: 处理配置文件的读取、写入和验证

**主要方法**:
- `read_user_config()`: 读取user_config.py中的配置变量
- `write_user_config()`: 更新user_config.py中的配置变量
- `get_current_config()`: 获取当前配置（敏感字段会被掩码）
- `validate_config_keys()`: 验证配置项键是否允许修改
- `filter_sensitive_fields()`: 过滤敏感字段
- `reload_config_module()`: 重新加载配置模块

**使用示例**:
```python
from xiaoai_media.services import ConfigService

# 获取当前配置
config = ConfigService.get_current_config()

# 更新配置
ConfigService.write_user_config({
    "MUSIC_DEFAULT_PLATFORM": "wy",
    "LOG_LEVEL": "DEBUG"
})

# 重新加载配置
ConfigService.reload_config_module()
```

### 3. PlaylistLoaderService (playlist_loader.py)

**职责**: 处理从不同来源（搜索、排行榜、保存的播放列表）加载播放列表

**主要方法**:
- `parse_songs_from_api_response()`: 从API响应中解析歌曲列表
- `load_from_search()`: 从搜索结果加载播放列表
- `load_from_chart()`: 从排行榜加载播放列表
- `load_from_saved_playlist()`: 从保存的播放列表加载

**数据模型**:
- `SongItem`: 歌曲项
- `SongQuality`: 歌曲音质信息
- `SongMeta`: 歌曲元数据

**使用示例**:
```python
from xiaoai_media.services import PlaylistLoaderService

# 从搜索加载
result = await PlaylistLoaderService.load_from_search(
    query="周杰伦",
    device_id="xxx",
    platform="tx",
    auto_play=True
)

# 从排行榜加载
result = await PlaylistLoaderService.load_from_chart(
    chart_keyword="热歌榜",
    device_id="xxx",
    platform="wy",
    auto_play=True
)

# 从保存的播放列表加载
result = await PlaylistLoaderService.load_from_saved_playlist(
    playlist_id="音乐_1234567890",
    device_id="xxx",
    auto_play=True
)
```

### 4. VoiceCommandService (voice_command_service.py)

**职责**: 处理自然语言语音命令的解析和执行

**主要方法**:
- `execute_command()`: 解析并执行自然语言语音命令
- `announce_search_results()`: 向音箱发送TTS，播报搜索结果数量

**支持的命令模式**:
- "播放/打开 [平台] [排行榜名称]" → 加载排行榜并播放
- "播放 [播单名称]" → 加载保存的播放列表并播放
- "搜索 [关键词]" → 搜索并加载结果
- 其他文本 → 作为原始语音命令转发给音箱

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

## 路由层变化

### music.py 路由

**重构前**: 包含大量业务逻辑（平台验证、命令解析、播放列表加载等）

**重构后**: 只处理HTTP请求/响应，调用服务层方法

```python
# 重构前
async def search_music(query: str, platform: str | None = None, ...):
    if not query.strip():
        raise HTTPException(...)
    plat = platform or config.MUSIC_DEFAULT_PLATFORM
    if plat not in _PLATFORMS:
        raise HTTPException(...)
    # ... 更多业务逻辑
    return await _proxy("POST", "/api/v3/search", ...)

# 重构后
async def search_music(query: str, platform: str | None = None, ...):
    return await MusicService.search_music(query, platform, page, limit)
```

### config.py 路由

**重构前**: 包含配置文件读写、验证等业务逻辑

**重构后**: 只处理HTTP请求/响应，调用服务层方法

```python
# 重构前
async def update_config(body: ConfigUpdate):
    updates = body.model_dump(exclude_none=True)
    # ... 过滤、验证逻辑
    _write_user_config(updates)
    # ... 重新加载逻辑
    return {"message": "..."}

# 重构后
async def update_config(body: ConfigUpdate):
    updates = body.model_dump(exclude_none=True)
    updates = ConfigService.filter_sensitive_fields(updates)
    if not updates:
        raise HTTPException(...)
    ConfigService.validate_config_keys(updates)
    ConfigService.write_user_config(updates)
    ConfigService.reload_config_module()
    return {"message": "Configuration updated successfully"}
```

## 优势

### 1. 代码复用
服务层可以被多个路由或其他模块复用，避免代码重复。

```python
# 可以在不同的路由中使用相同的服务
from xiaoai_media.services import MusicService

# 在music路由中
results = await MusicService.search_music(query, platform)

# 在其他路由或模块中也可以使用
results = await MusicService.search_music(query, platform)
```

### 2. 易于测试
服务层可以独立于HTTP框架进行单元测试。

```python
# 测试服务层（不需要启动HTTP服务器）
import pytest
from xiaoai_media.services import MusicService

@pytest.mark.asyncio
async def test_search_music():
    results = await MusicService.search_music("test", "tx")
    assert results is not None
```

### 3. 清晰的职责划分
- **路由层**: 处理HTTP请求/响应、参数验证、错误处理
- **服务层**: 处理业务逻辑、数据处理、外部API调用
- **数据层**: 数据模型定义（Pydantic模型）

### 4. 易于维护和扩展
- 业务逻辑集中在服务层，修改时只需要关注服务层
- 添加新功能时，可以先在服务层实现，然后在路由层暴露接口
- 服务层可以独立演进，不影响路由层

## 迁移指南

### 如何使用新的服务层

1. **导入服务类**:
```python
from xiaoai_media.services import (
    MusicService,
    ConfigService,
    PlaylistLoaderService,
    VoiceCommandService,
)
```

2. **调用服务方法**:
```python
# 所有服务方法都是静态方法，直接通过类调用
results = await MusicService.search_music(query, platform)
config = ConfigService.get_current_config()
```

3. **处理异常**:
```python
try:
    results = await MusicService.search_music(query, platform)
except HTTPException as e:
    # 服务层会抛出HTTPException，路由层可以直接传递
    raise
except Exception as e:
    # 其他异常需要转换为HTTPException
    raise HTTPException(status_code=500, detail=str(e))
```

### 向后兼容性

- API接口保持不变，客户端无需修改
- 所有现有功能都已迁移到服务层
- 路由层的行为与重构前完全一致

## 测试建议

### 单元测试
为每个服务类编写单元测试：

```python
# tests/services/test_music_service.py
import pytest
from xiaoai_media.services import MusicService

class TestMusicService:
    def test_validate_platform_valid(self):
        assert MusicService.validate_platform("tx") == "tx"
    
    def test_validate_platform_invalid(self):
        with pytest.raises(HTTPException):
            MusicService.validate_platform("invalid")
    
    @pytest.mark.asyncio
    async def test_search_music(self):
        results = await MusicService.search_music("test", "tx")
        assert "data" in results
```

### 集成测试
测试路由层和服务层的集成：

```python
# tests/api/test_music_routes.py
from fastapi.testclient import TestClient

def test_search_music_endpoint(client: TestClient):
    response = client.get("/api/music/search?query=test&platform=tx")
    assert response.status_code == 200
    assert "data" in response.json()
```

## 未来改进

1. **依赖注入**: 考虑使用依赖注入框架，使服务层更易于测试和扩展
2. **缓存层**: 为频繁访问的数据（如排行榜）添加缓存
3. **异步优化**: 优化并发请求处理
4. **错误处理**: 统一的错误处理和日志记录
5. **性能监控**: 添加性能监控和追踪

## 相关文档

- [API参考文档](../api/API_REFERENCE.md)
- [播放列表功能文档](../playlist/README.md)
- [配置指南](../config/USER_CONFIG_GUIDE.md)

## 总结

本次重构成功地将业务逻辑从API路由层分离到独立的服务层，实现了：

- ✅ 清晰的代码结构和职责划分
- ✅ 提高了代码的可复用性
- ✅ 便于单元测试和维护
- ✅ 保持了API的向后兼容性
- ✅ 为未来的功能扩展奠定了良好的基础

所有现有功能都已成功迁移，API行为保持不变，客户端无需任何修改。
