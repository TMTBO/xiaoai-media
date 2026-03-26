# 删除播单中的 interval 和 pic_url 字段

## 修改日期
2024-XX-XX

## 修改说明
从播单数据模型中删除了 `interval` 和 `pic_url` 两个字段，以及它们在前后端的所有引用。

## 修改的文件

### 后端文件

1. **backend/src/xiaoai_media/services/playlist_models.py**
   - 从 `PlaylistItem` 模型中删除 `interval` 和 `pic_url` 字段
   - 从 `PlaylistIndex` 模型中删除 `interval` 和 `pic_url` 字段
   - 从 `Playlist` 模型中删除 `interval` 和 `pic_url` 字段
   - 从 `CreatePlaylistRequest` 模型中删除 `interval` 和 `pic_url` 字段
   - 从 `UpdatePlaylistRequest` 模型中删除 `interval` 和 `pic_url` 字段

2. **backend/src/xiaoai_media/services/playlist_service.py**
   - 从 `get_item_url()` 方法中删除对这两个字段的引用
   - 从 `create_playlist()` 方法中删除对这两个字段的赋值
   - 从 `update_playlist()` 方法中删除对这两个字段的更新逻辑

3. **backend/src/xiaoai_media/services/playlist_storage.py**
   - 从 `load_playlist()` 方法中删除对这两个字段的加载
   - 从 `save_playlist()` 方法中删除对这两个字段的保存

4. **backend/src/xiaoai_media/player.py**
   - 从创建 `PlaylistItem` 时删除 `interval` 和 `pic_url` 参数

5. **user_config.py**
   - 更新 `get_audio_url()` 函数的文档说明，删除对这两个字段的描述

6. **user_config_template.py**
   - 更新 `get_audio_url()` 函数的文档说明，删除对这两个字段的描述

7. **music_provider.py**
   - 更新 `get_music_url()` 函数的文档说明，删除对这两个字段的描述

8. **music_provider_template.py**
   - 更新 `get_music_url()` 函数的文档说明，删除对这两个字段的描述

### 前端文件

1. **frontend/src/api/index.ts**
   - 从 `PlaylistItem` 接口中删除 `interval` 和 `pic_url` 字段
   - 从 `PlaylistIndex` 接口中删除 `interval` 和 `pic_url` 字段
   - 从 `Playlist` 接口中删除 `interval` 和 `pic_url` 字段
   - 从 `CreatePlaylistRequest` 接口中删除 `interval` 和 `pic_url` 字段
   - 从 `UpdatePlaylistRequest` 接口中删除 `interval` 和 `pic_url` 字段

2. **frontend/src/views/PlaylistManager.vue**
   - 从播单表单中删除 `interval` 和 `pic_url` 输入框
   - 从播单项表单中删除 `interval` 和 `pic_url` 输入框
   - 从 `playlistForm` 数据对象中删除这两个字段
   - 从 `itemForm` 数据对象中删除这两个字段
   - 从 `resetCreateForm()` 函数中删除这两个字段的重置
   - 从 `handleEdit()` 函数中删除这两个字段的赋值

## 影响范围

- 现有的播单数据文件（JSON）中如果包含这两个字段，不会影响系统运行，这些字段会被忽略
- 新创建的播单将不再包含这两个字段
- 前端界面不再显示和编辑这两个字段

## 注意事项

如果需要存储音频时长或封面图片信息，可以通过 `custom_params` 字段来实现，例如：

```json
{
  "title": "歌曲名",
  "custom_params": {
    "duration": 240,
    "cover_url": "https://example.com/cover.jpg"
  }
}
```
