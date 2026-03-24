# 播单批量导入功能

## 🎉 功能已完成

播单批量导入功能已完整实现，包括后端API和前端界面！

## ✨ 功能特性

- ✅ 自动检测运行环境（本地/Docker）
- ✅ 批量导入音频文件到播单
- ✅ 递归扫描子目录
- ✅ 多种音频格式支持
- ✅ 自动提取文件信息（标题、艺术家、专辑）
- ✅ 友好的图形界面
- ✅ 详细的导入统计

## 🚀 快速开始

### 方式1：使用测试脚本（推荐）

```bash
chmod +x test_batch_import.sh
./test_batch_import.sh
```

脚本会引导你完成整个流程。

### 方式2：使用前端界面

#### Docker环境

1. **配置目录挂载**

   编辑 `docker-compose.yml`：
   ```yaml
   volumes:
     - ./data:/data
     - /path/to/your/music:/data/music  # 添加这一行
   ```

2. **重启容器**
   ```bash
   docker-compose restart
   ```

3. **使用前端**
   - 打开浏览器访问前端
   - 进入"播单管理"页面
   - 选择播单，点击"项目"按钮
   - 点击"批量导入"按钮
   - 从下拉列表选择目录
   - 配置导入选项
   - 点击"开始导入"

#### 本地环境

1. **使用前端**
   - 打开浏览器访问前端
   - 进入"播单管理"页面
   - 选择播单，点击"项目"按钮
   - 点击"批量导入"按钮
   - 输入本地路径（如：`/Users/username/Music`）
   - 配置导入选项
   - 点击"开始导入"

### 方式3：使用API

```bash
# 1. 查看可用目录
curl http://localhost:8000/api/playlists/directories

# 2. 批量导入
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true,
    "file_extensions": [".mp3", ".flac", ".m4a"]
  }'
```

## 📖 文档

### 快速入门
- [中文快速指南](./播单批量导入功能说明.md) - 最快上手

### 详细文档
- [完整实现总结](./COMPLETE_IMPLEMENTATION_SUMMARY.md) - 全面了解
- [后端实现总结](./BATCH_IMPORT_SUMMARY.md) - 后端技术细节
- [前端实现总结](./FRONTEND_IMPLEMENTATION_SUMMARY.md) - 前端技术细节

### 使用指南
- [详细使用指南](./docs/playlist/BATCH_IMPORT_GUIDE.md) - API和使用说明
- [前端功能说明](./docs/playlist/FRONTEND_BATCH_IMPORT.md) - 前端界面说明

### 开发参考
- [前端集成示例](./docs/playlist/BATCH_IMPORT_FRONTEND_EXAMPLE.md) - Vue/React示例
- [更新日志](./docs/playlist/CHANGELOG_BATCH_IMPORT.md) - 详细变更记录
- [实现清单](./IMPLEMENTATION_CHECKLIST.md) - 开发清单

## 🎯 支持的音频格式

- MP3 (`.mp3`)
- M4A (`.m4a`)
- FLAC (`.flac`)
- WAV (`.wav`)
- OGG (`.ogg`)
- AAC (`.aac`)
- WMA (`.wma`)

## 📁 目录结构示例

```
/data/music/
├── 周杰伦/
│   ├── 叶惠美/
│   │   ├── 以父之名.mp3  → 标题: 以父之名, 艺术家: 周杰伦, 专辑: 叶惠美
│   │   └── 晴天.mp3
│   └── 范特西/
│       └── 双截棍.mp3
└── 林俊杰/
    └── 江南.mp3
```

## 🎨 界面预览

### Docker模式
```
┌──────────────────────────────────────┐
│ 批量导入音频文件                      │
├──────────────────────────────────────┤
│ ℹ️ Docker模式                         │
│ 从挂载的volume中选择目录              │
│                                      │
│ 选择目录: [music ▼]                  │
│ ☑ 递归扫描子目录                     │
│ ☑ MP3  ☑ M4A  ☑ FLAC                │
│                                      │
│ ✅ 导入完成                           │
│ ✅ 成功导入：50 个文件                │
│ 📁 扫描总数：100 个文件               │
│                                      │
│          [关闭]  [开始导入]          │
└──────────────────────────────────────┘
```

## 🔧 技术栈

### 后端
- Python 3.11
- FastAPI
- Pydantic

### 前端
- Vue 3
- TypeScript
- Element Plus

## 📊 文件变更

### 后端代码
- `backend/src/xiaoai_media/services/playlist_models.py` (+15行)
- `backend/src/xiaoai_media/services/playlist_service.py` (+120行)
- `backend/src/xiaoai_media/api/routes/playlist.py` (+50行)
- `backend/src/xiaoai_media/services/__init__.py` (+2行)

### 前端代码
- `frontend/src/api/index.ts` (+40行)
- `frontend/src/views/PlaylistManager.vue` (+180行)

### 配置文件
- `docker-compose.yml` (+3行)

### 文档
- 8个新文档，约3100行

## ✅ 验证状态

- [x] 后端代码语法检查通过
- [x] 前端代码编译成功
- [x] API接口定义完整
- [x] 文档齐全
- [ ] 实际环境测试（待进行）

## 🐛 故障排除

### 问题1：Docker模式下找不到目录

**解决方法：**
1. 检查 `docker-compose.yml` 中的 volume 配置
2. 重启容器：`docker-compose restart`
3. 使用API查看可用目录：`curl http://localhost:8000/api/playlists/directories`

### 问题2：没有文件被导入

**可能原因：**
- 文件格式不匹配
- 目录为空
- 没有开启递归扫描

**解决方法：**
- 检查文件扩展名
- 勾选"递归扫描子目录"
- 查看导入结果中的统计信息

### 问题3：权限错误

**解决方法：**
- 检查目录权限
- Docker环境：确保挂载的目录有读取权限

## 🎓 使用示例

### 完整示例脚本

```bash
#!/bin/bash

# 1. 创建播单
PLAYLIST_ID=$(curl -s -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的音乐收藏",
    "type": "music",
    "voice_keywords": ["音乐", "歌曲"]
  }' | jq -r '.id')

echo "播单ID: $PLAYLIST_ID"

# 2. 批量导入
curl -X POST "http://localhost:8000/api/playlists/$PLAYLIST_ID/import" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/data/music",
    "recursive": true,
    "file_extensions": [".mp3", ".flac", ".m4a"]
  }' | jq

# 3. 查看播单
curl -s "http://localhost:8000/api/playlists/$PLAYLIST_ID" | jq

# 4. 播放
curl -X POST "http://localhost:8000/api/playlists/$PLAYLIST_ID/play" \
  -H "Content-Type: application/json" \
  -d '{
    "start_index": 0,
    "announce": true
  }' | jq
```

## 🔄 后续改进计划

### 短期
- [ ] 添加单元测试
- [ ] 实际环境验证
- [ ] 性能优化

### 中期
- [ ] ID3标签读取
- [ ] 封面图片提取
- [ ] WebSocket实时进度

### 长期
- [ ] 重复文件检测
- [ ] 批量元信息编辑
- [ ] 音乐库管理

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

与主项目保持一致

---

**开始使用吧！** 🎵

如有问题，请查看详细文档或提交Issue。
