# 播单批量导入功能使用指南

## 功能概述

播单批量导入功能允许你从指定目录批量导入音频文件到播单中，支持本地模式和Docker模式。

## 支持的音频格式

- `.mp3` - MP3音频
- `.m4a` - AAC音频
- `.flac` - 无损音频
- `.wav` - 波形音频
- `.ogg` - Ogg Vorbis
- `.aac` - AAC音频
- `.wma` - Windows Media Audio

## 使用方式

### 1. 本地模式

在本地开发环境中，你可以直接使用本地文件系统的路径。

#### API调用示例

```bash
# 1. 创建播单
curl -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的音乐",
    "type": "music",
    "description": "从本地导入的音乐"
  }'

# 2. 从目录导入（非递归）
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/username/Music",
    "recursive": false
  }'

# 3. 从目录导入（递归扫描子目录）
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/username/Music",
    "recursive": true,
    "file_extensions": [".mp3", ".flac"]
  }'
```

### 2. Docker模式

在Docker环境中，需要先通过volume挂载本地目录到容器中。

#### 步骤1：配置volume挂载

编辑 `docker-compose.yml`：

```yaml
services:
  xiaoai-media:
    volumes:
      - ./data:/data
      # 挂载你的音乐目录
      - /path/to/your/music:/data/music
      # 可以挂载多个目录
      - /path/to/audiobooks:/data/audiobooks
      - /path/to/podcasts:/data/podcasts
```

#### 步骤2：重启容器

```bash
docker-compose down
docker-compose up -d
```

#### 步骤3：查看可用目录

```bash
curl http://localhost:8000/api/playlists/directories
```

响应示例：
```json
{
  "directories": [
    {
      "path": "/data",
      "name": "数据根目录 (/data)",
      "is_docker": true
    },
    {
      "path": "/data/music",
      "name": "music",
      "is_docker": true
    },
    {
      "path": "/data/audiobooks",
      "name": "audiobooks",
      "is_docker": true
    }
  ],
  "is_docker": true,
  "message": "Docker模式：从列表中选择目录"
}
```

#### 步骤4：导入文件

```bash
# 从挂载的目录导入
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true
  }'
```

## API参考

### GET /api/playlists/directories

获取可用的目录列表。

**响应：**
```json
{
  "directories": [
    {
      "path": "目录路径",
      "name": "目录名称",
      "is_docker": true/false
    }
  ],
  "is_docker": true/false,
  "message": "提示信息"
}
```

### POST /api/playlists/{playlist_id}/import

从指定目录批量导入音频文件。

**请求参数：**
```json
{
  "directory": "目录路径（必填）",
  "recursive": false,  // 是否递归扫描子目录（可选，默认false）
  "file_extensions": [".mp3", ".flac"]  // 文件扩展名列表（可选）
}
```

**响应：**
```json
{
  "imported": 50,           // 成功导入的文件数
  "skipped": 2,             // 跳过的文件数
  "total_scanned": 100,     // 扫描的总文件数
  "skipped_files": [],      // 跳过的文件列表（最多10个）
  "playlist_total_items": 50 // 播单中的总项目数
}
```

## 文件信息提取

导入时会自动提取以下信息：

1. **标题（title）**：文件名（去除扩展名）
2. **艺术家（artist）**：从目录结构提取（祖父目录）
3. **专辑（album）**：从目录结构提取（父目录）

### 目录结构示例

```
/data/music/
├── 周杰伦/
│   ├── 叶惠美/
│   │   ├── 以父之名.mp3      # artist: 周杰伦, album: 叶惠美
│   │   └── 晴天.mp3
│   └── 范特西/
│       └── 双截棍.mp3
└── 林俊杰/
    └── 江南.mp3              # artist: 林俊杰, album: (空)
```

## 注意事项

1. **文件路径**：导入的文件使用 `file://` 协议存储绝对路径
2. **权限问题**：确保应用有读取目录的权限
3. **Docker挂载**：
   - 必须先挂载目录到容器中才能访问
   - 建议挂载到 `/data` 的子目录下
   - 重启容器后挂载才会生效
4. **大量文件**：导入大量文件可能需要较长时间，建议分批导入
5. **文件格式**：只会导入指定扩展名的文件，其他文件会被跳过

## 前端集成建议

### 本地模式

使用HTML5的文件选择器：

```html
<input type="file" webkitdirectory directory multiple />
```

或使用Electron的对话框API：

```javascript
const { dialog } = require('electron');
const result = await dialog.showOpenDialog({
  properties: ['openDirectory']
});
```

### Docker模式

1. 先调用 `/api/playlists/directories` 获取可用目录
2. 显示目录列表供用户选择
3. 用户选择后调用导入API

```javascript
// 获取目录列表
const { directories, is_docker } = await fetch('/api/playlists/directories').then(r => r.json());

if (is_docker) {
  // Docker模式：显示目录选择器
  showDirectorySelector(directories);
} else {
  // 本地模式：使用文件选择器
  showFileSelector();
}
```

## 故障排除

### 问题1：找不到目录

**错误：** `Directory not found: /data/music`

**解决：**
- 检查docker-compose.yml中的volume配置
- 确保已重启容器
- 使用 `/api/playlists/directories` 查看实际可用的目录

### 问题2：没有文件被导入

**可能原因：**
- 文件扩展名不匹配
- 目录为空
- 没有开启递归扫描但文件在子目录中

**解决：**
- 检查 `file_extensions` 参数
- 设置 `recursive: true` 扫描子目录
- 查看响应中的 `total_scanned` 确认扫描了多少文件

### 问题3：权限错误

**错误：** `Permission denied`

**解决：**
- 检查目录权限
- Docker环境：确保挂载的目录有读取权限
- 本地环境：确保应用进程有访问权限

## 完整示例

```bash
#!/bin/bash

# 1. 创建播单
PLAYLIST_ID=$(curl -s -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的音乐收藏",
    "type": "music",
    "description": "从本地导入",
    "voice_keywords": ["音乐", "歌曲"]
  }' | jq -r '.id')

echo "Created playlist: $PLAYLIST_ID"

# 2. 导入文件
curl -X POST "http://localhost:8000/api/playlists/$PLAYLIST_ID/import" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true,
    "file_extensions": [".mp3", ".flac", ".m4a"]
  }' | jq

# 3. 查看播单
curl -s "http://localhost:8000/api/playlists/$PLAYLIST_ID" | jq

# 4. 播放播单
curl -X POST "http://localhost:8000/api/playlists/$PLAYLIST_ID/play" \
  -H "Content-Type: application/json" \
  -d '{
    "start_index": 0,
    "announce": true
  }' | jq
```

## 相关文档

- [播单功能指南](./PLAYLIST_GUIDE.md)
- [Docker部署指南](../deployment/DOCKER_GUIDE.md)
- [API参考文档](../api/API_REFERENCE.md)
