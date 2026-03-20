# 播单管理功能改进 - 更新说明

## 本次更新内容

### 1. ✅ 播单管理默认设备选择

**改进前：** 打开播单管理页面时，设备选择器为空，需要手动选择设备。

**改进后：** 
- 自动从配置文件读取 `MI_DID` 作为默认设备
- 如果配置的设备在设备列表中存在，会自动选中
- 无需每次手动选择设备，提升使用体验

**实现位置：**
- `frontend/src/views/PlaylistManager.vue` - `loadDevices()` 函数

### 2. ✅ 从音乐搜索/排行榜创建播单

**新增功能：** 可以一键将搜索结果或排行榜歌曲创建为播单

**使用方式：**

#### 从搜索结果创建播单
1. 在"音乐搜索"标签页搜索歌曲
2. 点击搜索结果上方的"创建播单"按钮
3. 输入播单名称、类型和描述（会自动预填）
4. 确认后，所有搜索结果会被添加到新播单中

#### 从排行榜创建播单
1. 在"排行榜"标签页选择一个排行榜
2. 点击右上角的"创建播单"按钮
3. 输入播单名称（会自动预填为排行榜名称）
4. 确认后，所有榜单歌曲会被添加到新播单中

**特点：**
- 自动预填播单名称和描述
- 歌曲信息完整保存（包括平台、ID、音质等）
- 使用动态 URL 获取，播放时才获取真实链接
- 创建成功后显示添加歌曲数量

**实现位置：**
- `frontend/src/views/MusicPanel.vue`
  - 添加"创建播单"按钮
  - `handleCreatePlaylist()` - 打开创建对话框
  - `confirmCreatePlaylist()` - 执行创建操作

### 3. ✅ 播单存储目录可配置

**改进前：** 播单数据固定存储在 `~/.xiaoai-media/playlists.json`

**改进后：** 
- 可以在 `user_config.py` 中配置存储目录
- 默认值为 `~/.xiaoai-media`，可自定义为任意路径

**配置方法：**

在 `user_config.py` 中添加或修改：
```python
# 播单数据存储目录
# 默认为用户目录下的 .xiaoai-media，可以自定义路径
PLAYLIST_STORAGE_DIR = "~/.xiaoai-media"

# 自定义示例：
# PLAYLIST_STORAGE_DIR = "~/Documents/xiaoai-playlists"
# PLAYLIST_STORAGE_DIR = "/data/music/playlists"
```

播单文件会存储在：`{PLAYLIST_STORAGE_DIR}/playlists.json`

**实现位置：**
- `user_config.py` - 添加 `PLAYLIST_STORAGE_DIR` 配置
- `backend/src/xiaoai_media/config.py` - 读取配置
- `backend/src/xiaoai_media/api/routes/playlist.py` - 使用配置的路径

### 4. ✨ 改进音乐 URL 获取逻辑

**改进内容：**

在 `user_config.py` 中的 `get_audio_url()` 函数现在能够：
- 调用真实的音乐下载 API 获取播放 URL
- 自动选择最高音质（flac > 320k > 128k）
- 处理错误情况并提供友好的错误信息

**实现代码：**
```python
def get_audio_url(custom_params: dict) -> str:
    """根据音频信息获取播放 URL"""
    import requests
    
    if custom_params.get("type") == "music":
        platform = custom_params.get("platform", "tx")
        song_id = custom_params.get("song_id", "")
        qualities = custom_params.get("qualities", [])
        
        # 选择最高音质
        quality_type = "320k"
        if qualities:
            for q in qualities:
                q_type = q.get("type", "")
                if "flac" in q_type.lower():
                    quality_type = q_type
                    break
                elif "320" in q_type:
                    quality_type = q_type
                    break
        
        # 调用音乐下载 API
        response = requests.post(
            f"{MUSIC_API_BASE_URL}/api/v3/song/{platform}/{song_id}",
            json={"quality": quality_type},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200 and data.get("data"):
                return data["data"].get("url")
        
        raise ValueError(f"Failed to get music URL: {platform}/{song_id}")
    
    # ... 其他类型的实现
```

## 使用场景示例

### 场景 1：快速创建周杰伦歌曲播单

1. 打开"音乐搜索"，搜索"周杰伦"
2. 点击"创建播单"按钮
3. 播单名称自动填充为"周杰伦 的搜索结果"
4. 点击"创建"，所有周杰伦的歌曲添加到播单
5. 在"播单管理"页面可以看到新创建的播单
6. 点击"播放"即可播放整个播单

### 场景 2：创建热门排行榜播单

1. 打开"排行榜"，选择"腾讯音乐"
2. 点击"热歌榜"查看歌曲列表
3. 点击右上角"创建播单"按钮
4. 播单名称自动填充为"热歌榜"
5. 确认创建，榜单所有歌曲添加到播单
6. 可以通过语音命令"播放热歌榜"来播放

### 场景 3：自定义存储路径

如果您想将播单数据存储在特定位置：

1. 编辑 `user_config.py`：
```python
PLAYLIST_STORAGE_DIR = "~/Music/xiaoai-playlists"
```

2. 重启后端服务
3. 新的播单数据会存储在 `~/Music/xiaoai-playlists/playlists.json`
4. 原有播单数据可以手动复制到新位置

## 技术细节

### 播单项数据结构

从音乐搜索/排行榜创建的播单项包含以下信息：

```json
{
  "title": "歌曲名",
  "artist": "歌手",
  "album": "专辑",
  "duration": 180,
  "cover_url": "封面图片URL",
  "url": "",
  "custom_params": {
    "type": "music",
    "platform": "tx",
    "song_id": "001ABC",
    "qualities": [
      {"type": "320k", "format": "mp3", "size": "9.15M"},
      {"type": "flac", "format": "flac", "size": "28.5M"}
    ]
  }
}
```

- `url` 留空，播放时通过 `custom_params` 动态获取
- `custom_params` 包含所有必要的音乐信息
- 系统会自动选择最高音质播放

### 配置加载顺序

1. 系统读取 `user_config.py` 中的 `PLAYLIST_STORAGE_DIR`
2. 如果未配置，使用默认值 `~/.xiaoai-media`
3. 路径会进行 `expanduser()` 展开（支持 `~` 符号）
4. 确保目录存在，不存在会自动创建

## 文件变更清单

### 修改的文件

**前端：**
- `frontend/src/views/PlaylistManager.vue`
  - 添加默认设备自动选择逻辑
- `frontend/src/views/MusicPanel.vue`
  - 添加"创建播单"按钮和对话框
  - 实现创建播单功能

**后端：**
- `user_config.py`
  - 添加 `PLAYLIST_STORAGE_DIR` 配置
  - 改进 `get_audio_url()` 函数实现
- `backend/src/xiaoai_media/config.py`
  - 添加 `PLAYLIST_STORAGE_DIR` 配置读取
- `backend/src/xiaoai_media/api/routes/playlist.py`
  - 使用可配置的存储路径

## 注意事项

1. **音乐 API 依赖**：
   - 播放从搜索/排行榜创建的播单需要音乐下载 API 正常运行
   - 确保 `MUSIC_API_BASE_URL` 配置正确

2. **存储路径修改**：
   - 修改存储路径后需要重启后端服务
   - 原有播单数据不会自动迁移，需要手动复制

3. **播单数量**：
   - 从排行榜创建播单可能包含大量歌曲（50-100首）
   - 建议根据需要选择性创建

4. **并发创建**：
   - 同时创建多个播单时，请等待上一个完成后再创建下一个

## 后续优化建议

1. 支持批量导入本地音频文件
2. 添加播单合并功能
3. 支持播单分享（导出/导入 JSON）
4. 添加播放历史记录
5. 支持智能播单（根据播放记录推荐）

## 反馈

如有问题或建议，请提交 Issue。
