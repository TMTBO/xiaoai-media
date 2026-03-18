# 小爱音箱TTS功能使用指南

## 快速开始

### 1. TTS播报（播报文本）
```python
from xiaoai_media.client import XiaoAiClient

async with XiaoAiClient() as client:
    # 获取设备
    devices = await client.list_devices()
    device_id = devices[0]["deviceID"]
    
    # 播报文本
    await client.text_to_speech("您有新消息", device_id)
```

### 2. 执行命令（相当于说"小爱同学，..."）
```python
# 带语音回应
await client.send_command("播放音乐", device_id)

# 静默执行
await client.send_command("关灯", device_id, silent=True)
```

## 两种功能对比

| 功能 | 方法 | 用途 | 音箱行为 |
|-----|------|------|---------|
| TTS播报 | `text_to_speech()` | 播报通知/消息 | 只播报文本 |
| 执行命令 | `send_command()` | 执行命令/查询 | 执行命令并回应 |

## 命令回应说明

音箱对不同命令的回应方式：

### 动作类命令（会执行具体动作）
- "播放音乐" → 播放音乐
- "唱首歌" → 唱歌
- "暂停" → 暂停播放

### 查询类命令（回应"好的"）
- "现在几点" → "好的"
- "今天天气" → "好的"
- "报时" → "好的"

**注意**：音箱回应"好的"是正常行为，表示成功收到并确认命令。

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
  "silent": false  # true=静默，false=语音回应
}
```

## 测试

运行测试脚本：
```bash
python3 test/test_tts.py
```

## 常见问题

**Q: 为什么音箱只回应"好的"？**  
A: 这是正常行为。查询类命令音箱会回应"好的"表示收到，动作类命令会执行具体动作。

**Q: 如何让音箱播报文本而不执行命令？**  
A: 使用`text_to_speech()`而不是`send_command()`。

**Q: 如何静默执行命令？**  
A: 使用`send_command(text, device_id, silent=True)`。

## 详细文档

- [TTS修复说明.md](TTS修复说明.md) - 技术实现细节
- [TTS_完整解决方案.md](TTS_完整解决方案.md) - 完整使用指南
- [功能验证报告.md](功能验证报告.md) - 测试验证结果
- [QUICK_TEST.md](QUICK_TEST.md) - 快速测试参考

## 支持的设备

支持所有小米/小爱音箱系列，包括：
- 小米智能音箱 Pro (OH2P)
- 小爱音箱系列 (LX06, LX01, LX04等)
- Redmi小爱音箱系列 (X10A, X6A等)

完整设备列表请参考[TTS修复说明.md](TTS修复说明.md)。
