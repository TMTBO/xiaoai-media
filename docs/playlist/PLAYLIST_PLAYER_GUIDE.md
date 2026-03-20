# 播放列表管理器 - 使用指南

## 概述

现在后端项目已经集成了一个完整的播放列表管理器，支持通过以下方式加载音乐并进行语音控制：

1. **搜索结果** - 搜索歌曲并加载到播放列表
2. **排行榜** - 从音乐平台排行榜加载歌曲
3. **保存的播单** - 从持久化的播单加载多媒体内容

所有这些功能都已经整合到 `music.py` 的播放控制能力中，支持统一的播放控制（播放、暂停、继续、停止、下一首、上一首）。

---

## API 端点

### 1. 从搜索结果加载播放列表

**端点**: `POST /api/music/load-from-search`

**功能**: 根据关键词搜索音乐，将结果加载到设备的播放列表中。

**请求体**:
```json
{
  "query": "周杰伦",
  "device_id": "xxx",
  "platform": "tx",     // 可选: tx|kw|kg|wy|mg，默认使用配置的平台
  "auto_play": true     // 可选: 是否自动播放第一首，默认 true
}
```

**响应**:
```json
{
  "action": "load_from_search",
  "query": "周杰伦",
  "platform": "tx",
  "device_id": "xxx",
  "total": 50,
  "songs": [
    {"name": "晴天", "singer": "周杰伦"},
    // 前10首歌曲的预览...
  ],
  "play_result": {...}  // 如果 auto_play=true，包含播放结果
}
```

**使用场景**: 
- 通过搜索关键词快速找到并播放音乐
- 创建基于艺术家或歌曲名的临时播放列表

---

### 2. 从排行榜加载播放列表

**端点**: `POST /api/music/load-from-chart`

**功能**: 从音乐平台的排行榜加载歌曲列表。

**请求体**:
```json
{
  "chart_keyword": "热歌榜",  // 或使用 chart_id
  "device_id": "xxx",
  "platform": "tx",          // 可选
  "auto_play": true          // 可选
}
```

**响应**:
```json
{
  "action": "load_from_chart",
  "chart_name": "腾讯音乐热歌榜",
  "chart_id": "123",
  "platform": "tx",
  "device_id": "xxx",
  "total": 50,
  "songs": [...],
  "play_result": {...}
}
```

**使用场景**:
- 播放当前流行音乐
- 发现新歌曲

---

### 3. 从保存的播单加载

**端点**: `POST /api/music/load-from-playlist`

**功能**: 从持久化的播单（来自 `/api/playlists`）加载内容到播放列表。

**请求体**:
```json
{
  "playlist_id": "音乐_1234567890",
  "device_id": "xxx",
  "auto_play": true
}
```

**响应**:
```json
{
  "action": "load_from_playlist",
  "playlist_name": "我的音乐",
  "playlist_id": "音乐_1234567890",
  "device_id": "xxx",
  "total": 30,
  "songs": [...],
  "play_result": {...}
}
```

**使用场景**:
- 播放自己策划的歌单
- 播放有声书、播客等多媒体内容

---

### 4. 统一的语音命令接口

**端点**: `POST /api/music/voice-command`

**功能**: 处理自然语言语音命令，自动识别意图并执行相应操作。

**请求体**:
```json
{
  "text": "播放腾讯热歌榜",
  "device_id": "xxx"
}
```

**支持的命令模式**:

| 命令类型 | 示例 | 说明 |
|---------|------|------|
| 播单 | "播放音乐播单"<br>"打开我的有声书" | 匹配播单名称或语音关键词 |
| 排行榜 | "播放腾讯热歌榜"<br>"打开网易云飙升榜" | 自动匹配平台和榜单名 |
| 搜索 | "搜索周杰伦"<br>"查找晴天" | 搜索并加载结果 |
| 其他 | 任意文本 | 直接发送给小爱音箱执行 |

**响应**:
```json
{
  "action": "play_playlist|play_chart|search_and_play|command",
  "result": {...},
  // 其他字段根据action类型而定
}
```

---

## 播放控制

加载播放列表后，可以使用以下端点控制播放：

| 端点 | 方法 | 功能 |
|-----|------|------|
| `/api/music/play` | POST | 播放指定索引的歌曲 |
| `/api/music/next` | POST | 下一首 |
| `/api/music/prev` | POST | 上一首 |
| `/api/music/pause` | POST | 暂停 |
| `/api/music/resume` | POST | 继续 |
| `/api/music/stop` | POST | 停止 |
| `/api/music/status` | GET | 获取播放状态 |

**示例**:
```bash
# 播放第一首
curl -X POST http://localhost:8000/api/music/play \
  -H "Content-Type: application/json" \
  -d '{"index": 0, "device_id": "xxx"}'

# 下一首
curl -X POST http://localhost:8000/api/music/next \
  -H "Content-Type: application/json" \
  -d '{"device_id": "xxx"}'

# 暂停
curl -X POST http://localhost:8000/api/music/pause \
  -H "Content-Type: application/json" \
  -d '{"device_id": "xxx"}'
```

---

## 语音控制集成

`command_handler.py` 已经集成了统一的语音命令处理。当音箱检测到唤醒词后的指令时，会自动：

1. 预处理指令（移除唤醒词等）
2. 调用 `/api/music/voice-command` 端点
3. 执行相应的操作（加载播单、排行榜、搜索等）
4. 返回语音反馈

**工作流程**:
```
用户说话
  ↓
"小爱同学，播放腾讯热歌榜"
  ↓
会话监控检测到指令
  ↓
command_handler.handle_command()
  ↓
预处理: "播放腾讯热歌榜"
  ↓
调用 /api/music/voice-command
  ↓
识别为排行榜命令
  ↓
加载排行榜并自动播放
  ↓
音箱开始播放
```

---

## 完整示例

### 示例 1: 通过语音播放排行榜

```python
import aiohttp
import asyncio

async def play_chart_by_voice():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/api/music/voice-command",
            json={
                "text": "播放腾讯热歌榜",
                "device_id": "your-device-id"
            }
        ) as resp:
            result = await resp.json()
            print(f"播放成功！榜单: {result['result']['chart_name']}")

asyncio.run(play_chart_by_voice())
```

### 示例 2: 搜索并播放

```python
async def search_and_play():
    async with aiohttp.ClientSession() as session:
        # 方式1: 直接使用 load-from-search
        async with session.post(
            "http://localhost:8000/api/music/load-from-search",
            json={
                "query": "周杰伦",
                "device_id": "your-device-id",
                "platform": "tx",
                "auto_play": True
            }
        ) as resp:
            result = await resp.json()
            print(f"加载了 {result['total']} 首歌曲")
        
        # 方式2: 使用语音命令
        async with session.post(
            "http://localhost:8000/api/music/voice-command",
            json={
                "text": "搜索周杰伦",
                "device_id": "your-device-id"
            }
        ) as resp:
            result = await resp.json()
            print(f"搜索命令执行成功")

asyncio.run(search_and_play())
```

### 示例 3: 加载播单并控制播放

```python
async def playlist_control():
    async with aiohttp.ClientSession() as session:
        # 1. 加载播单
        async with session.post(
            "http://localhost:8000/api/music/load-from-playlist",
            json={
                "playlist_id": "音乐_1234567890",
                "device_id": "your-device-id",
                "auto_play": True
            }
        ) as resp:
            result = await resp.json()
            print(f"播单 '{result['playlist_name']}' 开始播放")
        
        # 2. 等待一会儿
        await asyncio.sleep(10)
        
        # 3. 下一首
        async with session.post(
            "http://localhost:8000/api/music/next",
            json={"device_id": "your-device-id"}
        ) as resp:
            result = await resp.json()
            current = result['current']
            print(f"切换到: {current['singer']} - {current['name']}")
        
        # 4. 暂停
        await asyncio.sleep(5)
        async with session.post(
            "http://localhost:8000/api/music/pause",
            json={"device_id": "your-device-id"}
        ) as resp:
            print("已暂停")

asyncio.run(playlist_control())
```

---

## 测试

运行测试脚本验证所有功能：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行测试
python test/music/test_playlist_player.py
```

测试脚本会验证：
- ✓ 从搜索结果加载
- ✓ 从排行榜加载
- ✓ 语音命令-播单
- ✓ 语音命令-排行榜
- ✓ 语音命令-搜索
- ✓ 播放控制（下一首/上一首）

---

## 注意事项

1. **播单 URL 处理**: 从 `playlist.py` 加载的播单项如果没有直接的 URL，需要通过 `user_config.py` 中的 `get_audio_url` 函数动态获取。目前这部分功能需要用户自行实现。

2. **设备 ID**: 如果请求中没有提供 `device_id`，系统会使用默认设备（配置中的第一个设备）。

3. **平台支持**: 当前支持的音乐平台包括：
   - `tx` - 腾讯音乐/QQ音乐
   - `kw` - 酷我音乐
   - `kg` - 酷狗音乐
   - `wy` - 网易云音乐
   - `mg` - 咪咕音乐

4. **播放列表存储**: 播放列表存储在内存中，按设备ID索引。服务重启后需要重新加载。

---

## 架构说明

```
用户
  ├─→ 直接 API 调用
  │     ├─ /api/music/load-from-search
  │     ├─ /api/music/load-from-chart
  │     ├─ /api/music/load-from-playlist
  │     └─ /api/music/voice-command
  │
  └─→ 语音命令
        ↓
    会话监控 (conversation_monitor)
        ↓
    command_handler.handle_command()
        ↓
    /api/music/voice-command (统一入口)
        ↓
    自动识别意图并路由到:
        ├─ load_from_playlist (播单)
        ├─ load_from_chart (排行榜)
        ├─ load_from_search (搜索)
        └─ 其他命令 (直接发送给音箱)
```

---

## 下一步

1. **前端集成**: 在前端添加播放列表管理界面
2. **自定义播单**: 通过 `/api/playlists` 创建和管理个性化播单
3. **历史记录**: 记录播放历史和常用播单
4. **智能推荐**: 根据播放历史推荐相似音乐

---

## 更新日志

**2026-03-20**:
- 添加统一的播放列表管理器
- 集成搜索、排行榜、播单三种加载方式
- 增强 voice-command 支持多种意图识别
- 简化 command_handler 使用统一端点
- 添加完整的测试套件
