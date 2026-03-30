# Music Provider 更新日志

## 2026-03-23 - 接口迁移更新

### 新增功能

在 `music_provider.py` 和 `music_provider_template.py` 中新增以下接口：

1. **search_music()** - 搜索音乐
   - 支持用户自定义搜索逻辑
   - 可添加缓存、聚合多个音乐源等

2. **get_ranks()** - 获取排行榜列表
   - 支持用户自定义排行榜获取逻辑
   - 可过滤、添加自定义排行榜等

3. **get_rank_songs()** - 获取排行榜歌曲
   - 支持用户自定义排行榜歌曲获取逻辑
   - 可过滤、重新排序等

### 架构改进

- **职责分离**：`MusicService` 只负责参数校验，`music_provider` 负责实际 API 调用
- **统一接口**：所有音乐相关的可自定义接口都在 `music_provider` 中
- **易于扩展**：用户可以轻松替换或增强任何音乐相关功能

### 文档更新

- 更新了 `music_provider_template.py` 的文档说明
- 添加了详细的使用示例和参数说明
- 创建了 `docs/refactor/MUSIC_PROVIDER_MIGRATION.md` 迁移文档

### 兼容性

- ✅ 完全向后兼容
- ✅ 所有现有 API 接口保持不变
- ✅ 无需修改现有代码

### 使用方法

用户现在可以在 `music_provider.py` 中自定义以下功能：

```python
# 自定义搜索（例如添加缓存）
async def search_music(query, platform, page, limit, music_api_base_url, timeout=10):
    # 你的自定义逻辑
    pass

# 自定义排行榜获取
async def get_ranks(platform, music_api_base_url, timeout=10):
    # 你的自定义逻辑
    pass

# 自定义排行榜歌曲获取
async def get_rank_songs(rank_id, platform, page, limit, music_api_base_url, timeout=10):
    # 你的自定义逻辑
    pass

# 自定义播放 URL 获取（已有功能）
async def get_music_url(params, music_api_base_url, timeout=10):
    # 你的自定义逻辑
    pass
```

### 相关文档

- [MUSIC_PROVIDER_MIGRATION.md](docs/refactor/MUSIC_PROVIDER_MIGRATION.md) - 详细的迁移说明
- [MUSIC_PROVIDER_REFACTOR.md](docs/refactor/MUSIC_PROVIDER_REFACTOR.md) - 音乐提供者模块重构

---

**更新日期**：2026-03-23  
**影响范围**：music_provider.py, music_provider_template.py, MusicService  
**破坏性变更**：无
