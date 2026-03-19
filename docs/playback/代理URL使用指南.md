# 代理URL使用指南

## 🎯 快速参考

### 为什么需要代理？

音乐平台URL有防盗链保护，音箱直接访问会被拒绝。使用代理可以：
- ✅ 添加必要的HTTP headers
- ✅ 绕过防盗链限制
- ✅ 确保音箱能正常播放

### 如何使用？

**在 `music.py` 中：**
```python
# 获取原始URL
original_url = play_info["url"]

# 转换为代理URL
url = _make_proxy_url(original_url)

# 播放
await client.play_url(url, device_id, _type=1)
```

**在其他文件中：**
```python
from xiaoai_media.api.routes.music import _make_proxy_url

# 获取原始URL
original_url = play_info["url"]

# 转换为代理URL
url = _make_proxy_url(original_url)

# 播放
await client.play_url(url, device_id, _type=1)
```

## 📋 已应用的位置

| 功能 | 文件 | 函数 | 状态 |
|------|------|------|------|
| 播放指定歌曲 | `music.py` | `play_music` | ✅ |
| 下一首 | `music.py` | `play_next` | ✅ |
| 上一首 | `music.py` | `play_prev` | ✅ |
| 对话拦截播放 | `command_handler.py` | `_play_intercepted_song` | ✅ |

## 🔍 URL转换示例

### 腾讯音乐
```
原始: https://isure.stream.qqmusic.qq.com/C400003mAan70zUy5O.m4a?guid=xxx&vkey=xxx
代理: http://10.184.62.160:5050/main/proxy?url=https%3A//isure.stream.qqmusic.qq.com/...
```

### 网易云音乐
```
原始: https://music.163.com/song/media/outer/url?id=123456.mp3
代理: http://10.184.62.160:5050/main/proxy?url=https%3A//music.163.com/song/media/...
```

### 酷狗音乐
```
原始: http://fs.w.kugou.com/xxx.mp3
代理: http://10.184.62.160:5050/main/proxy?url=http%3A//fs.w.kugou.com/xxx.mp3
```

## ⚠️ 注意事项

### 1. 不要直接使用原始URL

❌ **错误做法：**
```python
url = play_info["url"]
await client.play_url(url, device_id)  # 音箱无法访问，播放失败
```

✅ **正确做法：**
```python
original_url = play_info["url"]
url = _make_proxy_url(original_url)
await client.play_url(url, device_id)  # 通过代理，播放成功
```

### 2. 确保配置正确

检查 `.env` 文件：
```env
# ❌ 错误：使用localhost
MUSIC_API_BASE_URL=http://localhost:5050

# ✅ 正确：使用局域网IP
MUSIC_API_BASE_URL=http://10.184.62.160:5050
```

### 3. 验证代理服务

确保 music_download 服务正在运行：
```bash
curl "http://10.184.62.160:5050/main/proxy?url=https://www.baidu.com"
```

应该返回百度首页内容。

## 🧪 测试

### 运行单元测试
```bash
python test/music/test_proxy_function.py
```

### 运行诊断
```bash
python test/music/diagnose_playback.py
```

应该看到：
```
✅ 配置检查
✅ 代理端点
```

## 🐛 故障排查

### 问题1：播放失败

**检查日志：**
```
[DEBUG] Converted URL to proxy: https://... -> http://10.184.62.160:5050/main/proxy?url=...
```

如果没有这行日志，说明没有使用代理函数。

**解决方案：**
确保在 `play_url` 前调用了 `_make_proxy_url`。

### 问题2：代理服务不可用

**错误信息：**
```
Cannot connect to proxy service
```

**解决方案：**
1. 检查 music_download 服务是否运行
2. 检查局域网IP是否正确
3. 检查防火墙设置

### 问题3：URL编码问题

**症状：**
代理URL中包含未编码的特殊字符。

**解决方案：**
`_make_proxy_url` 会自动处理URL编码，无需手动编码。

## 📚 相关文档

- [代理URL封装说明](./代理URL封装说明.md) - 详细技术文档
- [播放错误修复说明](./播放错误修复说明.md) - 问题分析和解决方案
- [播放错误快速修复](./播放错误快速修复.md) - 快速修复指南

## 💡 最佳实践

### 1. 统一使用代理函数
所有播放URL的地方都应该使用 `_make_proxy_url`。

### 2. 保留原始URL日志
便于调试和问题排查：
```python
_log.info("Got original URL: %s", original_url[:200])
url = _make_proxy_url(original_url)
_log.debug("Converted to proxy URL: %s", url[:200])
```

### 3. 错误处理
```python
try:
    url = _make_proxy_url(original_url)
    result = await client.play_url(url, device_id)
except Exception as e:
    _log.error("Failed to play: %s", e)
    raise
```

## 🚀 未来扩展

如果需要修改代理逻辑（如添加缓存、更换代理服务器等），只需修改 `_make_proxy_url` 函数，所有调用处自动生效。

**示例：添加缓存参数**
```python
def _make_proxy_url(original_url: str, cache: bool = True) -> str:
    """Convert URL to proxy URL with optional caching."""
    cache_param = "&cache=1" if cache else ""
    return f"{config.MUSIC_API_BASE_URL}/main/proxy?url={quote(original_url)}{cache_param}"
```
