# 播单管理功能 - 版本更新说明

## 新增功能

### 📋 播单管理系统

为工程添加了完整的播单（播放列表）管理功能，支持创建和管理多个不同类型的播单。

#### 主要特性

1. **多播单支持**
   - 支持创建多个不同类型的播单（音乐、有声书、播客等）
   - 每个播单可以包含多个音频项
   - 支持自定义播单名称、类型、描述

2. **灵活的 URL 处理**
   - **方式一**：直接提供音频 URL
   - **方式二**：通过 `user_config.py` 中的 `get_audio_url()` 函数动态获取
   - 自动使用工程代理服务包装 URL，解决防盗链问题

3. **语音命令控制**
   - 支持自定义语音关键词
   - 通过语音命令播放播单（例如："播放音乐播单"、"播放有声书"）
   - 自动匹配播单并播放

4. **完整的 Web 管理界面**
   - 创建、编辑、删除播单
   - 添加、删除播单项
   - 实时播放控制
   - 设备选择

## 技术实现

### 后端

**新增文件：**
- `backend/src/xiaoai_media/api/routes/playlist.py` - 播单管理路由
- `docs/PLAYLIST_GUIDE.md` - 详细使用指南

**更新文件：**
- `backend/src/xiaoai_media/api/main.py` - 注册播单路由
- `backend/src/xiaoai_media/command_handler.py` - 添加播单语音命令支持
- `user_config.py` - 添加 `get_audio_url()` 示例函数

**API 端点：**
```
GET    /api/playlists              - 获取所有播单
POST   /api/playlists              - 创建播单
GET    /api/playlists/{id}         - 获取指定播单
PUT    /api/playlists/{id}         - 更新播单
DELETE /api/playlists/{id}         - 删除播单
POST   /api/playlists/{id}/items   - 添加播单项
DELETE /api/playlists/{id}/items/{index} - 删除播单项
POST   /api/playlists/{id}/play    - 播放播单
POST   /api/playlists/play-by-voice - 语音命令播放
```

### 前端

**新增文件：**
- `frontend/src/views/PlaylistManager.vue` - 播单管理界面

**更新文件：**
- `frontend/src/api/index.ts` - 添加播单管理 API 接口
- `frontend/src/router/index.ts` - 注册播单管理路由
- `frontend/src/App.vue` - 添加导航菜单项

### 数据存储

播单数据存储在：
```
~/.xiaoai-media/playlists.json
```

## 使用示例

### 示例 1：创建音乐播单（直接 URL）

1. 在"播单管理"页面点击"新建播单"
2. 填写：
   - 播单名称：我的音乐
   - 类型：music
   - 语音关键词：音乐、歌单
3. 点击"管理项目" → "添加项目"
4. 填写：
   - 标题：周杰伦 - 晴天
   - 播放 URL：https://example.com/music/sunny.mp3
   - 艺术家：周杰伦

### 示例 2：创建有声书播单（动态 URL）

1. 创建播单：
   - 播单名称：有声书
   - 类型：audiobook
   - 语音关键词：有声书、听书
2. 添加项目时，自定义参数填写：
```json
{
  "type": "audiobook",
  "book_id": "xiyouji",
  "chapter": "01"
}
```
3. 在 `user_config.py` 中实现：
```python
def get_audio_url(custom_params: dict) -> str:
    book_id = custom_params.get("book_id")
    chapter = custom_params.get("chapter")
    # 从您的音频服务获取 URL
    return f"https://audiobook.example.com/{book_id}/{chapter}.mp3"
```

### 示例 3：语音命令播放

启用对话监听后，对音箱说：
- "播放音乐播单" → 播放名为"我的音乐"的播单
- "播放有声书" → 播放名为"有声书"的播单

## 工作流程

```
用户创建播单
    ↓
添加播单项
    ↓
选择：直接URL 或 动态获取
    ↓
播放时自动代理URL
    ↓
发送到小爱音箱播放
```

## 配置说明

### user_config.py 配置

如果使用动态 URL 获取，需要实现 `get_audio_url()` 函数：

```python
def get_audio_url(custom_params: dict) -> str:
    """
    根据音频信息获取播放 URL
    
    Args:
        custom_params: 自定义参数字典
    
    Returns:
        播放 URL（原始 URL，不需要包装代理，系统会自动处理）
    """
    # 实现您的 URL 获取逻辑
    # ...
    return url
```

文件中已包含详细的示例实现。

### 语音命令配置

在播单设置中配置语音关键词：
- 关键词应具有一定的独特性，避免误触发
- 一个播单可以设置多个关键词
- 系统会自动匹配包含关键词的语音命令

## 兼容性

- 向后兼容：不影响现有功能
- 可选功能：不使用播单管理不会影响其他功能
- 数据独立：播单数据独立存储，不影响其他数据

## 测试验证

✅ 后端模块导入成功  
✅ 主应用路由注册成功（35个路由）  
✅ 前端代码编译无错误  
✅ API 接口完整实现  

## 后续改进建议

1. 添加播单导入/导出功能（JSON/M3U格式）
2. 支持播单排序和拖拽
3. 添加播放历史记录
4. 支持播单分享
5. 添加播单封面图片
6. 支持随机播放、循环播放等模式

## 文档

详细使用指南请参考：
- [docs/PLAYLIST_GUIDE.md](docs/PLAYLIST_GUIDE.md)

## 反馈

如有问题或建议，请提交 Issue 或 PR。
