# 升级指南：迁移到 miservice_fork

## 概述

本指南帮助你从原版 `miservice` 升级到增强版 `miservice_fork`。

## 为什么升级？

`miservice_fork` (yihong0618/MiService) 在原版基础上新增了：

1. **专用播放控制API** - 不再依赖语音命令
2. **自动硬件检测** - 自动选择最佳播放方法
3. **循环模式控制** - 支持单曲/列表循环
4. **播放状态查询** - 实时获取播放状态

## 升级步骤

### 1. 更新依赖

```bash
cd backend
pip uninstall -y miservice
pip install miservice_fork
```

### 2. 验证安装

```bash
python -c "from miservice import MiNAService; print('✓ 安装成功')"
```

### 3. 代码已自动更新

以下文件已更新：
- `backend/pyproject.toml` - 依赖声明
- `backend/src/xiaoai_media/client.py` - 客户端实现
- `backend/src/xiaoai_media/api/routes/music.py` - API路由

### 4. 测试新功能

```bash
# 运行测试脚本
python test/music/test_new_api.py
```

### 5. 重启服务

```bash
cd backend
python -m uvicorn xiaoai_media.api.main:app --reload
```

## API 变化对比

### 暂停播放

**旧版本（语音命令）：**
```python
await client.send_command("暂停", device_id)
```

**新版本（专用API）：**
```python
await client.player_pause(device_id)
```

### 恢复播放

**旧版本（语音命令）：**
```python
await client.send_command("继续播放", device_id)
```

**新版本（专用API）：**
```python
await client.player_play(device_id)
```

### 播放URL

**旧版本（手动硬件判断）：**
```python
if hardware in USE_PLAY_MUSIC_API:
    # 使用 player_play_music
    result = await self._na_service.ubus_request(...)
else:
    # 使用 player_play_url
    result = await self._na_service.ubus_request(...)
```

**新版本（自动检测）：**
```python
result = await self._na_service.play_by_url(device_id, url, _type)
```

## 新增功能

### 1. 停止播放

```python
await client.player_stop(device_id)
```

```http
POST /api/music/stop
```

### 2. 获取播放状态

```python
status = await client.player_get_status(device_id)
```

```http
GET /api/music/status?device_id=xxx
```

### 3. 设置循环模式

```python
# 单曲循环
await client.player_set_loop(device_id, loop_type=0)

# 列表循环
await client.player_set_loop(device_id, loop_type=1)
```

## 兼容性说明

### 完全兼容
- 所有现有API接口保持不变
- 前端代码无需修改
- 环境变量配置不变

### 行为改进
- `/pause` 和 `/resume` 接口更可靠（使用专用API而非语音命令）
- 播放URL自动选择最佳方法（无需手动判断硬件）

## 故障排查

### 问题：导入错误

```
ModuleNotFoundError: No module named 'miservice'
```

**解决方案：**
```bash
pip install miservice_fork
```

### 问题：方法不存在

```
AttributeError: 'MiNAService' object has no attribute 'player_pause'
```

**解决方案：**
确认安装的是 `miservice_fork` 而非 `miservice`：
```bash
pip show miservice_fork
```

### 问题：播放失败

**解决方案：**
1. 检查设备是否在线
2. 查看日志获取详细错误信息
3. 尝试使用 `player_stop()` 后重新播放

## 参考资料

- [MiService Fork GitHub](https://github.com/yihong0618/MiService)
- [API 接口参考](API_REFERENCE.md)
- [迁移说明](MISERVICE_MIGRATION.md)
