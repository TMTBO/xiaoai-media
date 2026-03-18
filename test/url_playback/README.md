# URL播放功能测试

本目录包含小爱音箱URL播放功能的测试脚本和文档。

## 测试脚本

### 基础测试
- `test_play_url.py` - 测试基础的 play_url 方法
- `test_play_methods.py` - 测试不同的播放方法（player_play_url, player_play_music等）
- `test_play_with_stop.py` - 测试先停止再播放的流程

### 完整流程测试
- `test_complete_flow.py` - 完整测试：搜索 → 获取URL → 播放
- `test_music_flow.py` - 音乐播放流程测试
- `test_api_play.py` - 测试 /api/music/play API端点
- `test_playlist_control.py` - 测试播放列表控制（play → next → prev）

## 运行测试

### 前提条件
确保已设置环境变量：
```bash
export MI_USER=<your_xiaomi_account>
export MI_PASS=<your_password>
export MI_DID=<device_id>
```

或者在 `.env` 文件中配置。

### 运行单个测试
```bash
# 测试完整流程
python test/url_playback/test_complete_flow.py

# 测试API端点
python test/url_playback/test_api_play.py

# 测试播放列表控制
python test/url_playback/test_playlist_control.py
```

### 运行所有测试
```bash
cd test/url_playback
for test in test_*.py; do
    echo "Running $test..."
    python "$test"
    echo "---"
done
```

## 文档

- `FINAL_TEST_REPORT.md` - 最终测试报告，包含问题解决方案和测试结果
- `TEST_RESULTS.md` - 详细的测试结果记录
- `URL_PLAYBACK_INVESTIGATION.md` - URL播放功能的调查报告

## 关键发现

1. **不同硬件需要不同的播放方法**：
   - OH2P, LX04 等型号：使用 `player_play_music`
   - 其他型号：使用 `player_play_url`

2. **必须添加的参数**：
   - `media: "app_ios"` - 必须参数
   - `_type`: 1=MUSIC模式（灯光亮），2=普通模式

3. **参考项目**：
   - xiaomusic: https://github.com/hanxi/xiaomusic
   - miservice-fork: https://github.com/hanxi/MiService

## 测试环境

- Python: 3.14
- 设备: Xiaomi 智能音箱 Pro (OH2P)
- 音乐API: http://localhost:5050
- 后端API: http://localhost:8000
