# 小爱音箱TTS功能完整解决方案

## 核心发现

小爱音箱的MIoT接口有两种不同的TTS功能，需要区别对待：

### 1. TTS播报 (aiid=1或3)
- **用途**：单纯播报文本
- **参数**：只需要文本
- **示例**：`micli.py 5 您好`
- **特点**：音箱会播报文本，但不会执行命令或回应

### 2. 执行文本命令 (aiid=4)
- **用途**：相当于对音箱说"小爱同学，<文本>"
- **参数**：文本 + 响应标志（1=语音回应，0=静默）
- **示例**：
  - `micli.py 5-4 查询天气 1` - 带语音回应
  - `micli.py 5-4 关灯 0` - 静默执行
- **特点**：音箱会执行命令并根据响应标志决定是否语音回应

## 实现方案

### 1. 添加两个命令映射

```python
# TTS播报映射 (aiid=1或3)
TTS_COMMAND = {
    "OH2P": "7-3",  # 小米智能音箱Pro
    "LX06": "5-1",  # 小爱音箱
    # ... 其他设备
}

# 执行命令映射 (aiid=4)
EXECUTE_COMMAND = {
    "OH2P": "7-4",  # 小米智能音箱Pro
    "LX06": "5-4",  # 小爱音箱
    # ... 其他设备
}
```

### 2. 实现两个方法

```python
# TTS播报 - 只播报文本
async def text_to_speech(text, device_id):
    """播报文本，不执行命令"""
    siid, aiid = 7, 3  # 从TTS_COMMAND获取
    result = await miot_action(did, (siid, aiid), [text])
    return result

# 执行命令 - 相当于说"小爱同学，<文本>"
async def execute_text_command(text, device_id, silent=False):
    """执行命令，可控制是否语音回应"""
    siid, aiid = 7, 4  # 从EXECUTE_COMMAND获取
    response_flag = 0 if silent else 1
    result = await miot_action(did, (siid, aiid), [text, response_flag])
    return result

# 发送命令 - 调用execute_text_command
async def send_command(text, device_id, silent=False):
    """发送语音命令"""
    return await execute_text_command(text, device_id, silent)
```

## 使用场景

### 场景1：播报通知/消息
使用`text_to_speech()`，音箱只播报文本：
```python
await client.text_to_speech("您有新消息", device_id)
await client.text_to_speech("温度已达到25度", device_id)
```

### 场景2：执行命令（带回应）
使用`send_command()`，音箱会执行命令并语音回应：
```python
await client.send_command("播放音乐", device_id)      # 音箱会播放音乐
await client.send_command("唱首歌", device_id)        # 音箱会唱歌
await client.send_command("现在几点", device_id)      # 音箱会回应"好的"
await client.send_command("今天天气", device_id)      # 音箱会回应"好的"
```

**注意**：不同命令的回应方式不同：
- **动作类命令**（播放音乐、唱歌等）：音箱会执行具体动作
- **查询类命令**（时间、天气等）：音箱可能只回应"好的"表示收到命令
- 某些查询可能需要特定的触发词或格式才能得到详细回应

### 场景3：执行命令（静默）
使用`send_command(silent=True)`，音箱静默执行：
```python
await client.send_command("关灯", device_id, silent=True)
await client.send_command("打开空调", device_id, silent=True)
```

## API接口

### 1. TTS播报接口
```bash
POST /tts
{
  "text": "您好",
  "device_id": "xxx"
}
```

### 2. 命令执行接口
```bash
POST /command
{
  "text": "查询天气",
  "device_id": "xxx",
  "silent": false  # true=静默，false=语音回应
}
```

## 测试验证

运行测试：
```bash
python3 test/test_tts.py
```

测试覆盖：
- ✓ TTS播报功能
- ✓ 命令执行（带语音回应）
- ✓ 命令执行（静默模式）

## 关键要点

1. **区分两种功能**：播报 vs 执行命令
2. **不同的aiid**：aiid=1/3用于播报，aiid=4用于执行
3. **参数数量不同**：
   - 播报：1个参数（文本）
   - 执行：2个参数（文本 + 响应标志）
4. **响应标志**：1=语音回应，0=静默执行
5. **降级方案**：失败时自动降级到MiNAService

## 常见问题

### Q: 为什么音箱只回应"好的"？
A: 这是正常行为。不同命令的回应方式不同：
- **动作类命令**（播放音乐、唱歌）：音箱会执行具体动作
- **查询类命令**（时间、天气）：音箱可能只回应"好的"表示收到
- 如果只想播报文本而不执行命令，使用`text_to_speech()`

### Q: 为什么音箱没有回应？
A: 可能使用了TTS播报（aiid=1/3）而不是执行命令（aiid=4）。TTS播报只播报文本，不会执行命令或回应。应该使用`send_command()`而不是`text_to_speech()`。

### Q: 如何让音箱静默执行命令？
A: 使用`send_command(text, device_id, silent=True)`，设置`silent=True`。

### Q: 两种方法有什么区别？
A:
- `text_to_speech()` - 播报文本，音箱只读出文本
- `send_command()` - 执行命令，相当于说"小爱同学，<文本>"

### Q: 什么时候用哪个方法？
A:
- 播报通知/消息 → `text_to_speech()`
- 执行命令/查询 → `send_command()`

## 参考文档

- [MiService GitHub](https://github.com/Yonsm/MiService)
- MiService README 第7节：动作调用TTS 播报和执行文本
