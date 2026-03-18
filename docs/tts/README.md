# 小爱音箱TTS功能文档

本目录包含小爱音箱TTS（文本转语音）功能的完整文档。

## 📚 文档索引

### 🚀 快速开始
**[README_TTS.md](README_TTS.md)** - 5分钟快速上手
- 基本用法示例
- API接口说明
- 常见问题解答

### 📖 完整指南
**[TTS_完整解决方案.md](TTS_完整解决方案.md)** - 深入理解TTS功能
- 两种TTS功能详解（播报 vs 执行命令）
- 完整的使用场景和示例
- 设备支持列表
- 常见问题详解

### 🔧 技术文档
**[TTS修复说明.md](TTS修复说明.md)** - 技术实现细节
- 问题分析和解决方案
- 代码实现说明
- MIoT接口调用方式

### ✅ 验证报告
**[功能验证报告.md](功能验证报告.md)** - 完整测试结果
- 所有功能的测试验证
- 不同命令的回应行为
- 重要发现和结论

### 🧪 测试指南
**[QUICK_TEST.md](QUICK_TEST.md)** - 测试和故障排查
- 三种测试方法
- 预期结果说明
- 故障排查指南

## 🎯 核心功能

### 1. TTS播报
播报文本消息，音箱只读出文本：
```python
await client.text_to_speech("您有新消息", device_id)
```

### 2. 执行命令
相当于对音箱说"小爱同学，<命令>"：
```python
await client.send_command("播放音乐", device_id)
```

### 3. 静默模式
静默执行命令，不要语音回应：
```python
await client.send_command("关灯", device_id, silent=True)
```

## 💡 重要提示

### 音箱回应说明
- **动作类命令**（播放音乐、唱歌）→ 执行具体动作
- **查询类命令**（时间、天气）→ 回应"好的"

**音箱回应"好的"是正常行为**，表示成功收到并确认命令！

## 🧪 运行测试

```bash
# 运行完整测试
python3 test/test_tts.py

# 查看测试结果
# ✓ TTS播报功能
# ✓ 命令执行功能（带回应）
# ✓ 命令执行功能（静默模式）
```

## 📦 相关文件

### 源代码
- `backend/src/xiaoai_media/client.py` - 核心实现
- `backend/src/xiaoai_media/api/routes/command.py` - API路由

### 测试
- `test/test_tts.py` - 自动化测试脚本

## 🔗 外部参考

- [MiService GitHub](https://github.com/Yonsm/MiService) - 小米云服务库
- [xiaomusic](https://github.com/hanxi/xiaomusic) - 小爱音箱播放器

---

**建议阅读顺序**：
1. 先看 [README_TTS.md](README_TTS.md) 快速上手
2. 遇到问题查看 [QUICK_TEST.md](QUICK_TEST.md)
3. 需要深入了解看 [TTS_完整解决方案.md](TTS_完整解决方案.md)
4. 技术细节参考 [TTS修复说明.md](TTS修复说明.md)
