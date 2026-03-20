# 播放列表管理器 - 快速参考

## 新增功能总览

✅ **统一的播放列表管理器**，集成以下三种来源：
1. 🔍 **搜索结果** - 搜索歌曲并加载
2. 📊 **排行榜** - 从音乐平台榜单加载  
3. 📑 **保存的播单** - 从持久化播单加载

✅ **语音控制支持**，自动识别以下命令：
- "播放音乐播单"
- "播放腾讯热歌榜"
- "搜索周杰伦"

✅ **完整的播放控制**：播放、暂停、继续、停止、下一首、上一首

---

## 快速开始

### 1. 通过搜索播放音乐
```bash
curl -X POST http://localhost:8000/api/music/load-from-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "周杰伦",
    "device_id": "your-device-id",
    "auto_play": true
  }'
```

### 2. 播放排行榜
```bash
curl -X POST http://localhost:8000/api/music/load-from-chart \
  -H "Content-Type: application/json" \
  -d '{
    "chart_keyword": "热歌榜",
    "device_id": "your-device-id",
    "platform": "tx",
    "auto_play": true
  }'
```

### 3. 语音命令
```bash
curl -X POST http://localhost:8000/api/music/voice-command \
  -H "Content-Type: application/json" \
  -d '{
    "text": "播放腾讯热歌榜",
    "device_id": "your-device-id"
  }'
```

### 4. 播放控制
```bash
# 下一首
curl -X POST http://localhost:8000/api/music/next \
  -H "Content-Type: application/json" \
  -d '{"device_id": "your-device-id"}'

# 暂停
curl -X POST http://localhost:8000/api/music/pause \
  -H "Content-Type: application/json" \
  -d '{"device_id": "your-device-id"}'
```

---

## API 端点速查

| 端点 | 功能 | 参数 |
|-----|------|------|
| `POST /api/music/load-from-search` | 从搜索加载 | query, device_id, platform?, auto_play? |
| `POST /api/music/load-from-chart` | 从排行榜加载 | chart_keyword/chart_id, device_id, platform?, auto_play? |
| `POST /api/music/load-from-playlist` | 从播单加载 | playlist_id, device_id, auto_play? |
| `POST /api/music/voice-command` | 语音命令 | text, device_id |
| `POST /api/music/play` | 播放指定索引 | index, device_id |
| `POST /api/music/next` | 下一首 | device_id |
| `POST /api/music/prev` | 上一首 | device_id |
| `POST /api/music/pause` | 暂停 | device_id |
| `POST /api/music/resume` | 继续 | device_id |
| `POST /api/music/stop` | 停止 | device_id |
| `GET /api/music/status` | 播放状态 | device_id |

---

## 语音命令示例

| 说法 | 识别为 | 行为 |
|-----|-------|------|
| "播放音乐播单" | 播单命令 | 查找并播放匹配的播单 |
| "播放腾讯热歌榜" | 排行榜命令 | 加载榜单并播放第一首 |
| "搜索周杰伦" | 搜索命令 | 搜索并加载结果，播放第一首 |
| "播放周杰伦的歌" | 其他命令 | 直接发送给小爱音箱 |

---

## 测试

```bash
# 运行完整测试套件
source .venv/bin/activate
python test/music/test_playlist_player.py
```

---

## 文档

- 📖 **完整指南**: [PLAYLIST_PLAYER_GUIDE.md](PLAYLIST_PLAYER_GUIDE.md)
- 📝 **API 文档**: 访问 `http://localhost:8000/docs` 查看 Swagger UI

---

## 技术细节

**修改的文件**:
- ✏️ `backend/src/xiaoai_media/api/routes/music.py` - 添加新端点和增强 voice-command
- ✏️ `backend/src/xiaoai_media/command_handler.py` - 简化为统一调用 voice-command 端点

**新增的文件**:
- ✨ `test/music/test_playlist_player.py` - 完整测试套件
- ✨ `docs/playlist/PLAYLIST_PLAYER_GUIDE.md` - 详细使用指南
- ✨ `docs/playlist/QUICK_REFERENCE.md` - 本文档

**架构改进**:
- 🎯 统一的播放列表管理（内存存储，按设备 ID 索引）
- 🎯 统一的语音命令处理入口（自动意图识别）
- 🎯 灵活的加载方式（搜索/排行榜/播单）
- 🎯 完整的播放控制（next/prev/pause/resume/stop）

---

**更新时间**: 2026-03-20
