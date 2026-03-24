# 播单批量导入功能

## 新增功能

为播单管理添加了批量导入功能，支持从指定目录批量导入音频文件。

### 主要特性

1. **环境自适应**
   - 自动检测运行环境（本地/Docker）
   - 本地模式：支持任意文件系统路径
   - Docker模式：从挂载的volume中选择目录

2. **灵活的扫描选项**
   - 支持递归扫描子目录
   - 可自定义文件扩展名过滤
   - 自动提取文件元信息（标题、艺术家、专辑）

3. **智能信息提取**
   - 从文件名提取标题
   - 从目录结构提取艺术家和专辑信息
   - 保存文件路径和元数据

## 新增API端点

### 1. GET /api/playlists/directories

获取可用的目录列表（主要用于Docker环境）。

### 2. POST /api/playlists/{playlist_id}/import

从指定目录批量导入音频文件到播单。

## 代码变更

### 新增文件

- `docs/playlist/BATCH_IMPORT_GUIDE.md` - 详细使用指南
- `test_batch_import.sh` - 功能测试脚本

### 修改文件

1. **backend/src/xiaoai_media/services/playlist_models.py**
   - 新增 `ImportFromDirectoryRequest` 模型

2. **backend/src/xiaoai_media/services/playlist_service.py**
   - 新增 `is_docker_environment()` - 检测运行环境
   - 新增 `list_available_directories()` - 列出可用目录
   - 新增 `import_from_directory()` - 批量导入功能

3. **backend/src/xiaoai_media/api/routes/playlist.py**
   - 新增 `GET /directories` 路由
   - 新增 `POST /{playlist_id}/import` 路由

4. **backend/src/xiaoai_media/services/__init__.py**
   - 导出 `ImportFromDirectoryRequest`

5. **docker-compose.yml**
   - 添加音乐目录挂载示例

## 使用示例

### Docker环境

```bash
# 1. 配置 docker-compose.yml
volumes:
  - ./data:/data
  - /path/to/music:/data/music

# 2. 重启容器
docker-compose restart

# 3. 查看可用目录
curl http://localhost:8000/api/playlists/directories

# 4. 导入文件
curl -X POST http://localhost:8000/api/playlists/{id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true
  }'
```

### 本地环境

```bash
# 直接使用本地路径
curl -X POST http://localhost:8000/api/playlists/{id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/username/Music",
    "recursive": true
  }'
```

## 测试

运行测试脚本：

```bash
./test_batch_import.sh
```

脚本会：
1. 检测运行环境
2. 显示可用目录
3. 创建测试播单
4. 提示输入目录路径
5. 执行导入并显示结果

## 技术细节

### 环境检测

通过以下方式判断是否在Docker环境：
1. 检查 `/.dockerenv` 文件是否存在
2. 检查 `HOME` 环境变量是否为 `/data`

### 文件信息提取

假设目录结构为：`艺术家/专辑/歌曲.mp3`

```python
# 示例：/data/music/周杰伦/叶惠美/以父之名.mp3
title = "以父之名"      # 文件名（去除扩展名）
artist = "周杰伦"       # 祖父目录
album = "叶惠美"        # 父目录
```

### 文件URL格式

导入的文件使用 `file://` 协议：

```json
{
  "title": "歌曲名",
  "url": "file:///data/music/song.mp3",
  "custom_params": {
    "file_path": "/data/music/song.mp3",
    "file_size": 5242880,
    "file_extension": ".mp3"
  }
}
```

## 注意事项

1. **Docker挂载**
   - 必须在 docker-compose.yml 中配置volume
   - 修改配置后需要重启容器
   - 建议挂载到 `/data` 的子目录

2. **文件权限**
   - 确保应用有读取目录的权限
   - Docker环境中注意文件所有权

3. **性能考虑**
   - 大量文件导入可能耗时较长
   - 建议分批导入或使用非递归模式

4. **文件播放**
   - 本地文件使用 `file://` 协议
   - 需要确保播放设备能访问该路径
   - Docker环境中文件在容器内部

## 后续改进建议

1. **元数据提取增强**
   - 使用 mutagen 等库读取ID3标签
   - 提取更多元信息（时长、比特率等）

2. **进度反馈**
   - 添加WebSocket支持实时进度
   - 大文件导入时显示进度条

3. **文件预览**
   - 导入前预览将要导入的文件列表
   - 支持选择性导入

4. **重复检测**
   - 检测已存在的文件
   - 提供跳过或覆盖选项

5. **批量编辑**
   - 导入后批量修改元信息
   - 批量设置封面图片

## 相关文档

- [详细使用指南](./BATCH_IMPORT_GUIDE.md)
- [播单功能指南](./PLAYLIST_GUIDE.md)
- [API参考文档](../api/API_REFERENCE.md)
