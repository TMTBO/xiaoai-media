# TTS功能修复说明

## 问题描述

在使用`text_to_speech`方法时，通过`miio_command`调用MIoT接口失败，返回错误：
```
Error: {'code': -8, 'message': 'data type not valid', 'result': None}
```

另外，发送语音到音箱后没有回应，需要支持响应标志参数。

## 问题分析

参考[MiService文档](https://github.com/Yonsm/MiService)第7节"动作调用：TTS 播报和执行文本"，发现有两种不同的TTS功能：

### 1. TTS播报 (TTS Broadcast)
```bash
micli.py 5 您好  # siid=5, aiid=1（默认）
```
- 只播报文本，不执行命令
- 只需要一个参数：文本
- 使用aiid=1或3

### 2. 执行文本命令 (Execute Text Command)
```bash
micli.py 5-4 查询天气 1  # siid=5, aiid=4, response_flag=1
micli.py 5-4 关灯 0     # siid=5, aiid=4, response_flag=0
```
- 相当于对音箱说"小爱同学，<文本>"
- 需要两个参数：文本 + 响应标志（1=语音回应，0=静默执行）
- 使用aiid=4

## 解决方案

### 1. 直接调用MIoT API
不使用`miio_command`的字符串解析，直接调用`MiIOService.miot_action()`方法。

### 2. 区分两种功能
- `text_to_speech()` - TTS播报（aiid=1或3），只传文本参数
- `execute_text_command()` - 执行命令（aiid=4），传文本+响应标志
- `send_command()` - 调用`execute_text_command()`

### 代码实现

```python
# TTS播报映射
TTS_COMMAND = {
    "OH2P": "7-3",  # siid=7, aiid=3
    # ... 其他设备
}

# 执行命令映射
EXECUTE_COMMAND = {
    "OH2P": "7-4",  # siid=7, aiid=4
    # ... 其他设备
}

# TTS播报（只传文本）
async def text_to_speech(text, device_id):
    siid, aiid = 7, 3
    result = await miot_action(did, (siid, aiid), [text])

# 执行命令（传文本+响应标志）
async def execute_text_command(text, device_id, silent=False):
    siid, aiid = 7, 4
    response_flag = 0 if silent else 1
    result = await miot_action(did, (siid, aiid), [text, response_flag])
```

## 测试结果

运行测试脚本：
```bash
python3 test/test_tts.py
```

测试结果：
```
✓ 所有测试通过 (All tests passed)!
```

### TTS播报测试
- ✓ "你好" - TTS broadcast成功
- ✓ "测试成功" - TTS broadcast成功

### 命令执行测试
- ✓ "现在几点了" (语音回应) - Execute command成功
- ✓ "查询天气" (语音回应) - Execute command成功
- ✓ "关灯" (静默执行) - Execute command成功

## API使用示例

### 1. TTS播报（只播报文本）
```python
from xiaoai_media.client import XiaoAiClient

async with XiaoAiClient() as client:
    # 播报文本
    result = await client.text_to_speech("你好", device_id)
```

```bash
# API调用
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好", "device_id": "xxx"}'
```

### 2. 执行命令（相当于说"小爱同学，..."）
```python
# 带语音回应
result = await client.send_command("查询天气", device_id)

# 静默执行（不要音箱回应）
result = await client.send_command("关灯", device_id, silent=True)
```

```bash
# API调用 - 带语音回应
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{"text": "查询天气", "device_id": "xxx", "silent": false}'

# API调用 - 静默执行
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{"text": "关灯", "device_id": "xxx", "silent": true}'
```

## 支持的设备

### TTS播报 (aiid=1或3)
| 硬件代码 | SIID-AIID | 设备型号 |
|---------|-----------|---------|
| OH2     | 5-3       | 小米智能音箱 |
| OH2P    | 7-3       | 小米智能音箱Pro |
| LX06    | 5-1       | 小爱音箱 |
| LX01    | 5-1       | 小爱音箱 |
| ... | ... | ... |

### 执行命令 (aiid=4)
| 硬件代码 | SIID-AIID | 设备型号 |
|---------|-----------|---------|
| OH2     | 5-4       | 小米智能音箱 |
| OH2P    | 7-4       | 小米智能音箱Pro |
| LX06    | 5-4       | 小爱音箱 |
| LX01    | 5-4       | 小爱音箱 |
| ... | ... | ... |

## 关键改进

1. **区分两种TTS功能**：
   - TTS播报（aiid=1/3）：只播报文本
   - 执行命令（aiid=4）：执行命令并可控制是否语音回应

2. **正确的参数格式**：
   - TTS播报：`[text]`
   - 执行命令：`[text, response_flag]`

3. **支持静默模式**：
   - `silent=False`（默认）：设备会语音回应
   - `silent=True`：设备静默执行，不语音回应

4. **保留降级方案**：
   - 如果`miot_action`失败，自动降级到`MiNAService`

## 参考资料

- [MiService GitHub仓库](https://github.com/Yonsm/MiService)
- [xiaomusic TTS常量定义](https://github.com/hanxi/xiaomusic/blob/main/xiaomusic/const.py)
- MiService文档第7节：动作调用TTS 播报和执行文本

## 文件修改

- `backend/src/xiaoai_media/client.py` - 添加`execute_text_command`方法，修改`text_to_speech`和`send_command`
- `backend/src/xiaoai_media/api/routes/command.py` - 添加`silent`参数支持
- `test/test_tts.py` - 更新测试脚本，分别测试TTS播报和命令执行
- `TTS修复说明.md` - 本文档
