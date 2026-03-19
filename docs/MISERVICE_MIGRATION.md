# MiService 迁移说明

## 概述

项目已从原版 `miservice` 迁移到 `miservice_fork` (yihong0618/MiService)，新版本提供了更强大的音乐播放控制API。

## 主要变化

### 1. 依赖更新

```toml
# 旧版本
dependencies = ["miservice", ...]

# 新版本
dependencies = ["miservice_fork", ...]
```

### 2. 新增 API 方法

#### MiNAService 新增方法：

- `player_pause(deviceId)` - 暂停播放
- `player_stop(deviceId)` - 停止播放
- `player_play(deviceId)` - 恢复播放
- `player_get_status(deviceId)` - 获取播放状态
- `player_set_loop(deviceId, type)` - 设置循环模式 (0=单曲循环, 1=列表循环)
- `play_by_url(deviceId, url, _type)` - 播放URL（自动检测硬件类型）
- `play_by_music_url(deviceId, url, _type, audio_id, id)` - 使用音乐API播放

### 3. 客户端更新 (client.py)

#### 简化的 play_url 方法

旧版本需要手动判断硬件类型并选择 API：
```python
if hardware in USE_PLAY_MUSIC_API:
    # 使用 player_play_music
    result = await self._na_service.ubus_request(...)
else:
    # 使用 player_play_url
    result = await self._na_service.ubus_request(...)
```

新版本直接调用 `play_by_url`，自动处理硬件检测：
```python
result = await self._na_service.play_by_url(did, url, _type)
```

#### 新增播放控制方法

```python
# 暂停
await client.player_pause(device_id)

# 恢复播放
await client.player_play(device_id)

# 停止
await client.player_stop(device_id)

# 获取状态
status = await client.player_get_status(device_id)

# 设置循环模式
await client.player_set_loop(device_id, loop_type=1)
```

### 4. API 路由更新 (music.py)

#### 暂停/恢复接口改进

旧版本使用语音命令：
```python
# 暂停
await client.send_command("暂停", device_id)

# 恢复
await client.send_command("继续播放", device_id)
```

新版本使用专用API：
```python
# 暂停
await client.player_pause(device_id)

# 恢复
await client.player_play(device_id)
```

#### 新增接口

- `POST /api/music/stop` - 停止播放
- `GET /api/music/status?device_id=xxx` - 获取播放状态

## 优势

1. **更可靠的播放控制** - 使用专用API而非语音命令，避免语音识别问题
2. **自动硬件检测** - `play_by_url` 自动选择合适的播放API
3. **更多控制选项** - 支持暂停/恢复/停止/状态查询/循环模式
4. **代码更简洁** - 移除了手动硬件类型判断逻辑

## 安装

```bash
cd backend
pip uninstall -y miservice
pip install miservice_fork
```

## 测试

```bash
# 运行测试脚本
python test/music/test_new_api.py
```

## 参考

- GitHub: https://github.com/yihong0618/MiService
- PyPI: https://pypi.org/project/miservice-fork/
