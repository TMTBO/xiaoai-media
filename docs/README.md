# XiaoAi Media 文档中心

欢迎来到 XiaoAi Media 项目文档中心！

## 📚 文档目录

### 🎵 播放功能文档
**[playback/](playback/)** - 音乐播放功能完整文档

小爱音箱播放功能的完整使用指南，包括：
- 播放错误修复方案
- 代理URL使用指南
- 故障排查指南
- 技术实现细节

**快速链接**：
- [播放错误快速修复](playback/播放错误快速修复.md)
- [代理URL使用指南](playback/代理URL使用指南.md)
- [故障排查指南](playback/PLAYBACK_TROUBLESHOOTING.md)

### 🎤 TTS功能文档
**[tts/](tts/)** - 文本转语音功能完整文档

小爱音箱TTS功能的完整使用指南，包括：
- 快速开始指南
- 完整功能说明
- 技术实现细节
- 测试验证报告
- 故障排查指南

**快速链接**：
- [5分钟快速上手](tts/README_TTS.md)
- [完整解决方案](tts/TTS_完整解决方案.md)
- [功能验证报告](tts/功能验证报告.md)

### 💬 对话监听文档
**[conversation/](conversation/)** - 对话拦截和自动播放功能

对话监听功能的完整文档，包括：
- 功能说明和使用指南
- 播放拦截实现
- 问题修复报告
- 验证测试报告

**快速链接**：
- [快速开始](conversation/QUICK_START.md)
- [功能说明](conversation/功能说明.md)
- [使用说明](conversation/使用说明.md)

### ⚙️ 配置系统文档
**配置系统** - 用户配置和唤醒词功能

配置系统的完整文档，包括：
- 快速配置指南
- 完整配置说明
- 常见问题解答
- 迁移指南

**快速链接**：
- [快速配置指南](QUICK_CONFIG.md)
- [完整配置指南](USER_CONFIG_GUIDE.md)
- [配置常见问题](CONFIG_FAQ.md)
- [配置问题解答](CONFIG_ANSWERS.md)
- [迁移文档](migration/) - 从 .env 迁移到 user_config.py

## 🚀 快速开始

### 安装和配置

1. 克隆项目：
```bash
git clone <repository-url>
cd xiaoai-media
```

2. 配置环境：
```bash
# 复制配置模板
cp user_config_template.py user_config.py

# 编辑配置文件
vim user_config.py
```

详细配置说明：[快速配置指南](QUICK_CONFIG.md)

3. 启动服务：
```bash
# 后端
cd backend
python3 -m uvicorn xiaoai_media.api.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 基本使用

```python
from xiaoai_media.client import XiaoAiClient

async with XiaoAiClient() as client:
    # 获取设备列表
    devices = await client.list_devices()
    device_id = devices[0]["deviceID"]
    
    # TTS播报
    await client.text_to_speech("您有新消息", device_id)
    
    # 执行命令
    await client.send_command("播放音乐", device_id)
```

## 📖 功能模块

### 🎵 音乐播放
- ✅ 搜索和播放 - 搜索音乐并播放
- ✅ 播放控制 - 播放/暂停/上一首/下一首
- ✅ 代理播放 - 通过代理访问音乐URL
- ✅ 排行榜 - 播放各平台排行榜

详细文档：[playback/README.md](playback/README.md)

### 🎤 TTS文本转语音
- ✅ TTS播报 - 播报文本消息
- ✅ 命令执行 - 执行语音命令
- ✅ 静默模式 - 静默执行命令

详细文档：[tts/README.md](tts/README.md)

### 💬 对话监听
- ✅ 对话拦截 - 自动拦截播放指令
- ✅ 自动播放 - 通过本服务获取音乐URL
- ✅ 实时监听 - 持续监听音箱对话

详细文档：[conversation/README.md](conversation/README.md)

### 🔊 音量控制
- 获取音量
- 设置音量

### 📱 设备管理
- 设备列表查询
- 设备状态监控
- 多设备支持

## 🧪 测试

### 播放功能测试
```bash
# 诊断播放问题
python test/music/playback/diagnose_playback.py

# 测试代理函数
python test/music/playback/test_proxy_function.py
```

### TTS功能测试
```bash
python test/tts/test_tts.py
```

### 对话监听测试
```bash
python test/conversation/test_conversation_monitoring.py
```

## 🔧 API文档

### 核心接口

#### TTS播报
```http
POST /tts
Content-Type: application/json

{
  "text": "您好",
  "device_id": "xxx"
}
```

#### 执行命令
```http
POST /command
Content-Type: application/json

{
  "text": "播放音乐",
  "device_id": "xxx",
  "silent": false
}
```

#### 音量控制
```http
POST /volume
Content-Type: application/json

{
  "volume": 50,
  "device_id": "xxx"
}
```

#### 设备列表
```http
GET /devices
```

## 🎯 支持的设备

- 小米智能音箱 Pro (OH2P)
- 小爱音箱系列 (LX06, LX01, LX04等)
- Redmi小爱音箱系列 (X10A, X6A等)

完整设备列表请参考 [TTS文档](tts/TTS修复说明.md#支持的设备)。

## 🛠️ 技术栈

### 后端
- Python 3.7+
- FastAPI
- aiohttp
- miservice

### 前端
- Vue.js
- TypeScript
- Vite

## 📦 项目结构

```
xiaoai-media/
├── backend/              # 后端服务
│   └── src/
│       └── xiaoai_media/
│           ├── api/      # API路由
│           ├── client.py # 核心客户端
│           └── config.py # 配置
├── frontend/             # 前端界面
├── docs/                 # 文档（本目录）
│   ├── playback/        # 播放功能文档
│   ├── tts/             # TTS功能文档
│   └── conversation/    # 对话监听文档
├── test/                 # 测试脚本
│   ├── music/           # 音乐功能测试
│   │   └── playback/    # 播放功能测试
│   ├── tts/             # TTS功能测试
│   └── conversation/    # 对话监听测试
└── README.md            # 项目说明
```

## 🔗 外部资源

- [MiService](https://github.com/Yonsm/MiService) - 小米云服务库
- [xiaomusic](https://github.com/hanxi/xiaomusic) - 小爱音箱播放器

## 📝 贡献指南

欢迎贡献代码和文档！

## 📄 License

MIT

---

**文档更新日期**：2026-03-18
