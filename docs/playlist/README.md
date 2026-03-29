# 播放列表功能文档

XiaoAI Media 播放列表功能的完整文档。

## 📚 文档列表

- **[PLAYLIST_GUIDE.md](PLAYLIST_GUIDE.md)** - 播放列表完整使用指南
  - 播放列表的创建和管理
  - 语音命令控制
  - 自定义音频源集成

- **[PLAYLIST_STORAGE_REFACTOR.md](PLAYLIST_STORAGE_REFACTOR.md)** - 存储结构重构说明
  - 多文件存储格式
  - 性能优化
  - 数据迁移指南

- **[PLAYLIST_REFACTOR_SUMMARY.md](PLAYLIST_REFACTOR_SUMMARY.md)** - 重构完成总结
  - 已完成的工作
  - 性能优化效果
  - 使用说明

- **[CHANGELOG_PLAYLIST_REFACTOR.md](CHANGELOG_PLAYLIST_REFACTOR.md)** - 重构更新日志
  - 版本变更记录
  - 破坏性变更说明
  - 向后兼容性

- **[REFACTOR_CHECKLIST.md](REFACTOR_CHECKLIST.md)** - 重构检查清单
  - 代码变更清单
  - 部署步骤
  - 验证清单

- **[PLAYLIST_FEATURE_UPDATE.md](PLAYLIST_FEATURE_UPDATE.md)** - 功能更新说明
  - 最新功能介绍
  - API 变更说明

- **[PLAYLIST_IMPROVEMENTS.md](PLAYLIST_IMPROVEMENTS.md)** - 功能改进记录
  - 历史改进记录
  - 优化说明

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速参考指南

## 🎯 功能概览

播放列表（Playlist）功能允许你：

1. **创建多个播放列表**
   - 音乐播放列表
   - 有声书播放列表
   - 播客播放列表
   - 自定义内容播放列表

2. **管理播放列表**
   - 添加/删除播放项
   - 修改播放列表信息
   - 设置语音关键词

3. **语音控制播放**
   - "播放音乐播单"
   - "播放有声书"
   - "播放我的播客"

4. **自定义音频源**
   - 通过 `user_config.py` 中的 `get_audio_url()` 函数
   - 支持动态获取播放 URL
   - 可集成任意音频源

## 🚀 快速开始

### 存储结构

播单数据采用多文件存储格式（v1.0+ 新特性）：

```
playlists/
├── index.json           # 播单索引文件
├── {playlist_id_1}.json # 播单1的详细数据
└── {playlist_id_2}.json # 播单2的详细数据
```

**数据迁移**：如果你之前使用旧版本，请运行：
```bash
python scripts/migrate_playlists.py
```

详见：[存储结构重构说明](PLAYLIST_STORAGE_REFACTOR.md)

### 1. 创建播放列表

通过管理后台或 API 创建播放列表：

```bash
curl -X POST http://localhost:8000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的音乐",
    "type": "music",
    "description": "我喜欢的音乐",
    "voice_keywords": ["音乐", "歌曲"]
  }'
```

### 2. 添加播放项

```bash
curl -X POST http://localhost:8000/api/playlists/{playlist_id}/items \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "title": "告白气球",
        "artist": "周杰伦",
        "url": "https://music.qq.com/song.mp3"
      }
    ]
  }'
```

### 3. 语音播放

对小爱音箱说："播放音乐"

## 📖 详细文档

查看 [PLAYLIST_GUIDE.md](PLAYLIST_GUIDE.md) 了解完整功能说明。

## 🔗 相关文档

- [API 参考](../api/API_REFERENCE.md) - 播放列表 API
- [用户配置](../config/USER_CONFIG_GUIDE.md) - 自定义音频源配置
