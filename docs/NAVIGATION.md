# 📖 文档导航

快速找到你需要的文档！

## 🎯 我想...

### 🎵 播放功能

#### 快速修复播放错误
→ [playback/播放错误快速修复.md](playback/播放错误快速修复.md)  
最快的播放错误修复方法

#### 了解代理URL使用
→ [playback/代理URL使用指南.md](playback/代理URL使用指南.md)  
如何使用代理URL播放音乐

#### 排查播放问题
→ [playback/PLAYBACK_TROUBLESHOOTING.md](playback/PLAYBACK_TROUBLESHOOTING.md)  
播放故障排查指南

#### 了解播放技术细节
→ [playback/代理URL封装说明.md](playback/代理URL封装说明.md)  
代理URL的技术实现

#### 浏览所有播放文档
→ [playback/README.md](playback/README.md)  
播放功能文档索引

### 🎤 TTS功能

#### 快速开始使用TTS功能
→ [tts/README_TTS.md](tts/README_TTS.md)  
5分钟快速上手，包含基本示例和API说明

#### 深入了解TTS功能
→ [tts/TTS_完整解决方案.md](tts/TTS_完整解决方案.md)  
完整的功能说明、使用场景和最佳实践

#### 解决TTS相关问题
→ [tts/QUICK_TEST.md](tts/QUICK_TEST.md)  
测试方法和故障排查指南

#### 了解技术实现细节
→ [tts/TTS修复说明.md](tts/TTS修复说明.md)  
技术实现、代码说明和MIoT接口调用

#### 查看测试验证结果
→ [tts/功能验证报告.md](tts/功能验证报告.md)  
完整的功能测试报告和验证结果

#### 浏览所有TTS文档
→ [tts/README.md](tts/README.md)  
TTS文档索引和概览

### 💬 对话监听功能

#### 快速开始使用对话监听
→ [conversation/QUICK_START.md](conversation/QUICK_START.md)  
对话监听快速入门

#### 了解对话监听功能
→ [conversation/功能说明.md](conversation/功能说明.md)  
对话监听的功能说明

#### 查看使用说明
→ [conversation/使用说明.md](conversation/使用说明.md)  
详细的使用指南

#### 浏览所有对话监听文档
→ [conversation/README.md](conversation/README.md)  
对话监听文档索引

### 📚 其他文档

#### 查看项目整体文档
→ [README.md](README.md)  
文档中心首页

#### 升级到新版 MiService
→ [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md)  
从 miservice 升级到 miservice_fork 的完整指南

#### 查看API接口文档
→ [API_REFERENCE.md](API_REFERENCE.md)  
所有API接口的详细说明

## 📚 按主题浏览

### 🎵 播放功能
```
playback/
├── README.md                    # 播放文档索引
├── 播放错误快速修复.md           # 快速修复指南
├── 播放错误修复说明.md           # 详细修复说明
├── 代理URL使用指南.md           # 代理使用指南
├── 代理URL封装说明.md           # 技术实现
├── PLAYBACK_FIX.md             # 修复文档（英文）
├── PLAYBACK_TROUBLESHOOTING.md # 故障排查
├── QUICK_PLAYBACK_GUIDE.md     # 快速指南
└── PROXY_URL_SUMMARY.md        # 代理封装总结
```

### 🎤 TTS功能
```
tts/
├── README.md                    # TTS文档索引
├── README_TTS.md               # 快速开始
├── TTS_完整解决方案.md          # 完整指南
├── TTS修复说明.md              # 技术文档
├── 功能验证报告.md              # 测试报告
└── QUICK_TEST.md               # 测试指南
```

### 💬 对话监听功能
```
conversation/
├── README.md                    # 对话监听索引
├── QUICK_START.md              # 快速开始
├── 功能说明.md                  # 功能说明
├── 使用说明.md                  # 使用指南
├── 修复说明.md                  # 修复文档
└── ...                         # 其他文档
```

### 📖 其他文档
```
├── MISERVICE_MIGRATION.md      # 迁移说明
├── UPGRADE_GUIDE.md            # 升级指南
├── API_REFERENCE.md            # API接口参考
└── BEFORE_AFTER.md             # 升级前后对比
```

## 🔍 按角色查找

### 我是开发者

#### 播放功能
1. [代理URL使用指南](playback/代理URL使用指南.md) - 了解如何使用代理
2. [代理URL封装说明](playback/代理URL封装说明.md) - 了解技术实现
3. [测试指南](playback/README.md#测试) - 运行测试

#### TTS功能
1. [快速开始](tts/README_TTS.md) - 了解基本用法
2. [技术文档](tts/TTS修复说明.md) - 了解实现细节
3. [测试指南](tts/QUICK_TEST.md) - 运行测试

#### 对话监听
1. [快速开始](conversation/QUICK_START.md) - 了解基本用法
2. [功能说明](conversation/功能说明.md) - 了解功能细节

### 我是用户

#### 播放功能
1. [快速修复](playback/播放错误快速修复.md) - 解决播放问题
2. [故障排查](playback/PLAYBACK_TROUBLESHOOTING.md) - 排查问题

#### TTS功能
1. [快速开始](tts/README_TTS.md) - 学习如何使用
2. [完整指南](tts/TTS_完整解决方案.md) - 了解所有功能
3. [故障排查](tts/QUICK_TEST.md#故障排查) - 解决问题

#### 对话监听
1. [使用说明](conversation/使用说明.md) - 学习如何使用
2. [快速参考](conversation/快速参考.md) - 快速查找

### 我是测试人员

#### 播放功能
1. [测试脚本](../test/music/playback/) - 播放测试
2. [诊断工具](../test/music/playback/diagnose_playback.py) - 诊断问题

#### TTS功能
1. [测试指南](tts/QUICK_TEST.md) - 测试方法
2. [验证报告](tts/功能验证报告.md) - 测试结果
3. [技术文档](tts/TTS修复说明.md) - 技术背景

#### 对话监听
1. [测试脚本](../test/conversation/) - 对话监听测试
2. [测试报告](conversation/TEST_REPORT.md) - 测试结果

## 🆘 常见问题快速链接

### 播放相关

#### 播放失败显示"播放错误"？
→ [播放错误快速修复.md](playback/播放错误快速修复.md)

#### 如何使用代理URL？
→ [代理URL使用指南.md](playback/代理URL使用指南.md)

#### 播放问题如何排查？
→ [PLAYBACK_TROUBLESHOOTING.md](playback/PLAYBACK_TROUBLESHOOTING.md)

### TTS相关

#### 音箱只回应"好的"？
→ [TTS_完整解决方案.md#常见问题](tts/TTS_完整解决方案.md#常见问题)

#### 如何播报文本？
→ [README_TTS.md#TTS播报](tts/README_TTS.md#1-tts播报播报文本)

#### 如何执行命令？
→ [README_TTS.md#执行命令](tts/README_TTS.md#2-执行命令相当于说小爱同学)

#### 如何静默执行？
→ [TTS_完整解决方案.md#场景3](tts/TTS_完整解决方案.md#场景3执行命令静默)

#### 测试失败怎么办？
→ [QUICK_TEST.md#故障排查](tts/QUICK_TEST.md#故障排查)

### 对话监听相关

#### 如何启用对话监听？
→ [使用说明.md](conversation/使用说明.md)

#### 对话拦截如何工作？
→ [功能说明.md](conversation/功能说明.md)

## 📱 快速命令

```bash
# 查看所有文档
ls -R docs/

# 搜索文档内容
grep -r "关键词" docs/

# 播放功能测试
python test/music/playback/diagnose_playback.py
python test/music/playback/test_proxy_function.py

# TTS功能测试
python test/tts/test_tts.py

# 对话监听测试
python test/conversation/test_conversation_monitoring.py
```

## 🔄 文档更新

最后更新：2026-03-19

---

**提示**：使用 Ctrl+F (或 Cmd+F) 在本页面搜索关键词快速定位！
