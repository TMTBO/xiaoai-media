# 播放列表服务迁移文档

## 概述

播放列表模块已从独立的 `playlist/` 目录迁移到统一的 `services/` 层，与其他服务模块保持一致的架构。

## 迁移内容

### 文件迁移

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `playlist/models.py` | `services/playlist_models.py` | 数据模型定义 |
| `playlist/service.py` | `services/playlist_service.py` | 业务逻辑服务 |
| `playlist/storage.py` | `services/playlist_storage.py` | 存储管理 |
| `playlist/__init__.py` | `playlist/__init__.py` (兼容层) | 保留作为向后兼容 |

### 目录结构

**迁移前**:
```
backend/src/xiaoai_media/
├── api/routes/
│   └── playlist.py
├── playlist/              # 独立模块
│   ├── __init__.py
│   ├── models.py
│   ├── service.py
│   └── storage.py
└── services/              # 其他服务
    ├── music_service.py
    └── config_service.py
```

**迁移后**:
```
backend/src/xiaoai_media/
├── api/routes/
│   └── playlist.py        # 更新导入路径
├── playlist/              # 兼容层
│   └── __init__.py        # 转发导入
└── services/              # 统一服务层
    ├── music_service.py
    ├── config_service.py
    ├── playlist_service.py    # 从 playlist/service.py 迁移
    ├── playlist_storage.py    # 从 playlist/storage.py 迁移
    ├── playlist_models.py     # 从 playlist/models.py 迁移
    └── playlist_loader.py
```

## 导入路径变更

### 旧的导入方式（已弃用）

```python
from xiaoai_media.playlist import (
    PlaylistService,
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    CreatePlaylistRequest,
    UpdatePlaylistRequest,
    AddItemRequest,
    PlayPlaylistRequest,
)
```

### 新的导入方式（推荐）

```python
from xiaoai_media.services import (
    PlaylistService,
    Playlist,
    PlaylistIndex,
    PlaylistItem,
    CreatePlaylistRequest,
    UpdatePlaylistRequest,
    AddItemRequest,
    PlayPlaylistRequest,
    PlaylistStorage,
)
```

## 向后兼容性

### 兼容层实现

为了保持向后兼容，`playlist/__init__.py` 保留作为兼容层：

```python
# playlist/__init__.py
import warnings

warnings.warn(
    "xiaoai_media.playlist module is deprecated. "
    "Please import from xiaoai_media.services instead.",
    DeprecationWarning,
    stacklevel=2,
)

# 从新位置导入
from xiaoai_media.services import (
    PlaylistService,
    Playlist,
    # ... 其他导出
)
```

### 使用旧导入的影响

- ✅ 代码仍然可以正常工作
- ⚠️ 会显示弃用警告
- 📝 建议尽快迁移到新的导入方式

## 服务模块说明

### PlaylistService - 播放列表服务

**职责**: 播放列表的业务逻辑处理

**主要方法**:
- `list_playlists()` - 获取所有播放列表
- `create_playlist()` - 创建新播放列表
- `get_playlist()` - 获取指定播放列表
- `update_playlist()` - 更新播放列表信息
- `delete_playlist()` - 删除播放列表
- `add_items()` - 添加播放列表项
- `delete_item()` - 删除播放列表项
- `play_playlist()` - 播放播放列表
- `play_by_voice_command()` - 语音命令播放
- `get_item_url()` - 获取播放URL
- `make_proxy_url()` - 生成代理URL

**使用示例**:
```python
from xiaoai_media.services import PlaylistService, CreatePlaylistRequest

# 创建播放列表
playlist = PlaylistService.create_playlist(
    CreatePlaylistRequest(
        name="我的音乐",
        type="music",
        description="我喜欢的歌曲",
        voice_keywords=["音乐", "歌曲"]
    )
)

# 获取所有播放列表
result = PlaylistService.list_playlists()

# 播放播放列表
result = await PlaylistService.play_playlist(
    playlist_id="音乐_1234567890",
    req=PlayPlaylistRequest(device_id="xxx", start_index=0)
)
```

### PlaylistStorage - 播放列表存储

**职责**: 播放列表的文件存储和索引管理

**主要方法**:
- `get_playlists_dir()` - 获取存储目录
- `get_index_file()` - 获取索引文件路径
- `get_playlist_data_file()` - 获取数据文件路径
- `ensure_storage_dir()` - 确保目录存在
- `load_index()` - 加载索引
- `save_index()` - 保存索引
- `load_playlist_data()` - 加载播放列表数据
- `save_playlist_data()` - 保存播放列表数据
- `load_playlist()` - 加载完整播放列表
- `save_playlist()` - 保存完整播放列表
- `delete_playlist()` - 删除播放列表文件

**存储结构**:
```
~/.xiaoai_media/playlists/
├── index.json                    # 索引文件
├── 音乐_1234567890.json          # 播放列表数据
└── 有声书_9876543210.json        # 播放列表数据
```

**使用示例**:
```python
from xiaoai_media.services import PlaylistStorage

# 加载索引
index = PlaylistStorage.load_index()

# 加载完整播放列表
playlist = PlaylistStorage.load_playlist("音乐_1234567890")

# 保存播放列表
PlaylistStorage.save_playlist(playlist)

# 删除播放列表
PlaylistStorage.delete_playlist("音乐_1234567890")
```

### PlaylistModels - 数据模型

**定义的模型**:
- `Playlist` - 完整播放列表
- `PlaylistIndex` - 播放列表索引信息
- `PlaylistItem` - 播放列表项
- `CreatePlaylistRequest` - 创建请求
- `UpdatePlaylistRequest` - 更新请求
- `AddItemRequest` - 添加项请求
- `PlayPlaylistRequest` - 播放请求

**使用示例**:
```python
from xiaoai_media.services import (
    Playlist,
    PlaylistItem,
    CreatePlaylistRequest,
)

# 创建播放列表项
item = PlaylistItem(
    title="歌曲名",
    artist="歌手名",
    album="专辑名",
    url="https://..."
)

# 创建播放列表
playlist = Playlist(
    id="音乐_1234567890",
    name="我的音乐",
    type="music",
    items=[item],
    voice_keywords=["音乐"]
)
```

## 迁移步骤

### 1. 更新导入语句

**查找并替换**:
```bash
# 查找旧的导入
grep -r "from xiaoai_media.playlist import" .

# 替换为新的导入
# from xiaoai_media.playlist import → from xiaoai_media.services import
```

### 2. 测试功能

确保所有播放列表相关功能正常工作：
- ✅ 创建播放列表
- ✅ 获取播放列表列表
- ✅ 获取单个播放列表
- ✅ 更新播放列表
- ✅ 删除播放列表
- ✅ 添加播放列表项
- ✅ 删除播放列表项
- ✅ 播放播放列表
- ✅ 语音命令播放

### 3. 移除弃用警告

更新所有使用旧导入的代码，消除弃用警告。

## API端点

所有API端点保持不变：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/playlists` | GET | 获取所有播放列表 |
| `/api/playlists` | POST | 创建新播放列表 |
| `/api/playlists/{id}` | GET | 获取指定播放列表 |
| `/api/playlists/{id}` | PUT | 更新播放列表 |
| `/api/playlists/{id}` | DELETE | 删除播放列表 |
| `/api/playlists/{id}/items` | POST | 添加播放列表项 |
| `/api/playlists/{id}/items/{index}` | DELETE | 删除播放列表项 |
| `/api/playlists/{id}/play` | POST | 播放播放列表 |
| `/api/playlists/play-by-voice` | POST | 语音命令播放 |

## 优势

### 1. 统一的架构
- 所有服务模块在同一目录下
- 一致的命名和组织方式
- 便于理解和维护

### 2. 更好的模块化
- 清晰的职责划分
- 服务层、存储层、模型层分离
- 易于测试和扩展

### 3. 代码复用
- 播放列表服务可以被其他模块使用
- 与其他服务（音乐、配置）集成更方便

### 4. 向后兼容
- 旧代码仍然可以工作
- 平滑的迁移路径
- 清晰的弃用警告

## 测试建议

### 单元测试

```python
import pytest
from xiaoai_media.services import PlaylistService, CreatePlaylistRequest

def test_create_playlist():
    req = CreatePlaylistRequest(
        name="测试播放列表",
        type="music",
        voice_keywords=["测试"]
    )
    playlist = PlaylistService.create_playlist(req)
    assert playlist.name == "测试播放列表"
    assert playlist.type == "music"

def test_list_playlists():
    result = PlaylistService.list_playlists()
    assert "playlists" in result
    assert "total" in result
```

### 集成测试

```python
from fastapi.testclient import TestClient

def test_create_playlist_endpoint(client: TestClient):
    response = client.post("/api/playlists", json={
        "name": "测试播放列表",
        "type": "music",
        "voice_keywords": ["测试"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试播放列表"
```

## 相关文档

- [API服务层重构文档](./API_SERVICES_REFACTOR.md)
- [服务层快速参考](./SERVICES_QUICK_REFERENCE.md)
- [播放列表功能文档](../playlist/README.md)
- [服务层README](../../backend/src/xiaoai_media/services/README.md)

## 总结

播放列表模块已成功迁移到统一的服务层：

✅ 文件已迁移到 `services/` 目录  
✅ 导入路径已更新  
✅ 保持向后兼容性  
✅ API端点保持不变  
✅ 所有功能正常工作  
✅ 文档已更新  

建议尽快将代码中的旧导入方式更新为新的导入方式，以消除弃用警告。
