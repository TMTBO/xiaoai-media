# 播单管理功能使用指南

## 功能概述

播单管理功能允许您创建和管理多个播放列表（音乐、有声书、播客等），并通过语音命令控制播放。

## 主要特性

1. **多播单支持** - 可以创建多个不同类型的播单
2. **灵活的 URL 处理** - 支持直接 URL 或通过 `user_config.py` 动态获取
3. **语音命令控制** - 通过自定义关键词实现语音控制
4. **自动代理** - 自动使用工程的代理服务处理 URL

## 使用步骤

### 1. 创建播单

在"播单管理"页面，点击"新建播单"按钮：

- **播单名称**：例如"我的音乐"、"有声书"、"播客"
- **类型**：例如 `music`、`audiobook`、`podcast`（可选）
- **描述**：播单的详细描述（可选）
- **语音关键词**：用于语音识别的关键词，例如"音乐"、"歌单"、"有声书"

### 2. 添加播单项

点击"管理项目"按钮，然后点击"添加项目"：

#### 方式一：直接提供 URL

如果您已经有音频的直接 URL，填写以下信息：

- **标题**：音频标题（必填）
- **艺术家/作者**：可选
- **专辑/系列**：可选
- **播放 URL**：音频的直接 URL
- **封面 URL**：封面图片 URL（可选）
- **时长**：音频时长（秒）

#### 方式二：动态获取 URL

如果需要通过 `user_config.py` 动态获取 URL：

1. 将"播放 URL"留空
2. 在"自定义参数"中填写 JSON 格式的参数，例如：

```json
{
  "type": "music",
  "platform": "tx",
  "song_id": "001ABC"
}
```

3. 在 `user_config.py` 中实现 `get_audio_url` 函数来处理这些参数

### 3. 配置 user_config.py

如果使用动态 URL 获取，需要在 `user_config.py` 中实现 `get_audio_url` 函数：

```python
def get_audio_url(custom_params: dict) -> str:
    """
    根据音频信息获取播放 URL
    
    Args:
        custom_params: 自定义参数字典
    
    Returns:
        播放 URL（原始 URL，系统会自动添加代理）
    """
    audio_type = custom_params.get("type", "")
    
    if audio_type == "music":
        platform = custom_params.get("platform", "tx")
        song_id = custom_params.get("song_id", "")
        # 调用第三方音乐 API 获取 URL
        # ...
        return music_url
    
    elif audio_type == "audiobook":
        book_id = custom_params.get("book_id", "")
        chapter = custom_params.get("chapter", "1")
        # 获取有声书 URL
        # ...
        return audiobook_url
    
    # ... 更多类型处理
```

### 4. 播放播单

#### 方式一：手动播放

在播单列表中，点击"播放"按钮即可播放播单。

#### 方式二：语音命令

启用对话监听后，可以通过语音命令播放：

- "播放音乐播单"
- "播放有声书播单"
- "播放我的歌单"

系统会根据播单的语音关键词匹配对应的播单进行播放。

## 工作原理

### URL 代理流程

```
播单项 URL → 检查 URL 是否存在
            ↓
         是否为空？
       /          \
      是           否
     ↓             ↓
调用 user_config   直接使用 URL
get_audio_url()      ↓
     ↓            包装为代理 URL
  返回 URL          ↓
     ↓           发送到音箱播放
包装为代理 URL
     ↓
发送到音箱播放
```

### 代理 URL 格式

原始 URL：
```
https://example.com/audio/song.mp3
```

代理 URL：
```
http://10.184.62.160:5050/main/proxy?url=https%3A%2F%2Fexample.com%2Faudio%2Fsong.mp3
```

代理服务会添加必要的请求头并转发音频流到音箱。

## API 端点

播单管理提供以下 API 端点：

- `GET /api/playlists` - 获取所有播单
- `POST /api/playlists` - 创建新播单
- `GET /api/playlists/{id}` - 获取指定播单
- `PUT /api/playlists/{id}` - 更新播单
- `DELETE /api/playlists/{id}` - 删除播单
- `POST /api/playlists/{id}/items` - 添加播单项
- `DELETE /api/playlists/{id}/items/{index}` - 删除播单项
- `POST /api/playlists/{id}/play` - 播放播单
- `POST /api/playlists/play-by-voice` - 根据语音命令播放

## 数据存储

播单数据存储在：
```
~/.xiaoai-media/playlists.json
```

## 注意事项

1. **URL 格式**：确保提供的 URL 是直接的音频文件链接
2. **代理服务**：确保 `MUSIC_API_BASE_URL` 配置正确
3. **语音关键词**：避免使用过于常见的词汇，以免误触发
4. **自定义参数**：JSON 格式必须正确，否则会导致添加失败
5. **对话监听**：语音命令播放需要启用对话监听功能

## 示例场景

### 场景 1：音乐播单

创建一个音乐播单，使用音乐搜索 API 动态获取 URL：

```python
# user_config.py
def get_audio_url(custom_params: dict) -> str:
    import requests
    
    platform = custom_params.get("platform", "tx")
    song_id = custom_params.get("song_id")
    
    # 调用音乐 API
    response = requests.get(
        f"{MUSIC_API_BASE_URL}/api/v3/{platform}/song/{song_id}"
    )
    data = response.json()
    
    # 返回最高音质的 URL
    return data["data"]["url"]
```

### 场景 2：有声书播单

创建有声书播单，直接提供 URL：

在添加项目时，直接填写：
- **标题**：西游记第01回
- **播放 URL**：`https://audiobook.example.com/xiyouji/01.mp3`
- **艺术家**：吴承恩
- **专辑**：西游记

### 场景 3：播客播单

混合使用直接 URL 和动态获取：

- 部分已下载的播客：直接提供本地文件 URL
- 在线播客：通过 RSS 源动态获取

## 故障排除

### 播放失败

1. 检查 URL 是否有效
2. 确认代理服务是否正常运行
3. 查看日志获取详细错误信息

### 语音命令不响应

1. 确认对话监听是否启用
2. 检查语音关键词是否正确配置
3. 确认唤醒词过滤设置

### 动态 URL 获取失败

1. 检查 `user_config.py` 中的 `get_audio_url` 函数实现
2. 确认自定义参数格式正确
3. 查看后端日志了解具体错误

## 更新日志

### v1.0.0 (2026-03-20)

- ✨ 新增播单管理功能
- ✨ 支持多播单管理
- ✨ 支持直接 URL 和动态 URL 获取
- ✨ 支持语音命令控制
- ✨ 自动代理 URL 处理
