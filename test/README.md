# 功能测试目录

本目录包含小爱音箱媒体控制系统的功能测试、端到端测试和手动测试脚本。

---

## 📂 测试目录说明

项目包含两个测试目录：

### 1. `backend/tests/` - 单元测试和集成测试
包含后端核心功能的单元测试和集成测试，使用 pytest 框架。
详见：[backend/tests/README.md](../backend/tests/README.md)

### 2. `test/` - 功能测试和端到端测试（本目录）
包含完整功能的端到端测试、手动测试脚本和测试文档。

---

## 📋 目录结构

```
test/
├── README.md                    # 本文件
├── test_auth.py                 # 认证功能测试
├── test_batch_import.sh         # 批量导入测试脚本
├── test_scheduler.sh            # 定时任务测试脚本
├── check_volumes.sh             # Docker卷检查脚本
├── debug_volumes.py             # 卷调试工具
│
├── command/                     # 命令处理测试
│   ├── README.md
│   ├── test_playing_block.py
│   └── test_response_flag.py
│
├── config/                      # 配置测试
│   └── test_data_dir.py
│
├── conversation/                # 对话记录功能测试
│   ├── README.md
│   ├── test_conversation.sh
│   ├── test_*.py
│   ├── FEATURE_SPEC.md
│   ├── TEST_REPORT.md
│   └── USER_GUIDE.md
│
├── music/                       # 音乐功能测试
│   ├── test_api_direct.py
│   ├── test_music_provider.py
│   └── test_*.py
│
├── playback/                    # 播放功能测试
│   └── test_audio_id_timestamp.py
│
├── playlist/                    # 播单功能测试
│   └── test_storage_refactor.py
│
├── tts/                         # TTS功能测试
│   └── test_tts.py
│
├── url_playback/                # URL播放功能测试
│   ├── README.md
│   ├── test_complete_flow.py
│   ├── test_api_play.py
│   └── ...
│
└── wake_word/                   # 唤醒词测试
```

---

## 🧪 测试模块

### 1. 认证功能测试
**文件**: `test_auth.py`

测试用户认证和授权功能。

```bash
python test/test_auth.py
```

### 2. 对话记录功能测试
**目录**: `conversation/`

测试小爱音箱对话历史记录功能，包括：
- 对话监听和拦截
- 播放指令识别
- 端到端流程测试

```bash
cd test/conversation
./test_conversation.sh
```

详细信息：[conversation/README.md](conversation/README.md)

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
```

详细信息：[url_playback/README.md](url_playback/README.md)

### 4. TTS 功能测试
**目录**: `tts/`

测试文字转语音功能。

```bash
python test/tts/test_tts.py
```

### 5. 命令处理测试
**目录**: `command/`

测试命令处理逻辑，包括：
- 播放阻塞机制
- 响应标志处理

```bash
python test/command/test_playing_block.py
python test/command/test_response_flag.py
```

### 6. 音乐功能测试
**目录**: `music/`

测试音乐搜索、获取和播放功能。

```bash
python test/music/test_music_provider.py
python test/music/test_api_direct.py
```

---

## 🚀 运行测试

### 运行所有功能测试

```bash
# 认证测试
python test/test_auth.py

# 对话记录测试
cd test/conversation && ./test_conversation.sh && cd ../..

# URL播放测试
for test in test/url_playback/test_*.py; do
    echo "Running $test..."
    python "$test"
done

# TTS测试
python test/tts/test_tts.py
```

### 运行批量导入测试

```bash
./test/test_batch_import.sh
```

### 运行定时任务测试

```bash
./test/test_scheduler.sh
```

---

## 🔧 测试环境要求

### 环境变量
```bash
export MI_USER=<your_xiaomi_account>
export MI_PASS=<your_password>
export MI_DID=<device_id>
```

或在项目根目录创建 `user_config.py`（从 `user_config_template.py` 复制）。

### 依赖服务
- 后端服务: http://localhost:8000
- 前端服务: http://localhost:5173
- 音乐API服务: http://localhost:5050

### Python 环境
- Python 3.10+
- 虚拟环境已激活
- 已安装所有依赖 (`pip install -e backend/`)

---

## 📊 测试状态

| 模块 | 状态 | 最后更新 |
|------|------|----------|
| 认证功能 | ✅ 通过 | 2026-03-31 |
| 对话记录 | ✅ 通过 | 2026-03-18 |
| URL播放 | ✅ 通过 | 2026-03-18 |
| TTS功能 | ✅ 通过 | 2026-03-18 |
| 命令处理 | ✅ 通过 | 2026-03-31 |

---

## 📝 贡献指南

添加新测试时，请：
1. 在相应的子目录中创建测试文件
2. 更新该子目录的 README.md
3. 更新本文件的测试模块列表
4. 确保测试可以独立运行
5. 添加必要的文档说明

---

## 📚 相关文档

- [单元测试目录](../backend/tests/README.md) - 单元测试和集成测试
- [项目主 README](../README.md)
- [对话记录功能文档](conversation/README.md)
- [URL播放功能文档](url_playback/README.md)
- [项目结构](../docs/STRUCTURE.md)

---

**最后更新**: 2026-03-31
