# 测试目录

本目录包含小爱音箱媒体控制系统的所有测试文件和文档。

## 目录结构

```
test/
├── README.md                    # 本文件
├── test_tts.py                  # TTS功能测试
├── conversation/                # 对话记录功能测试
│   ├── README.md
│   ├── test_conversation.sh
│   ├── FEATURE_SPEC.md
│   ├── TEST_REPORT.md
│   ├── USER_GUIDE.md
│   └── QUICK_REFERENCE.md
└── url_playback/                # URL播放功能测试
    ├── README.md
    ├── test_complete_flow.py
    ├── test_api_play.py
    ├── test_playlist_control.py
    ├── FINAL_TEST_REPORT.md
    └── ...
```

## 测试模块

### 1. TTS 功能测试
**文件**: `test_tts.py`

测试文字转语音功能。

```bash
python test/test_tts.py
```

### 2. 对话记录功能测试
**目录**: `conversation/`

测试小爱音箱对话历史记录功能。

```bash
cd test/conversation
./test_conversation.sh
```

详细信息请查看 [conversation/README.md](conversation/README.md)

### 3. URL播放功能测试
**目录**: `url_playback/`

测试直接播放URL的功能，包括：
- 基础播放测试
- 完整流程测试（搜索 → 获取URL → 播放）
- API端点测试
- 播放列表控制测试

```bash
# 运行完整流程测试
python test/url_playback/test_complete_flow.py

# 运行API测试
python test/url_playback/test_api_play.py

# 运行播放列表测试
python test/url_playback/test_playlist_control.py
```

详细信息请查看 [url_playback/README.md](url_playback/README.md)

## 运行所有测试

```bash
# TTS测试
python test/test_tts.py

# 对话记录测试
cd test/conversation && ./test_conversation.sh && cd ../..

# URL播放测试
for test in test/url_playback/test_*.py; do
    echo "Running $test..."
    python "$test"
done
```

## 测试环境要求

### 环境变量
```bash
export MI_USER=<your_xiaomi_account>
export MI_PASS=<your_password>
export MI_DID=<device_id>
```

或在项目根目录的 `.env` 文件中配置。

### 依赖服务
- 后端服务: http://localhost:8000
- 前端服务: http://localhost:5173
- 音乐API服务: http://localhost:5050

### Python 环境
- Python 3.10+
- 虚拟环境已激活
- 已安装所有依赖 (`pip install -e backend/`)

## 测试状态

| 模块 | 状态 | 最后更新 |
|------|------|----------|
| TTS功能 | ✅ 通过 | 2026-03-18 |
| 对话记录 | ✅ 通过 | 2026-03-18 |
| URL播放 | ✅ 通过 | 2026-03-18 |

## 贡献指南

添加新测试时，请：
1. 在相应的子目录中创建测试文件
2. 更新该子目录的 README.md
3. 更新本文件的测试模块列表
4. 确保测试可以独立运行
5. 添加必要的文档说明

## 相关文档

- [项目主 README](../README.md)
- [对话记录功能文档](conversation/README.md)
- [URL播放功能文档](url_playback/README.md)
- [TTS文档](../docs/tts/)
