# 播单批量导入功能 - 更新日志

## 版本信息

- **功能名称**: 播单批量导入
- **开发日期**: 2024-03-24
- **状态**: ✅ 已完成

## 功能概述

为播单管理系统添加批量导入功能，支持从指定目录批量导入音频文件，自动适配本地和Docker环境。

## 新增功能

### 1. 环境自动检测

- 自动识别运行环境（本地/Docker）
- 根据环境提供不同的目录选择方式
- 检测逻辑：
  - 检查 `/.dockerenv` 文件
  - 检查 `HOME` 环境变量是否为 `/data`

### 2. 目录列表API

**端点**: `GET /api/playlists/directories`

**功能**:
- 本地模式：返回提示信息，引导使用文件选择器
- Docker模式：列出 `/data` 下的所有可用目录

**响应示例**:
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
    }
  ],
  "is_docker": true,
  "message": "Docker模式：从列表中选择目录"
}
```

### 3. 批量导入API

**端点**: `POST /api/playlists/{playlist_id}/import`

**功能**:
- 扫描指定目录下的音频文件
- 支持递归扫描子目录
- 可自定义文件扩展名过滤
- 自动提取文件元信息

**请求参数**:
```json
{
  "directory": "/data/music",
  "recursive": true,
  "file_extensions": [".mp3", ".flac", ".m4a"]
}
```

**响应示例**:
```json
{
  "imported": 50,
  "skipped": 2,
  "total_scanned": 100,
  "skipped_files": ["file1.txt", "file2.log"],
  "playlist_total_items": 50
}
```

### 4. 智能元信息提取

从文件路径自动提取：
- **标题**: 文件名（去除扩展名）
- **艺术家**: 祖父目录名
- **专辑**: 父目录名

**示例**:
```
/data/music/周杰伦/叶惠美/以父之名.mp3
↓
title: "以父之名"
artist: "周杰伦"
album: "叶惠美"
```

### 5. 文件元数据保存

每个导入的文件保存以下信息：
```json
{
  "title": "歌曲名",
  "artist": "艺术家",
  "album": "专辑",
  "url": "file:///data/music/song.mp3",
  "custom_params": {
    "file_path": "/data/music/song.mp3",
    "file_size": 5242880,
    "file_extension": ".mp3"
  }
}
```

## 代码变更

### 新增文件

| 文件 | 说明 |
|------|------|
| `docs/playlist/BATCH_IMPORT_GUIDE.md` | 详细使用指南 |
| `docs/playlist/BATCH_IMPORT_README.md` | 功能说明文档 |
| `docs/playlist/BATCH_IMPORT_FRONTEND_EXAMPLE.md` | 前端集成示例 |
| `docs/playlist/CHANGELOG_BATCH_IMPORT.md` | 本更新日志 |
| `test_batch_import.sh` | 功能测试脚本 |

### 修改文件

#### 1. `backend/src/xiaoai_media/services/playlist_models.py`

**变更**:
- 新增 `ImportFromDirectoryRequest` 数据模型

**代码**:
```python
class ImportFromDirectoryRequest(BaseModel):
    """从目录批量导入请求"""
    directory: str = Field(..., description="要导入的目录路径")
    recursive: bool = Field(False, description="是否递归扫描子目录")
    file_extensions: list[str] = Field(
        default_factory=lambda: [".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac"],
        description="要导入的文件扩展名列表"
    )
```

#### 2. `backend/src/xiaoai_media/services/playlist_service.py`

**变更**:
- 新增 `is_docker_environment()` 方法
- 新增 `list_available_directories()` 方法
- 新增 `import_from_directory()` 方法

**新增方法**:

```python
@staticmethod
def is_docker_environment() -> bool:
    """判断是否在Docker环境中运行"""
    
@staticmethod
def list_available_directories() -> list[dict[str, str]]:
    """列出可用的目录（主要用于Docker环境）"""
    
@staticmethod
def import_from_directory(
    playlist_id: str,
    directory: str,
    recursive: bool = False,
    file_extensions: list[str] | None = None
) -> dict[str, any]:
    """从指定目录批量导入音频文件"""
```

#### 3. `backend/src/xiaoai_media/api/routes/playlist.py`

**变更**:
- 导入 `ImportFromDirectoryRequest`
- 新增 `GET /directories` 路由
- 新增 `POST /{playlist_id}/import` 路由

**新增路由**:

```python
@router.get("/directories")
async def list_directories():
    """列出可用的目录"""

@router.post("/{playlist_id}/import")
async def import_from_directory(playlist_id: str, req: ImportFromDirectoryRequest):
    """从指定目录批量导入音频文件"""
```

#### 4. `backend/src/xiaoai_media/services/__init__.py`

**变更**:
- 导出 `ImportFromDirectoryRequest`

#### 5. `docker-compose.yml`

**变更**:
- 添加音乐目录挂载示例注释

```yaml
volumes:
  - ./data:/data
  # 音乐目录挂载（可选）
  # - /path/to/your/music:/data/music
```

## 支持的音频格式

默认支持以下格式：
- `.mp3` - MP3
- `.m4a` - AAC/ALAC
- `.flac` - FLAC无损
- `.wav` - WAV
- `.ogg` - Ogg Vorbis
- `.aac` - AAC
- `.wma` - Windows Media Audio

可通过 `file_extensions` 参数自定义。

## 使用场景

### 场景1：本地开发环境

```bash
# 直接使用本地路径
curl -X POST http://localhost:8000/api/playlists/{id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/username/Music/周杰伦",
    "recursive": true
  }'
```

### 场景2：Docker生产环境

```bash
# 1. 配置 docker-compose.yml
volumes:
  - /mnt/nas/music:/data/music

# 2. 重启容器
docker-compose restart

# 3. 导入
curl -X POST http://localhost:8000/api/playlists/{id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true
  }'
```

### 场景3：有声书导入

```bash
# 目录结构：/data/audiobooks/书名/章节.mp3
curl -X POST http://localhost:8000/api/playlists/{id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/audiobooks/三体",
    "recursive": true,
    "file_extensions": [".mp3", ".m4a"]
  }'
```

## 测试

### 自动化测试脚本

```bash
chmod +x test_batch_import.sh
./test_batch_import.sh
```

### 手动测试步骤

1. **创建测试播单**
   ```bash
   curl -X POST http://localhost:8000/api/playlists \
     -H "Content-Type: application/json" \
     -d '{"name": "测试", "type": "music"}'
   ```

2. **查看可用目录**
   ```bash
   curl http://localhost:8000/api/playlists/directories
   ```

3. **执行导入**
   ```bash
   curl -X POST http://localhost:8000/api/playlists/{id}/import \
     -H "Content-Type: application/json" \
     -d '{"directory": "/data/music", "recursive": true}'
   ```

4. **验证结果**
   ```bash
   curl http://localhost:8000/api/playlists/{id}
   ```

## 性能考虑

### 扫描性能

- 非递归模式：快速，适合单层目录
- 递归模式：较慢，适合深层目录结构
- 建议：大量文件时分批导入

### 内存使用

- 文件列表在内存中构建
- 大目录（>10000文件）可能占用较多内存
- 建议：使用目录过滤或分批导入

## 已知限制

1. **文件协议**
   - 使用 `file://` 协议
   - 播放设备需要能访问该路径
   - Docker环境中路径在容器内部

2. **元信息提取**
   - 仅从文件路径提取
   - 不读取ID3标签
   - 未来可增强

3. **进度反馈**
   - 当前为同步操作
   - 大量文件时无实时进度
   - 未来可添加WebSocket支持

4. **重复检测**
   - 不检测重复文件
   - 可能导入相同文件多次
   - 未来可添加去重逻辑

## 后续改进计划

### 短期（v1.1）

- [ ] 添加ID3标签读取（使用mutagen库）
- [ ] 支持封面图片提取
- [ ] 添加文件时长信息

### 中期（v1.2）

- [ ] WebSocket实时进度反馈
- [ ] 导入前预览功能
- [ ] 重复文件检测

### 长期（v2.0）

- [ ] 批量元信息编辑
- [ ] 自动分类和标签
- [ ] 音乐库管理功能

## 相关文档

- [详细使用指南](./BATCH_IMPORT_GUIDE.md)
- [前端集成示例](./BATCH_IMPORT_FRONTEND_EXAMPLE.md)
- [播单功能指南](./PLAYLIST_GUIDE.md)
- [API参考文档](../api/API_REFERENCE.md)
- [Docker部署指南](../deployment/DOCKER_GUIDE.md)

## 贡献者

- 开发：AI Assistant
- 测试：待补充
- 文档：AI Assistant

## 反馈

如有问题或建议，请提交Issue或Pull Request。
