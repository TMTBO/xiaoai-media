# 快速测试指南 (Quick Test Guide)

## 测试TTS功能

### 方法1：运行测试脚本
```bash
python3 test/test_tts.py
```

### 方法2：Python交互式测试

#### TTS播报（只播报文本）
```python
import asyncio
import sys
sys.path.insert(0, "backend/src")

from xiaoai_media.client import XiaoAiClient

async def test_broadcast():
    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        device_id = devices[0]["deviceID"]
        
        # TTS播报 - 只播报文本
        result = await client.text_to_speech("你好", device_id)
        print(result)

asyncio.run(test_broadcast())
```

#### 执行命令（带语音回应）
```python
async def test_command():
    async with XiaoAiClient() as client:
        devices = await client.list_devices()
        device_id = devices[0]["deviceID"]
        
        # 执行命令 - 带语音回应
        result = await client.send_command("查询天气", device_id)
        print(result)
        
        # 执行命令 - 静默模式
        result = await client.send_command("关灯", device_id, silent=True)
        print(result)

asyncio.run(test_command())
```

### 方法3：通过API测试

1. 启动后端服务：
```bash
cd backend
python3 -m uvicorn xiaoai_media.api.main:app --reload
```

2. TTS播报：
```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好", "device_id": "YOUR_DEVICE_ID"}'
```

3. 执行命令（带语音回应）：
```bash
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{"text": "查询天气", "device_id": "YOUR_DEVICE_ID", "silent": false}'
```

4. 执行命令（静默模式）：
```bash
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{"text": "关灯", "device_id": "YOUR_DEVICE_ID", "silent": true}'
```

## 两种功能对比

| 功能 | 方法 | 参数 | 音箱行为 | 使用场景 |
|-----|------|------|---------|---------|
| TTS播报 | `text_to_speech()` | 文本 | 只播报文本 | 通知、消息播报 |
| 执行命令 | `send_command()` | 文本 + silent标志 | 执行命令并可选回应 | 查询、控制设备 |

## 预期结果

### TTS播报成功
```json
{
  "device": "设备名称(device_id)",
  "miot_did": "2085689284",
  "command": "你好",
  "result": 0,
  "method": "miot_action"
}
```

### 执行命令成功（带回应）
```json
{
  "device": "设备名称(device_id)",
  "miot_did": "2085689284",
  "command": "查询天气",
  "result": 0,
  "method": "miot_action_execute",
  "silent": false
}
```

### 执行命令成功（静默）
```json
{
  "device": "设备名称(device_id)",
  "miot_did": "2085689284",
  "command": "关灯",
  "result": 0,
  "method": "miot_action_execute",
  "silent": true
}
```

其中：
- `result: 0` 表示成功
- `method: "miot_action"` 表示TTS播报
- `method: "miot_action_execute"` 表示执行命令
- `method: "mina_service"` 表示使用了降级方案（也是成功的）

## 故障排查

### 问题1：找不到设备
```
No devices found!
```
**解决**：检查`.env`文件中的`MI_USER`和`MI_PASS_TOKEN`是否正确。

### 问题2：音箱没有回应
**原因**：可能使用了TTS播报而不是执行命令。
**解决**：
- 如果想要音箱回应，使用`send_command(text, device_id)`
- 如果只想播报文本，使用`text_to_speech(text, device_id)`

### 问题3：想要静默执行
**解决**：使用`send_command(text, device_id, silent=True)`

### 问题4：miot_action失败，降级到MiNAService
```
WARNING - MiService: miot_action failed (...), trying MiNAService fallback
```
**说明**：这是正常的降级行为，TTS仍然可以工作。可能原因：
- 设备硬件型号不在映射中
- 设备不支持MIoT接口

### 问题5：所有方法都失败
```
ERROR - MiService: All TTS methods failed
```
**解决**：
1. 检查设备是否在线
2. 检查网络连接
3. 检查小米账号权限

## 查看日志

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 支持的命令示例

### TTS播报（只播报）
- `"你好"`
- `"测试成功"`
- `"温度已达到25度"`
- `"您有新消息"`

### 执行命令效果说明

| 命令类型 | 示例命令 | 音箱回应 | 说明 |
|---------|---------|---------|------|
| 动作类 | "播放音乐" | 播放音乐 | 执行具体动作 |
| 动作类 | "唱首歌" | 唱歌 | 执行具体动作 |
| 动作类 | "暂停" | 暂停播放 | 执行具体动作 |
| 查询类 | "现在几点" | "好的" | 确认收到命令 |
| 查询类 | "今天天气" | "好的" | 确认收到命令 |
| 查询类 | "今天星期几" | "好的" | 确认收到命令 |
| 娱乐类 | "讲个笑话" | "好的" | 确认收到命令 |
| 娱乐类 | "讲个故事" | "好的" | 确认收到命令 |

**注意**：
- 音箱回应"好的"表示成功收到并确认命令，这是正常行为
- 某些查询类命令可能需要特定格式或触发词才能得到详细回应
- 如果只想播报文本而不执行命令，使用`text_to_speech()`

### 执行命令（静默）
- `"关灯"` (silent=True)
- `"打开空调"` (silent=True)
- `"关闭电视"` (silent=True)
