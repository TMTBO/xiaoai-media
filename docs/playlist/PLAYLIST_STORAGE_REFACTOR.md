# 播单存储结构重构

## 概述

将播单存储从单文件格式重构为多文件格式，提高性能和可维护性。

## 变更内容

### 1. 存储结构变更

#### 旧格式（单文件）
```
playlists.json  # 包含所有播单的完整数据
```

#### 新格式（多文件）
```
playlists/
├── index.json           # 播单索引文件（所有播单的基本信息）
├── {playlist_id_1}.json # 播单1的详细数据
├── {playlist_id_2}.json # 播单2的详细数据
└── ...
```

### 2. 数据结构变更

#### 播单索引 (index.json)
```json
{
  "playlist_id": {
    "id": "播单ID",
    "name": "播单名称",
    "type": "播单类型",
    "description": "描述",
    "voice_keywords": ["关键词1", "关键词2"],
    "item_count": 10,
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
}
```

#### 播单详细数据 ({playlist_id}.json)
```json
[
  {
    "title": "歌曲名",
    "artist": "艺术家",
    "album": "专辑名",
    "audio_id": "音频ID",
    "url": "音频URL（可选）",
    "custom_params": {}
  }
]
```

### 3. 播单项字段精简

移除了不必要的字段，只保留核心信息：

**保留字段：**
- `title`: 歌曲名
- `artist`: 艺术家
- `album`: 专辑名
- `audio_id`: 音频ID
- `url`: 音频URL（可选）
- `custom_params`: 自定义参数

**移除字段：**
- `duration`: 时长（不影响播放）
- `cover_url`: 封面URL（不影响播放）

## 优势

### 1. 性能优化
- **按需加载**：列表页面只加载索引信息，不加载完整数据
- **减少内存占用**：不需要一次性加载所有播单的完整数据
- **加快响应速度**：索引文件更小，读取更快

### 2. 语音播放优化
- **快速匹配**：从索引文件中匹配唤醒词，无需加载完整数据
- **延迟加载**：只在需要播放时才加载对应播单的详细数据

### 3. 可维护性
- **独立管理**：每个播单的数据独立存储，便于备份和恢复
- **减少冲突**：多个操作不会同时修改同一个文件
- **易于扩展**：可以方便地添加新的播单相关功能

## API 变更

### 后端 API

#### 列表接口返回类型变更
```python
# 旧版本：返回完整播单数据
GET /api/playlists
Response: { playlists: Playlist[] }

# 新版本：返回索引信息
GET /api/playlists
Response: { playlists: PlaylistIndex[] }
```

#### 其他接口保持兼容
- `GET /api/playlists/{id}`: 返回完整播单数据（按需加载）
- `POST /api/playlists`: 创建播单
- `PUT /api/playlists/{id}`: 更新播单
- `DELETE /api/playlists/{id}`: 删除播单
- `POST /api/playlists/{id}/items`: 添加播单项
- `DELETE /api/playlists/{id}/items/{index}`: 删除播单项
- `POST /api/playlists/{id}/play`: 播放播单
- `POST /api/playlists/play-by-voice`: 语音播放

### 前端 API

#### 类型定义更新
```typescript
// 新增：播单索引类型
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

// 播单项类型精简
interface PlaylistItem {
  title: string       // 歌曲名
  artist: string      // 艺术家
  album: string       // 专辑名
  audio_id: string    // 音频ID
  url?: string        // 音频URL
  custom_params: Record<string, any>
}
```

## 数据迁移

### 自动迁移脚本

提供了自动迁移脚本 `scripts/migrate_playlists.py`：

```bash
# 运行迁移脚本
python scripts/migrate_playlists.py
```

脚本功能：
1. 读取旧的 `playlists.json` 文件
2. 创建新的 `playlists/` 目录
3. 生成索引文件 `playlists/index.json`
4. 为每个播单创建独立的数据文件
5. 备份旧文件为 `playlists.json.backup`

### 手动迁移

如果需要手动迁移：

1. 创建 `playlists/` 目录
2. 从旧文件中提取索引信息，保存到 `playlists/index.json`
3. 为每个播单创建独立的 JSON 文件
4. 备份或删除旧的 `playlists.json` 文件

## 前端 UI 更新

### 播单列表页面
- 显示 `item_count` 而不是 `items.length`
- 点击"项目"按钮时才加载完整播单数据

### 播单项表单
- 移除"时长"和"封面URL"字段
- 添加"音频ID"字段
- 简化表单，只保留必要信息

## 向后兼容性

### 数据兼容
- 旧的 `playlists.json` 文件会被自动迁移
- 迁移后旧文件会被备份，不会丢失数据

### API 兼容
- 所有现有 API 端点保持不变
- 只有列表接口的返回类型发生变化
- 前端已同步更新，保持兼容

## 注意事项

1. **首次启动**：如果存在旧的 `playlists.json`，建议运行迁移脚本
2. **备份数据**：迁移前建议备份 `playlists.json` 文件
3. **权限检查**：确保 `playlists/` 目录有读写权限
4. **Docker 环境**：数据目录为 `/data/playlists/`

## 测试建议

### 后端测试
```bash
# 测试播单列表
curl http://localhost:8000/api/playlists

# 测试获取单个播单
curl http://localhost:8000/api/playlists/{playlist_id}

# 测试语音播放
curl -X POST http://localhost:8000/api/playlists/play-by-voice \
  -H "Content-Type: application/json" \
  -d '{"voice_text": "播放音乐"}'
```

### 前端测试
1. 访问播单管理页面
2. 检查播单列表是否正常显示
3. 点击"项目"按钮，检查是否能正常加载播单详情
4. 测试创建、编辑、删除播单功能
5. 测试添加、删除播单项功能
6. 测试播放功能

## 相关文件

### 后端
- `backend/src/xiaoai_media/api/routes/playlist.py`: 播单路由（已更新）
- `backend/src/xiaoai_media/config.py`: 配置文件（无需修改）

### 前端
- `frontend/src/api/index.ts`: API 类型定义（已更新）
- `frontend/src/views/PlaylistManager.vue`: 播单管理页面（已更新）

### 脚本
- `scripts/migrate_playlists.py`: 数据迁移脚本（新增）

### 文档
- `docs/playlist/PLAYLIST_STORAGE_REFACTOR.md`: 本文档（新增）
