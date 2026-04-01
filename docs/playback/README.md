# 播放功能文档

本目录包含小爱音箱播放功能的相关文档。

## 📚 文档列表

### 核心功能

- **[PLAYBACK_CONTROLLER.md](./PLAYBACK_CONTROLLER.md)** ⭐ - 播放控制器（定时器模式）
- **[PLAYBACK_CONTROLLER_CHANGELOG.md](./PLAYBACK_CONTROLLER_CHANGELOG.md)** - 播放控制器更新日志
- **[PLAYBACK_MODE_QUICK_START.md](./PLAYBACK_MODE_QUICK_START.md)** - 播放模式快速入门

### 快速开始

- **[QUICK_PLAYBACK_GUIDE.md](./QUICK_PLAYBACK_GUIDE.md)** - 播放功能快速指南
- **[播放错误快速修复.md](./播放错误快速修复.md)** - 快速修复播放错误的指南

### 问题修复

- **[PLAYBACK_TROUBLESHOOTING.md](./PLAYBACK_TROUBLESHOOTING.md)** - 播放故障排查指南
- **[播放错误修复说明.md](./播放错误修复说明.md)** - 播放错误的详细分析和修复方案
- **[PLAYBACK_FIX.md](./PLAYBACK_FIX.md)** - 播放修复技术文档（英文）

### 代理URL功能

- **[代理URL使用指南.md](./代理URL使用指南.md)** - 代理URL的使用方法和最佳实践
- **[代理URL封装说明.md](./代理URL封装说明.md)** - 代理URL封装的技术细节
- **[PROXY_URL_SUMMARY.md](./PROXY_URL_SUMMARY.md)** - 代理URL封装完成总结

## 🎯 核心概念

### 为什么需要代理？

音乐平台的URL通常有防盗链保护：
- 需要特定的HTTP headers（Referer、User-Agent等）
- 音箱直接访问会被拒绝
- 通过代理服务器可以添加必要的headers

### 代理URL格式

```
原始URL: https://music.qq.com/song.mp3
代理URL: http://10.184.62.160:5050/main/proxy?url=https%3A//music.qq.com/song.mp3
```

### 工作流程

```
音箱 → 代理服务器 → 添加headers → 音乐平台 → 返回流 → 音箱 → 播放成功
```

## 🚀 快速开始

### 1. 配置环境

编辑 `.env` 文件：
```env
MUSIC_API_BASE_URL=http://10.184.62.160:5050  # 使用局域网IP
```

### 2. 测试播放

```bash
# 运行诊断
python test/music/playback/diagnose_playback.py

# 测试代理函数
python test/music/playback/test_proxy_function.py
```

### 3. 使用代理函数

```python
from xiaoai_media.api.routes.music import _make_proxy_url

# 转换URL
original_url = "https://music.qq.com/song.mp3"
proxy_url = _make_proxy_url(original_url)

# 播放
await client.play_url(proxy_url, device_id, _type=1)
```

## 🔧 故障排查

### 播放失败

1. 检查配置是否使用局域网IP
2. 验证代理服务是否运行
3. 查看后端日志

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 播放无响应 | 使用localhost | 改为局域网IP |
| 403 Forbidden | 未使用代理 | 使用 `_make_proxy_url` |
| 连接超时 | 代理服务未运行 | 启动 music_download |

## 📖 相关文档

- [TTS功能文档](../tts/) - TTS文本转语音功能
- [对话监听文档](../conversation/) - 对话拦截和自动播放
- [API参考](../API_REFERENCE.md) - 完整API文档

## 🧪 测试

测试文件位于 `test/music/playback/` 目录：

- `diagnose_playback.py` - 诊断播放问题
- `test_proxy_function.py` - 测试代理函数
- `test_proxy_playback.py` - 测试代理播放

## 💡 最佳实践

1. **始终使用代理URL** - 所有播放URL都应该通过 `_make_proxy_url` 转换
2. **使用局域网IP** - 配置中不要使用 localhost
3. **添加日志** - 记录原始URL和代理URL便于调试
4. **错误处理** - 捕获并记录播放错误

## 🔗 快速链接

- [播放控制器](./PLAYBACK_CONTROLLER.md) - 定时器模式播放控制
- [播放模式快速入门](./PLAYBACK_MODE_QUICK_START.md) - 快速上手
- [播放错误快速修复](./播放错误快速修复.md) - 最快的修复方法
- [代理URL使用指南](./代理URL使用指南.md) - 如何使用代理
- [故障排查指南](./PLAYBACK_TROUBLESHOOTING.md) - 解决播放问题
