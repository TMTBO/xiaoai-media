# 播单存储结构重构 - 更新日志

## 版本：v1.0.0
## 日期：2024-01-XX

### 🎯 重构目标

将播单存储从单文件格式重构为多文件格式，提高性能和可维护性。

### ✨ 主要变更

#### 1. 存储结构优化

**旧格式（单文件）：**
```
playlists.json  # 包含所有播单的完整数据
```

**新格式（多文件）：**
```
playlists/
├── index.json           # 播单索引文件
├── {playlist_id_1}.json # 播单1的详细数据
├── {playlist_id_2}.json # 播单2的详细数据
└── ...
```

#### 2. 数据结构精简

**播单项字段变更：**

保留字段：
- `title`: 歌曲名
- `artist`: 艺术家
- `album`: 专辑名
- `audio_id`: 音频ID（新增）
- `url`: 音频URL
- `custom_params`: 自定义参数

移除字段：
- `duration`: 时长（不影响播放）
- `cover_url`: 封面URL（不影响播放）

#### 3. API 变更

**列表接口返回类型变更：**
```typescript
// 旧版本
GET /api/playlists
Response: { playlists: Playlist[] }  // 包含完整数据

// 新版本
GET /api/playlists
Response: { playlists: PlaylistIndex[] }  // 只包含索引信息
```

**新增类型：**
```typescript
interface PlaylistIndex {
  id: string
  name: string
  type: string
  description: string
  voice_keywords: string[]
  item_count: number  // 新增：播单项数量
  created_at: string
  updated_at: string
}
```

### 🚀 性能优化

1. **按需加载**：列表页面只加载索引信息，减少数据传输
2. **快速匹配**：语音播放从索引文件匹配唤醒词，无需加载完整数据
3. **减少内存占用**：不需要一次性加载所有播单的完整数据

### 📦 新增文件

#### 后端
- 更新：`backend/src/xiaoai_media/api/routes/playlist.py`
  - 新增：`_get_playlists_dir()` - 获取播单目录
  - 新增：`_get_index_file()` - 获取索引文件路径
  - 新增：`_get_playlist_data_file()` - 获取播单数据文件路径
  - 新增：`_load_index()` - 加载索引
  - 新增：`_save_index()` - 保存索引
  - 新增：`_load_playlist_data()` - 加载播单数据
  - 新增：`_save_playlist_data()` - 保存播单数据
  - 新增：`_load_playlist()` - 加载完整播单
  - 新增：`_save_playlist()` - 保存完整播单
  - 新增：`_delete_playlist_files()` - 删除播单文件
  - 新增：`PlaylistIndex` 数据模型

#### 前端
- 更新：`frontend/src/api/index.ts`
  - 新增：`PlaylistIndex` 类型定义
  - 更新：`PlaylistItem` 类型定义（精简字段）
  - 更新：`listPlaylists()` 返回类型

- 更新：`frontend/src/views/PlaylistManager.vue`
  - 更新：使用 `PlaylistIndex` 类型
  - 更新：点击"项目"按钮时才加载完整数据
  - 更新：表单字段（移除时长和封面，添加音频ID）

#### 脚本
- 新增：`scripts/migrate_playlists.py` - 数据迁移脚本

#### 文档
- 新增：`docs/playlist/PLAYLIST_STORAGE_REFACTOR.md` - 重构说明文档
- 更新：`docs/playlist/README.md` - 添加存储结构说明

#### 测试
- 新增：`test/playlist/test_storage_refactor.py` - 存储结构测试

### 🔄 数据迁移

提供自动迁移脚本：

```bash
python scripts/migrate_playlists.py
```

迁移脚本功能：
1. 读取旧的 `playlists.json` 文件
2. 创建新的 `playlists/` 目录
3. 生成索引文件和独立的播单数据文件
4. 备份旧文件为 `playlists.json.backup`

### ⚠️ 破坏性变更

1. **列表接口返回类型变更**
   - 影响：前端需要更新类型定义
   - 解决：已同步更新前端代码

2. **播单项字段变更**
   - 影响：移除了 `duration` 和 `cover_url` 字段
   - 解决：这些字段不影响播放功能，可安全移除

### ✅ 向后兼容性

- 旧的 `playlists.json` 文件会被自动迁移
- 迁移后旧文件会被备份，不会丢失数据
- 所有现有 API 端点保持不变（除列表接口返回类型）

### 📝 使用说明

#### 首次启动

如果存在旧的 `playlists.json` 文件：

```bash
# 1. 运行迁移脚本
python scripts/migrate_playlists.py

# 2. 启动服务
python -m xiaoai_media.api.main
```

#### 新安装

无需任何操作，系统会自动创建新的存储结构。

### 🧪 测试

运行测试验证新的存储结构：

```bash
# 运行播单存储测试
pytest test/playlist/test_storage_refactor.py -v

# 运行所有播单测试
pytest test/playlist/ -v
```

### 📚 相关文档

- [存储结构重构说明](docs/playlist/PLAYLIST_STORAGE_REFACTOR.md)
- [播单功能指南](docs/playlist/PLAYLIST_GUIDE.md)
- [API 参考](docs/api/API_REFERENCE.md)

### 🙏 致谢

感谢所有参与测试和反馈的用户！

---

## 下一步计划

- [ ] 添加播单导入/导出功能
- [ ] 支持播单分享
- [ ] 添加播单封面图片支持
- [ ] 优化语音匹配算法
