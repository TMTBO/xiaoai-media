# XiaoAi Media 文档中心

欢迎来到 XiaoAi Media 项目文档中心！

## 📚 快速导航

- **[文档结构说明](STRUCTURE.md)** - 完整的文档组织结构
- **[文档索引](INDEX.md)** - 按主题查找文档
- **[导航指南](NAVIGATION.md)** - 功能导航地图

## 🚀 快速开始

1. [快速配置指南](config/QUICK_CONFIG.md) - 5 分钟配置完成
2. [快速播放测试](playback/QUICK_PLAYBACK_GUIDE.md) - 测试音乐播放
3. [TTS 快速测试](tts/QUICK_TEST.md) - 测试语音播报

## 📖 功能文档

### ⚙️ 配置管理
**[config/](config/)** - 配置系统完整文档

- [配置管理 API](config/CONFIG_API.md) - 通过管理后台管理配置
- [用户配置指南](config/USER_CONFIG_GUIDE.md) - 详细配置说明
- [配置常见问题](config/CONFIG_FAQ.md) - 配置问题排查
- [配置速查表](config/CONFIG_CHEATSHEET.md) - 配置项速查

### 🎵 播放功能
**[playback/](playback/)** - 音乐播放功能完整文档

- [快速播放指南](playback/QUICK_PLAYBACK_GUIDE.md) - 快速上手
- [播放故障排查](playback/PLAYBACK_TROUBLESHOOTING.md) - 问题诊断
- [代理 URL 使用](playback/代理URL使用指南.md) - 代理功能说明
- [播放错误修复](playback/播放错误修复说明.md) - 错误解决方案

### 📝 播放列表
**[playlist/](playlist/)** - 播放列表功能文档

- [播放列表指南](playlist/PLAYLIST_GUIDE.md) - 播放列表使用
- [功能更新说明](playlist/PLAYLIST_FEATURE_UPDATE.md) - 最新功能
- [功能改进记录](playlist/PLAYLIST_IMPROVEMENTS.md) - 改进历史

### 🎤 TTS 语音播报
**[tts/](tts/)** - 文本转语音功能完整文档

- [TTS 功能概览](tts/README.md) - 功能介绍
- [快速测试指南](tts/QUICK_TEST.md) - 5 分钟测试
- [完整解决方案](tts/TTS_完整解决方案.md) - 深入了解
- [功能验证报告](tts/功能验证报告.md) - 测试结果

### 💬 对话监听
**[conversation/](conversation/)** - 对话拦截和自动播放功能

- [快速开始](conversation/QUICK_START.md) - 快速配置
- [用户指南](conversation/USER_GUIDE.md) - 完整使用指南
- [功能说明](conversation/功能说明.md) - 功能详解
- [快速参考](conversation/快速参考.md) - 常用命令

### 🔧 API 开发
**[api/](api/)** - API 接口文档

- [API 参考手册](api/API_REFERENCE.md) - 完整 API 文档
- [API 实现说明](api/API实现说明.md) - 实现细节

### 🔄 迁移与升级
**[migration/](migration/)** - 迁移和升级指南

- [MiService 迁移](migration/MISERVICE_MIGRATION.md) - MiService 迁移
- [配置迁移指南](migration/MIGRATION_TO_USER_CONFIG.md) - 配置迁移
- [升级指南](UPGRADE_GUIDE.md) - 版本升级

## 🔍 问题排查

遇到问题？查看这些文档：

- [配置常见问题](config/CONFIG_FAQ.md) - 配置相关问题
- [播放故障排查](playback/PLAYBACK_TROUBLESHOOTING.md) - 播放问题
- [TTS 修复说明](tts/TTS修复说明.md) - TTS 问题

## 📊 项目信息

- [改进前后对比](BEFORE_AFTER.md) - 项目改进历史
- [代码组织报告](ORGANIZATION_REPORT.md) - 代码结构
- [组织摘要](ORGANIZATION_SUMMARY.md) - 架构概览

## 💡 贡献指南

文档维护原则请参考 [文档结构说明](STRUCTURE.md)。
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
