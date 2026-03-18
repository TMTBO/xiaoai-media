# XiaoAi Media 文档中心

欢迎来到 XiaoAi Media 项目文档中心！

## 📚 文档目录

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

## 🚀 快速开始

### 安装和配置

1. 克隆项目：
```bash
git clone <repository-url>
cd xiaoai-media
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入小米账号信息
```

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

### TTS文本转语音
- ✅ TTS播报 - 播报文本消息
- ✅ 命令执行 - 执行语音命令
- ✅ 静默模式 - 静默执行命令

详细文档：[tts/README.md](tts/README.md)

### 音乐控制
- 播放/暂停
- 上一首/下一首
- 音量控制

### 设备管理
- 设备列表查询
- 设备状态监控
- 多设备支持

## 🧪 测试

### TTS功能测试
```bash
python3 test/test_tts.py
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
│   └── tts/             # TTS功能文档
├── test/                 # 测试脚本
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
