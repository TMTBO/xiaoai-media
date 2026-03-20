# 对话 API 实现说明

## 小米对话 API

### API 端点

```
GET https://userprofile.mina.mi.com/device_profile/v2/conversation
```

### 请求参数

- `source=dialogu` - 固定值
- `hardware={hardware}` - 设备型号（如 LX06, OH2P 等）
- `timestamp={timestamp}` - 当前时间戳（毫秒）
- `limit=2` - 返回最近 N 条对话

### 请求 Cookies

```
deviceId={device_id}
serviceToken={service_token}
```

### 响应格式

```json
{
  "code": 0,
  "data": "{\"records\":[{\"time\":1234567890,\"query\":\"播放周杰伦的晴天\",\"answers\":[{\"tts\":{\"text\":\"好的\"}}]}]}"
}
```

注意：`data` 字段是一个 JSON 字符串，需要再次解析。

### 实现代码

```python
async def get_latest_ask(self, device_id: str | None = None) -> list[dict]:
    """获取最新对话记录"""
    did = await self._resolve_device_id(device_id)
    
    # 获取设备硬件型号
    devices = await self.list_devices()
    hardware = next(
        (d.get("hardware", "") for d in devices if d["deviceID"] == did),
        "LX06"  # 默认值
    )
    
    # 构建 API URL
    timestamp = int(time.time() * 1000)
    url = f"https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
    
    # 发送请求
    cookies = {"deviceId": did}
    if self._account and hasattr(self._account, "service_token"):
        cookies["serviceToken"] = self._account.service_token
    
    async with self._session.get(url, cookies=cookies, timeout=15) as resp:
        data = await resp.json()
        
        # 解析响应
        result = []
        if d := data.get("data"):
            records = json.loads(d).get("records", [])
            for record in records:
                answers = record.get("answers", [{}])
                answer = answers[0].get("tts", {}).get("text", "").strip() if answers else ""
                
                result.append({
                    "time": record.get("time", 0),
                    "query": record.get("query", "").strip(),
                    "answer": answer,
                })
        
        return result
```

## 与 xiaomusic 的对比

xiaomusic 使用相同的 API，但有两种获取方式：

1. **HTTP API 方式**（大多数设备）
   - 直接调用 `userprofile.mina.mi.com` API
   - 需要 deviceId 和 serviceToken

2. **MiNA Service 方式**（特定设备如 M01）
   - 使用 `mina_service.get_latest_ask(device_id)`
   - 某些设备型号需要这种方式

我们的实现目前使用 HTTP API 方式，适用于大多数设备。

## 注意事项

1. **serviceToken 获取**
   - 需要先通过 `MiAccount` 登录
   - serviceToken 会自动保存在 account 对象中

2. **hardware 参数**
   - 不同设备型号需要传递正确的 hardware 值
   - 可以从 `device_list()` 获取

3. **时间戳**
   - 必须是毫秒级时间戳
   - 用于 API 缓存控制

4. **limit 参数**
   - 控制返回的对话数量
   - 建议设置为 2，只获取最新的对话
