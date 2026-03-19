# 代理URL封装说明

## 📦 功能概述

将音乐URL代理功能封装为统一的函数`_make_proxy_url()`，在所有播放URL的地方统一使用。

## 🎯 封装的函数

### `_make_proxy_url(original_url: str) -> str`

**位置：** `backend/src/xiaoai_media/api/routes/music.py`

**功能：** 将音乐平台的原始URL转换为代理URL，使音箱能够访问。

**参数：**
- `original_url`: 音乐平台的原始URL（如 `https://music.qq.com/xxx.mp3`）

**返回：**
- 代理URL（如 `http://10.184.62.160:5050/main/proxy?url=https%3A%2F%2F...`）

**示例：**
```python
from xiaoai_media.api.routes.music import _make_proxy_url

# 原始URL
original = "https://music.qq.com/song.mp3"

# 转换为代理URL
proxy = _make_proxy_url(original)
# 结果: http://10.184.62.160:5050/main/proxy?url=https%3A%2F%2Fmusic.qq.com%2Fsong.mp3
```

## 📍 应用位置

已在以下所有播放URL的地方应用代理：

### 1. 播放指定歌曲 (`play_music`)
**文件：** `backend/src/xiaoai_media/api/routes/music.py`

```python
async def play_music(req: PlayRequest):
    # ...
    original_url = play_info["url"]
    url = _make_proxy_url(original_url)  # ✅ 使用代理
    result = await client.play_url(url, req.device_id, _type=1)
```

### 2. 下一首 (`play_next`)
**文件：** `backend/src/xiaoai_media/api/routes/music.py`

```python
async def play_next(req: DeviceRequest):
    # ...
    original_url = play_info["url"]
    url = _make_proxy_url(original_url)  # ✅ 使用代理
    result = await client.play_url(url, req.device_id, _type=1)
```

### 3. 上一首 (`play_prev`)
**文件：** `backend/src/xiaoai_media/api/routes/music.py`

```python
async def play_prev(req: DeviceRequest):
    # ...
    original_url = play_info["url"]
    url = _make_proxy_url(original_url)  # ✅ 使用代理
    result = await client.play_url(url, req.device_id, _type=1)
```

### 4. 对话拦截播放 (`_play_intercepted_song`)
**文件：** `backend/src/xiaoai_media/command_handler.py`

```python
async def _play_intercepted_song(self, device_id: str, index: int):
    # ...
    original_url = play_info["url"]
    from xiaoai_media.api.routes.music import _make_proxy_url
    url = _make_proxy_url(original_url)  # ✅ 使用代理
    result = await client.play_url(url, device_id, _type=1)
```

## 🔍 工作原理

### 转换过程

```
原始URL (音乐平台)
    ↓
URL编码 (quote)
    ↓
拼接代理路径
    ↓
代理URL (音箱可访问)
```

### 详细示例

**输入：**
```
https://isure.stream.qqmusic.qq.com/C400003mAan70zUy5O.m4a?guid=test&vkey=test
```

**处理：**
1. URL编码：`https%3A//isure.stream.qqmusic.qq.com/C400003mAan70zUy5O.m4a%3Fguid%3Dtest%26vkey%3Dtest`
2. 拼接：`{MUSIC_API_BASE_URL}/main/proxy?url={编码后的URL}`

**输出：**
```
http://10.184.62.160:5050/main/proxy?url=https%3A//isure.stream.qqmusic.qq.com/C400003mAan70zUy5O.m4a%3Fguid%3Dtest%26vkey%3Dtest
```

## ✅ 优势

### 1. 统一管理
- 所有代理逻辑集中在一个函数
- 修改代理逻辑只需改一处
- 代码更易维护

### 2. 一致性
- 所有播放URL都使用相同的代理方式
- 避免遗漏某些播放场景
- 确保所有播放都能正常工作

### 3. 可测试性
- 函数独立，易于单元测试
- 可以验证URL转换的正确性
- 便于调试和问题排查

### 4. 可扩展性
- 未来如需修改代理逻辑（如添加参数、更换代理服务器等）
- 只需修改`_make_proxy_url`函数
- 所有调用处自动生效

## 🧪 测试

运行测试脚本验证代理函数：

```bash
python test/music/test_proxy_function.py
```

**预期输出：**
```
============================================================
测试代理URL函数
============================================================

配置的音乐API地址: http://10.184.62.160:5050

测试用例：

1. 原始URL:
   https://music.qq.com/song.mp3
   代理URL:
   http://10.184.62.160:5050/main/proxy?url=https%3A//music.qq.com/song.mp3
   ✅ 格式正确

...

============================================================
所有测试通过！
============================================================
```

## 📝 使用建议

### 在新代码中使用

如果需要添加新的播放功能，记得使用代理函数：

```python
# ❌ 错误：直接使用原始URL
url = play_info["url"]
await client.play_url(url, device_id)

# ✅ 正确：使用代理URL
original_url = play_info["url"]
url = _make_proxy_url(original_url)
await client.play_url(url, device_id)
```

### 导入方式

在`music.py`中：
```python
# 直接使用，无需导入
url = _make_proxy_url(original_url)
```

在其他文件中：
```python
from xiaoai_media.api.routes.music import _make_proxy_url

url = _make_proxy_url(original_url)
```

## 🔧 故障排查

### 如果播放失败

1. **检查日志中的URL**
   ```
   [DEBUG] Converted URL to proxy: https://... -> http://10.184.62.160:5050/main/proxy?url=...
   ```

2. **验证代理服务**
   ```bash
   curl "http://10.184.62.160:5050/main/proxy?url=https://www.baidu.com"
   ```

3. **检查配置**
   ```bash
   cat .env | grep MUSIC_API_BASE_URL
   ```

## 📚 相关文档

- [播放错误修复说明](./播放错误修复说明.md)
- [播放错误快速修复](./播放错误快速修复.md)
- [PLAYBACK_FIX.md](./PLAYBACK_FIX.md)
