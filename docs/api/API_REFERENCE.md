# API 接口参考

## 音乐播放控制

### 播放音乐
```http
POST /api/music/play
Content-Type: application/json

{
  "index": 0,
  "device_id": "设备ID（可选）"
}
```

### 暂停播放
```http
POST /api/music/pause
Content-Type: application/json

{
  "device_id": "设备ID（可选）"
}
```

**说明**: 使用新的 `player_pause` API，比语音命令更可靠。

### 恢复播放
```http
POST /api/music/resume
Content-Type: application/json

{
  "device_id": "设备ID（可选）"
}
```

**说明**: 使用新的 `player_play` API，比语音命令更可靠。

### 停止播放
```http
POST /api/music/stop
Content-Type: application/json

{
  "device_id": "设备ID（可选）"
}
```

**说明**: 新增接口，使用 `player_stop` API。

### 获取播放状态
```http
GET /api/music/status?device_id=设备ID
```

**说明**: 新增接口，获取当前播放状态。

### 下一首
```http
POST /api/music/next
Content-Type: application/json

{
  "device_id": "设备ID（可选）"
}
```

### 上一首
```http
POST /api/music/prev
Content-Type: application/json

{
  "device_id": "设备ID（可选）"
}
```

## 音乐搜索

### 搜索歌曲
```http
GET /api/music/search?query=关键词&platform=tx&page=1&limit=20
```

参数：
- `query`: 搜索关键词（必填）
- `platform`: 平台代码（可选，默认tx）
  - `tx`: 腾讯音乐/QQ音乐
  - `wy`: 网易云音乐
  - `kw`: 酷我音乐
  - `kg`: 酷狗音乐
  - `mg`: 咪咕音乐
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20，最大50）

### 获取排行榜列表
```http
GET /api/music/ranks?platform=tx
```

### 获取排行榜歌曲
```http
GET /api/music/rank/{rank_id}?platform=tx&page=1&limit=50
```

## 播放列表管理

### 同步播放列表
```http
POST /api/music/playlist
Content-Type: application/json

{
  "songs": [
    {
      "id": "歌曲ID",
      "name": "歌曲名",
      "singer": "歌手",
      "platform": "平台代码",
      "qualities": [...],
      "interval": 时长（秒）,
      "meta": {...}
    }
  ],
  "device_id": "设备ID（可选）"
}
```

### 获取播放列表
```http
GET /api/music/playlist?device_id=设备ID
```

## 语音命令

### 执行语音命令
```http
POST /api/music/voice-command
Content-Type: application/json

{
  "text": "播放周杰伦的稻香",
  "device_id": "设备ID（可选）"
}
```

支持的命令格式：
- `播放[平台][排行榜名称]` - 播放排行榜
- 其他文本 - 作为语音命令发送给音箱

### 搜索结果播报
```http
POST /api/music/announce-search
Content-Type: application/json

{
  "query": "周杰伦",
  "count": 10,
  "device_id": "设备ID（可选）"
}
```

## 设备管理

### 获取设备列表
```http
GET /api/devices?force_refresh=false
```

## TTS 文本转语音

### TTS播报
```http
POST /api/tts
Content-Type: application/json

{
  "text": "您好",
  "device_id": "设备ID（可选）"
}
```

### 执行命令
```http
POST /api/command
Content-Type: application/json

{
  "text": "播放音乐",
  "device_id": "设备ID（可选）",
  "silent": false
}
```

参数：
- `silent`: true=静默执行（无语音回应），false=正常执行（有语音回应）

## 音量控制

### 设置音量
```http
POST /api/volume
Content-Type: application/json

{
  "volume": 50,
  "device_id": "设备ID（可选）"
}
```

### 获取音量
```http
GET /api/volume?device_id=设备ID
```

## 配置管理

### 获取配置
```http
GET /api/config
```

### 更新配置
```http
POST /api/config
Content-Type: application/json

{
  "enable_conversation_polling": true,
  "conversation_poll_interval": 3
}
```

## 错误响应

所有接口在出错时返回标准错误格式：

```json
{
  "detail": "错误描述"
}
```

常见HTTP状态码：
- `200`: 成功
- `404`: 资源不存在
- `422`: 参数错误
- `502`: 外部服务错误
