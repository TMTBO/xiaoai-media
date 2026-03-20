# 指令播放拦截测试

## 功能说明

当设备正在播放时，阻止执行新的指令，并返回提示信息："设备正在播放, 当前不允许操作"。

## 实现位置

- `backend/src/xiaoai_media/client.py` - `send_command()` 方法中添加播放状态检查
- `backend/src/xiaoai_media/api/routes/command.py` - API 层返回 409 状态码

## 工作原理

1. 在执行指令前，调用 `player_get_status()` 检查设备播放状态
2. 如果 `status == 1`（正在播放），则阻止指令执行
3. 返回包含 `blocked: true` 和错误信息的响应
4. API 层捕获并返回 HTTP 409 状态码

## 测试方法

```bash
# 运行测试脚本
python test/command/test_playing_block.py
```

## API 响应示例

### 设备正在播放时

```json
{
  "device": "小爱音箱(123456)",
  "command": "今天天气怎么样",
  "result": false,
  "error": "设备正在播放, 当前不允许操作",
  "blocked": true
}
```

HTTP 状态码: 409 Conflict

### 设备未播放时

正常执行指令，返回执行结果。
