# 播单模块重构说明

## 概述

将播单管理功能从单一的路由文件拆分为独立的模块，提高代码的可维护性和可测试性。

## 重构目标

1. **关注点分离**：将路由、业务逻辑、数据模型和存储分离
2. **提高可测试性**：业务逻辑独立，便于单元测试
3. **提高可维护性**：模块化设计，职责清晰
4. **提高可复用性**：服务层可被其他模块调用

## 模块结构

### 重构前
```
backend/src/xiaoai_media/api/routes/
└── playlist.py  (600+ 行，包含所有逻辑)
```

### 重构后
```
backend/src/xiaoai_media/
├── api/routes/
│   └── playlist.py          # 路由层（仅处理 HTTP 请求/响应）
└── playlist/
    ├── __init__.py          # 模块导出
    ├── models.py            # 数据模型
    ├── storage.py           # 存储管理
    └── service.py           # 业务逻辑
```

## 模块职责

### 1. models.py - 数据模型
**职责**：定义数据结构

**包含**：
- `PlaylistItem` - 播单项模型
- `PlaylistIndex` - 播单索引模型
- `Playlist` - 完整播单模型
- `CreatePlaylistRequest` - 创建请求模型
- `UpdatePlaylistRequest` - 更新请求模型
- `AddItemRequest` - 添加项请求模型
- `PlayPlaylistRequest` - 播放请求模型

**特点**：
- 纯数据模型，无业务逻辑
- 使用 Pydantic 进行数据验证
- 可被其他模块导入使用

### 2. storage.py - 存储管理
**职责**：处理文件系统操作

**包含**：
- `PlaylistStorage` 类（静态方法）
  - `get_playlists_dir()` - 获取存储目录
  - `get_index_file()` - 获取索引文件路径
  - `get_playlist_data_file()` - 获取数据文件路径
  - `ensure_storage_dir()` - 确保目录存在
  - `load_index()` - 加载索引
  - `save_index()` - 保存索引
  - `load_playlist_data()` - 加载播单数据
  - `save_playlist_data()` - 保存播单数据
  - `load_playlist()` - 加载完整播单
  - `save_playlist()` - 保存完整播单
  - `delete_playlist()` - 删除播单

**特点**：
- 只负责数据持久化
- 不包含业务逻辑
- 抛出 `RuntimeError` 而非 HTTP 异常
- 使用静态方法，无状态

### 3. service.py - 业务逻辑
**职责**：实现业务逻辑

**包含**：
- `PlaylistService` 类（静态方法）
  - `generate_playlist_id()` - 生成播单 ID
  - `make_proxy_url()` - 生成代理 URL
  - `get_item_url()` - 获取播放 URL
  - `list_playlists()` - 列出所有播单
  - `create_playlist()` - 创建播单
  - `get_playlist()` - 获取播单
  - `update_playlist()` - 更新播单
  - `delete_playlist()` - 删除播单
  - `add_items()` - 添加播单项
  - `delete_item()` - 删除播单项
  - `play_playlist()` - 播放播单
  - `play_by_voice_command()` - 语音播放

**特点**：
- 包含所有业务逻辑
- 调用存储层进行数据操作
- 抛出 `ValueError` 和 `RuntimeError`
- 使用静态方法，无状态
- 可被路由层和其他模块调用

### 4. playlist.py - 路由层
**职责**：处理 HTTP 请求和响应

**包含**：
- FastAPI 路由端点
- HTTP 请求验证
- HTTP 响应格式化
- 异常转换（业务异常 → HTTP 异常）

**特点**：
- 只包含路由定义
- 调用服务层处理业务逻辑
- 将业务异常转换为 HTTP 状态码
- 代码简洁，易于理解

## 异常处理策略

### 存储层 (storage.py)
- 抛出 `RuntimeError` - 存储操作失败

### 服务层 (service.py)
- 抛出 `ValueError` - 业务逻辑错误（如：播单不存在）
- 抛出 `RuntimeError` - 系统错误（如：配置文件不存在）

### 路由层 (playlist.py)
- `ValueError` → `HTTPException(404)` - 资源不存在
- `RuntimeError` → `HTTPException(502)` - 后端服务错误
- 其他异常 → `HTTPException(500)` - 服务器内部错误

## 代码对比

### 重构前（playlist.py）
```python
# 600+ 行，包含所有逻辑
def _get_playlists_dir() -> Path: ...
def _load_index() -> dict: ...
def _save_index(index: dict): ...
# ... 更多存储函数

class PlaylistItem(BaseModel): ...
class Playlist(BaseModel): ...
# ... 更多模型

@router.get("")
async def list_playlists():
    index = _load_index()
    return {"playlists": [...], "total": len(index)}
```

### 重构后

#### models.py
```python
# 纯数据模型
class PlaylistItem(BaseModel):
    title: str
    artist: str
    # ...
```

#### storage.py
```python
# 存储管理
class PlaylistStorage:
    @staticmethod
    def load_index() -> dict[str, PlaylistIndex]:
        # 加载索引逻辑
        ...
```

#### service.py
```python
# 业务逻辑
class PlaylistService:
    @staticmethod
    def list_playlists() -> dict:
        index = PlaylistStorage.load_index()
        return {"playlists": list(index.values()), "total": len(index)}
```

#### playlist.py
```python
# 路由层
@router.get("")
async def list_playlists():
    try:
        return PlaylistService.list_playlists()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 优势

### 1. 代码组织
- ✅ 职责清晰，易于理解
- ✅ 文件大小合理（每个文件 100-300 行）
- ✅ 模块化设计，便于导航

### 2. 可测试性
- ✅ 业务逻辑独立，可单独测试
- ✅ 存储层可 mock，便于单元测试
- ✅ 路由层简单，集成测试即可

### 3. 可维护性
- ✅ 修改存储逻辑不影响业务逻辑
- ✅ 修改业务逻辑不影响路由定义
- ✅ 添加新功能只需修改对应模块

### 4. 可复用性
- ✅ 服务层可被其他模块调用
- ✅ 存储层可被其他服务使用
- ✅ 模型可在多处共享

## 迁移指南

### 对外部调用的影响
**无影响** - API 端点保持不变，只是内部实现重构

### 对测试的影响
- 可以直接测试 `PlaylistService` 而不需要启动 HTTP 服务
- 可以 mock `PlaylistStorage` 进行单元测试

### 示例：单元测试

#### 重构前
```python
# 需要启动 FastAPI 应用
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get("/api/playlists")
```

#### 重构后
```python
# 可以直接测试服务层
from xiaoai_media.playlist import PlaylistService

result = PlaylistService.list_playlists()
assert "playlists" in result
```

## 后续优化

### 短期
- [ ] 添加服务层单元测试
- [ ] 添加存储层单元测试
- [ ] 完善异常处理

### 中期
- [ ] 考虑使用依赖注入
- [ ] 添加缓存层
- [ ] 优化并发访问

### 长期
- [ ] 考虑使用数据库替代文件存储
- [ ] 添加事务支持
- [ ] 实现播单版本控制

## 相关文档

- [播单存储重构](PLAYLIST_STORAGE_REFACTOR.md)
- [播单功能指南](../playlist/PLAYLIST_GUIDE.md)
- [API 参考](../api/API_REFERENCE.md)

---

**重构完成日期**：2024-01-XX  
**重构人员**：Kiro AI Assistant
