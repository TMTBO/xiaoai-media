# 播单批量导入功能 - 实现总结

## 功能说明

为播单管理系统添加了批量导入功能，支持从指定目录批量导入音频文件到播单中。该功能自动适配本地和Docker环境，提供灵活的文件扫描和导入选项。

## 核心特性

✅ **环境自适应**
- 自动检测本地/Docker环境
- 本地模式：支持任意文件系统路径
- Docker模式：从挂载的volume中选择目录

✅ **灵活的扫描选项**
- 支持递归/非递归扫描
- 可自定义文件扩展名过滤
- 默认支持7种常见音频格式

✅ **智能信息提取**
- 从文件名提取标题
- 从目录结构提取艺术家和专辑
- 保存完整的文件元数据

## 新增API

### 1. GET /api/playlists/directories
获取可用的目录列表（主要用于Docker环境）

### 2. POST /api/playlists/{playlist_id}/import
从指定目录批量导入音频文件

## 文件变更

### 后端代码

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `backend/src/xiaoai_media/services/playlist_models.py` | 修改 | 新增 `ImportFromDirectoryRequest` 模型 |
| `backend/src/xiaoai_media/services/playlist_service.py` | 修改 | 新增3个方法：环境检测、目录列表、批量导入 |
| `backend/src/xiaoai_media/api/routes/playlist.py` | 修改 | 新增2个路由端点 |
| `backend/src/xiaoai_media/services/__init__.py` | 修改 | 导出新增的请求模型 |

### 配置文件

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `docker-compose.yml` | 修改 | 添加音乐目录挂载示例 |

### 文档

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `docs/playlist/BATCH_IMPORT_GUIDE.md` | 新增 | 详细使用指南 |
| `docs/playlist/BATCH_IMPORT_README.md` | 新增 | 功能说明文档 |
| `docs/playlist/BATCH_IMPORT_FRONTEND_EXAMPLE.md` | 新增 | 前端集成示例（Vue3/React） |
| `docs/playlist/CHANGELOG_BATCH_IMPORT.md` | 新增 | 详细更新日志 |

### 测试工具

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `test_batch_import.sh` | 新增 | 自动化测试脚本 |

## 快速开始

### Docker环境

```bash
# 1. 配置 docker-compose.yml
volumes:
  - ./data:/data
  - /path/to/your/music:/data/music

# 2. 重启容器
docker-compose restart

# 3. 查看可用目录
curl http://localhost:8000/api/playlists/directories

# 4. 创建播单并导入
PLAYLIST_ID=$(curl -s -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{"name": "我的音乐", "type": "music"}' | jq -r '.id')

curl -X POST "http://localhost:8000/api/playlists/$PLAYLIST_ID/import" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true
  }'
```

### 本地环境

```bash
# 直接使用本地路径
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/username/Music",
    "recursive": true
  }'
```

## 使用测试脚本

```bash
chmod +x test_batch_import.sh
./test_batch_import.sh
```

脚本会引导你完成：
1. 环境检测
2. 目录选择
3. 播单创建
4. 文件导入
5. 结果验证

## API示例

### 请求

```bash
POST /api/playlists/{playlist_id}/import
Content-Type: application/json

{
  "directory": "/data/music",
  "recursive": true,
  "file_extensions": [".mp3", ".flac", ".m4a"]
}
```

### 响应

```json
{
  "imported": 50,
  "skipped": 2,
  "total_scanned": 100,
  "skipped_files": ["file1.txt", "file2.log"],
  "playlist_total_items": 50
}
```

## 支持的音频格式

- `.mp3` - MP3音频
- `.m4a` - AAC/ALAC音频
- `.flac` - FLAC无损音频
- `.wav` - WAV波形音频
- `.ogg` - Ogg Vorbis
- `.aac` - AAC音频
- `.wma` - Windows Media Audio

## 目录结构示例

```
/data/music/
├── 周杰伦/
│   ├── 叶惠美/
│   │   ├── 以父之名.mp3      # title: 以父之名, artist: 周杰伦, album: 叶惠美
│   │   └── 晴天.mp3
│   └── 范特西/
│       └── 双截棍.mp3
└── 林俊杰/
    └── 江南.mp3
```

## 前端集成

提供了完整的Vue 3和React组件示例，包括：
- 环境检测和显示
- Docker模式的目录选择器
- 本地模式的文件输入
- 导入选项配置
- 进度显示
- 结果展示

详见：`docs/playlist/BATCH_IMPORT_FRONTEND_EXAMPLE.md`

## 注意事项

1. **Docker环境**
   - 必须先在 docker-compose.yml 中配置volume挂载
   - 修改配置后需要重启容器
   - 建议挂载到 `/data` 的子目录

2. **文件权限**
   - 确保应用有读取目录的权限
   - Docker环境注意文件所有权

3. **性能考虑**
   - 大量文件导入可能耗时较长
   - 建议分批导入或使用非递归模式

4. **文件路径**
   - 导入的文件使用 `file://` 协议
   - 播放设备需要能访问该路径

## 后续改进建议

- [ ] 使用mutagen库读取ID3标签
- [ ] 提取封面图片和音频时长
- [ ] WebSocket实时进度反馈
- [ ] 导入前预览功能
- [ ] 重复文件检测和去重
- [ ] 批量元信息编辑

## 相关文档

- [详细使用指南](docs/playlist/BATCH_IMPORT_GUIDE.md)
- [前端集成示例](docs/playlist/BATCH_IMPORT_FRONTEND_EXAMPLE.md)
- [更新日志](docs/playlist/CHANGELOG_BATCH_IMPORT.md)
- [播单功能指南](docs/playlist/PLAYLIST_GUIDE.md)

## 验证清单

- [x] 后端API实现
- [x] 环境检测逻辑
- [x] 目录列表功能
- [x] 批量导入功能
- [x] 元信息提取
- [x] 错误处理
- [x] API文档
- [x] 使用指南
- [x] 前端示例
- [x] 测试脚本
- [x] Docker配置示例

## 测试建议

1. **本地环境测试**
   - 创建测试播单
   - 准备测试音频文件
   - 测试非递归导入
   - 测试递归导入
   - 验证元信息提取

2. **Docker环境测试**
   - 配置volume挂载
   - 重启容器
   - 测试目录列表API
   - 测试批量导入
   - 验证文件路径正确性

3. **边界情况测试**
   - 空目录
   - 不存在的目录
   - 无权限的目录
   - 大量文件（>1000）
   - 深层嵌套目录

## 完成状态

✅ 功能已完整实现并通过语法检查
✅ 文档已完善
✅ 测试工具已提供
✅ 前端集成示例已提供

可以开始测试和使用了！
