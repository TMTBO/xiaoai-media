# 播放错误修复说明

## 问题根源

通过对比xiaomusic的成功播放日志，发现了当前项目播放失败的核心原因：

### 1. URL访问问题（主要原因）

**xiaomusic的做法：**
- 使用本地音乐文件
- 通过HTTP服务器提供访问：`http://192.168.x.x:8090/music/xxx.flac`
- 音箱可以直接访问局域网内的HTTP服务器

**当前项目的问题：**
- 从音乐平台API获取的URL有防盗链保护
- 音箱直接访问这些URL会被拒绝（缺少Referer、User-Agent等headers）
- 导致播放失败

### 2. localhost配置问题

原配置：
```env
MUSIC_API_BASE_URL=http://localhost:5050
```

音箱无法访问localhost，需要使用局域网IP。

## 解决方案

### 修改1：使用代理URL

在`backend/src/xiaoai_media/api/routes/music.py`的`play_music`函数中：

```python
# 将音乐平台URL转换为代理URL
from urllib.parse import quote
proxy_url = f"{config.MUSIC_API_BASE_URL}/main/proxy?url={quote(original_url)}"
```

这样音箱访问的是：
```
http://10.184.62.160:5050/main/proxy?url=https%3A%2F%2Fmusic.platform.com%2Fsong.mp3
```

代理服务器会：
1. 接收音箱的请求
2. 添加必要的headers访问音乐平台
3. 将音乐流转发给音箱

### 修改2：更新配置文件

`.env`文件：
```env
MUSIC_API_BASE_URL=http://10.184.62.160:5050
```

使用局域网IP而不是localhost。

### 修改3：添加停止延迟

在播放前添加0.5秒延迟，确保停止完成：
```python
await client.player_stop(req.device_id)
await asyncio.sleep(0.5)
await client.play_url(url, req.device_id, _type=1)
```

## 关键对比

| 项目 | xiaomusic | 当前项目（修复前） | 当前项目（修复后） |
|------|-----------|-------------------|-------------------|
| 音乐源 | 本地文件 | 在线音乐平台 | 在线音乐平台 |
| URL格式 | `http://局域网IP:端口/music/xxx.flac` | `https://music.platform.com/xxx.mp3` | `http://局域网IP:5050/main/proxy?url=...` |
| 音箱访问 | ✅ 直接访问 | ❌ 防盗链拒绝 | ✅ 通过代理访问 |
| 停止播放 | `group_force_stop_xiaoai` | `player_stop` | `player_stop` + 延迟 |

## 测试方法

1. 重启后端服务
2. 在前端搜索并播放音乐
3. 查看后端日志，确认：
   - `Got original playback URL` - 原始URL
   - `Converted to proxy URL` - 代理URL
   - `Play result` - 播放结果

## 预期效果

修复后，播放流程：
1. 前端请求播放歌曲
2. 后端从音乐API获取原始URL
3. **转换为代理URL**（关键步骤）
4. 停止当前播放
5. 播放代理URL
6. 音箱访问代理URL
7. 代理服务器转发音乐流
8. ✅ 播放成功
