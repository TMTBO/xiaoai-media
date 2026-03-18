# URL播放功能 - 快速开始

## 5分钟快速测试

### 1. 确保服务运行

```bash
# 启动音乐API服务（端口 5050）
# 启动后端服务（端口 8000）
cd backend
python -m uvicorn xiaoai_media.api.main:app --host 0.0.0.0 --port 8000
```

### 2. 运行测试

```bash
# 完整流程测试（推荐）
python test/url_playback/test_complete_flow.py

# API端点测试
python test/url_playback/test_api_play.py
```

### 3. 预期结果

```
✓ Found: 稻香 - 周杰伦
✓ Got URL: http://wx.music.tc.qq.com/...
✓ Play result: {'method': 'player_play_music', 'result': True}
✓ SUCCESS! Song is now playing on your speaker!
```

## 使用API

### 播放歌曲

```bash
curl -X POST http://localhost:8000/api/music/play \
  -H "Content-Type: application/json" \
  -d '{
    "songs": [{
      "id": "003aAYrm3GE0Ac",
      "name": "稻香",
      "singer": "周杰伦",
      "platform": "tx"
    }],
    "index": 0,
    "device_id": "your-device-id"
  }'
```

### 下一首

```bash
curl -X POST http://localhost:8000/api/music/next \
  -H "Content-Type: application/json" \
  -d '{"device_id": "your-device-id"}'
```

### 上一首

```bash
curl -X POST http://localhost:8000/api/music/prev \
  -H "Content-Type: application/json" \
  -d '{"device_id": "your-device-id"}'
```

## Python代码示例

```python
import asyncio
from xiaoai_media.client import XiaoAiClient

async def play_song():
    url = "http://music.example.com/song.mp3"
    device_id = "your-device-id"
    
    async with XiaoAiClient() as client:
        result = await client.play_url(url, device_id)
        print(f"Playing: {result}")

asyncio.run(play_song())
```

## 常见问题

### Q: 音箱没有播放？
A: 检查：
1. 设备硬件型号是否在支持列表中
2. URL是否可访问
3. 网络连接是否正常

### Q: 如何查看设备硬件型号？
A: 
```python
async with XiaoAiClient() as client:
    devices = await client.list_devices()
    for d in devices:
        print(f"{d['name']}: {d['hardware']}")
```

### Q: 支持哪些硬件型号？
A: 
- 使用 player_play_music: OH2P, LX04, LX05, L05B, L05C, L06, L06A, X08A, X10A, X08C, X08E, X8F, X4B, X6A
- 使用 player_play_url: 其他型号

## 下一步

- 查看 [README.md](README.md) 了解所有测试
- 查看 [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) 了解实现细节
- 查看 [SUMMARY.md](SUMMARY.md) 了解完整历程
