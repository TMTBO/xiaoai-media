# XiaoAi Media

小爱音箱媒体控制系统

## 功能特性

- 🎵 音乐播放控制
- 🔊 音量控制
- 💬 TTS文本转语音
- 🎤 语音命令执行
- 📱 设备管理
- 🎧 **对话监听** - 自动拦截音箱播放指令，通过本服务获取音乐 URL

## 快速开始

### 环境配置

本项目使用 Python 配置文件进行配置。

1. 复制配置模板：
```bash
cp user_config_template.py user_config.py
```

2. 编辑 `user_config.py`，填入配置信息：
```python
MI_USER = "你的小米账号"
MI_PASS = "你的密码"
MI_DID = ""  # 设备ID（可选）
MI_REGION = "cn"

# 唤醒词配置
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

详细配置说明请查看：[用户配置指南](docs/USER_CONFIG_GUIDE.md)

### 验证配置

```bash
make verify-config
```

### 启动后端服务

```bash
cd backend
python3 -m uvicorn xiaoai_media.api.main:app --reload
```

### 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

## 文档

完整文档请查看：**[docs/](docs/)**

### 快速链接
- 📖 [文档中心](docs/README.md) - 所有文档的入口
- ⚙️ [用户配置指南](docs/USER_CONFIG_GUIDE.md) - 配置说明和唤醒词设置
- 🔄 [配置迁移指南](docs/migration/MIGRATION_TO_USER_CONFIG.md) - 从 .env 迁移到 user_config.py
- 🎤 [TTS功能文档](docs/tts/) - TTS完整使用指南
- 🎧 [对话监听功能](docs/conversation_monitoring.md) - 自动拦截播放指令
- 🧭 [文档导航](docs/NAVIGATION.md) - 快速找到你需要的文档

### TTS功能文档
- [快速开始](docs/tts/README_TTS.md) - 5分钟上手
- [完整指南](docs/tts/TTS_完整解决方案.md) - 深入了解
- [测试指南](docs/tts/QUICK_TEST.md) - 测试和故障排查
- [技术文档](docs/tts/TTS修复说明.md) - 实现细节
- [验证报告](docs/tts/功能验证报告.md) - 测试结果

## TTS功能

本项目支持完整的TTS（文本转语音）功能，包括：

- **TTS播报** - 播报文本消息
- **命令执行** - 相当于对音箱说"小爱同学，..."
- **静默模式** - 静默执行命令

### 快速示例

```python
from xiaoai_media.client import XiaoAiClient

async with XiaoAiClient() as client:
    devices = await client.list_devices()
    device_id = devices[0]["deviceID"]
    
    # TTS播报
    await client.text_to_speech("您有新消息", device_id)
    
    # 执行命令
    await client.send_command("播放音乐", device_id)
    
    # 静默执行
    await client.send_command("关灯", device_id, silent=True)
```

### 详细文档

完整的TTS功能文档请查看：**[docs/tts/](docs/tts/)**

快速链接：
- [快速开始指南](docs/tts/README_TTS.md) - 5分钟上手
- [完整解决方案](docs/tts/TTS_完整解决方案.md) - 深入了解所有功能
- [技术实现说明](docs/tts/TTS修复说明.md) - 代码和技术细节
- [功能验证报告](docs/tts/功能验证报告.md) - 完整测试结果
- [测试指南](docs/tts/QUICK_TEST.md) - 测试方法和故障排查

## API接口

### TTS播报
```bash
POST /tts
{
  "text": "您好",
  "device_id": "xxx"
}
```

### 执行命令
```bash
POST /command
{
  "text": "播放音乐",
  "device_id": "xxx",
  "silent": false
}
```

### 音量控制
```bash
POST /volume
{
  "volume": 50,
  "device_id": "xxx"
}
```

### 设备列表
```bash
GET /devices
```

## 测试

运行TTS功能测试：
```bash
python3 test/test_tts.py
```

## 项目结构

```
xiaoai-media/
├── backend/              # 后端服务
│   └── src/
│       └── xiaoai_media/
│           ├── api/      # API路由
│           ├── client.py # 核心客户端
│           └── config.py # 配置
├── frontend/             # 前端界面
├── docs/                 # 文档
│   └── tts/             # TTS功能文档
├── test/                 # 测试脚本
└── README.md            # 本文件
```

## 支持的设备

支持所有小米/小爱音箱系列，包括：
- 小米智能音箱 Pro (OH2P)
- 小爱音箱系列 (LX06, LX01, LX04等)
- Redmi小爱音箱系列 (X10A, X6A等)

## 技术栈

### 后端
- Python 3.7+
- FastAPI
- aiohttp
- miservice_fork (yihong0618/MiService)

### 前端
- Vue.js
- TypeScript
- Vite

## 参考资料

- [MiService Fork](https://github.com/yihong0618/MiService) - 增强版小米云服务库
- [MiService](https://github.com/Yonsm/MiService) - 原版小米云服务库
- [xiaomusic](https://github.com/hanxi/xiaomusic) - 小爱音箱播放器

## License

MIT
