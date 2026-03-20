# API 文档

XiaoAI Media 后端 API 的完整文档。

## 📚 文档列表

- **[API_REFERENCE.md](API_REFERENCE.md)** - API 接口完整参考
  - 所有端点的详细说明
  - 请求/响应格式
  - 错误代码

- **[API实现说明.md](API实现说明.md)** - API 实现技术说明
  - 架构设计
  - 实现细节
  - 最佳实践

## 🎯 API 端点概览

### 设备管理 `/api/devices`
- `GET /api/devices` - 获取设备列表

### TTS 语音播报 `/api/tts`
- `POST /api/tts` - 发送文本到音箱播报

### 音量控制 `/api/volume`
- `GET /api/volume` - 获取当前音量
- `POST /api/volume/set` - 设置音量
- `POST /api/volume/up` - 增加音量
- `POST /api/volume/down` - 减少音量

### 命令控制 `/api/command`
- `POST /api/command` - 发送控制命令

### 配置管理 `/api/config`
- `GET /api/config` - 获取当前配置
- `PUT /api/config` - 更新配置

### 音乐功能 `/api/music`
- `POST /api/music/search` - 搜索音乐
- `POST /api/music/play` - 播放音乐
- `GET /api/music/charts` - 获取排行榜

### 播放列表 `/api/playlists`
- `GET /api/playlists` - 获取所有播放列表
- `POST /api/playlists` - 创建播放列表
- `GET /api/playlists/{id}` - 获取播放列表详情
- `PUT /api/playlists/{id}` - 更新播放列表
- `DELETE /api/playlists/{id}` - 删除播放列表
- `POST /api/playlists/{id}/items` - 添加播放项
- `DELETE /api/playlists/{id}/items/{index}` - 删除播放项
- `POST /api/playlists/{id}/play` - 播放播放列表

### 音频代理 `/api/proxy`
- `GET /api/proxy/stream` - 代理音频流

## 🚀 快速开始

### 基础 URL
```
http://localhost:8000/api
```

### 认证
当前版本无需认证。

### 示例请求

#### 获取设备列表
```bash
curl http://localhost:8000/api/devices
```

#### 发送 TTS
```bash
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "你好，小爱同学"}'
```

#### 搜索音乐
```bash
curl -X POST http://localhost:8000/api/music/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "告白气球", "platform": "tx"}'
```

## 📖 详细文档

查看 [API_REFERENCE.md](API_REFERENCE.md) 了解所有端点的详细说明。

## 🔗 相关文档

- [配置 API](../config/CONFIG_API.md) - 配置管理 API 详解
- [播放列表指南](../playlist/PLAYLIST_GUIDE.md) - 播放列表 API 使用
- [快速开始](../README.md) - 项目快速开始
