# 播放控制器更新说明

## 更新内容

根据反馈，对播放控制器进行了以下三项重要更新：

### 1. 添加每秒进度推送 ✅

**问题**：定时器模式下，前端无法实时看到播放进度更新。

**解决方案**：
- 新增 `_progress_push_loop()` 方法，每秒推送一次播放进度
- 在 `on_play_started()` 时启动进度推送任务
- 在 `on_play_paused()` 和 `on_play_stopped()` 时取消进度推送任务
- 进度计算基于开始时间和初始位置，避免频繁调用 API

**实现细节**：
```python
async def _progress_push_loop(self, device_id: str):
    """进度推送循环，每秒推送一次播放进度"""
    while True:
        await asyncio.sleep(1.0)
        
        # 计算当前播放位置
        elapsed_ms = int((current_time - start_time) * 1000)
        current_position = initial_position + elapsed_ms
        
        # 推送进度更新
        await self._notify_status_change(device_id, status)
```

**效果**：
- 前端每秒收到一次进度更新
- 播放进度条平滑移动
- 不增加 API 调用次数

### 2. 完善 PlaylistService 中的 controller 桥接 ✅

**问题**：`playlist_service.py` 中有些地方只调用了 `monitor`，没有支持 `controller`。

**解决方案**：

#### 2.1 修改 `_delayed_monitor_check()` 方法

**位置**：`backend/src/xiaoai_media/services/playlist_service.py:570`

**修改前**：
```python
# 获取 monitor 实例
from xiaoai_media.playback_monitor import get_monitor
monitor = get_monitor()

# 如果 monitor 没有运行，调用 check_and_resume
if not monitor.running:
    await monitor.check_and_resume()
```

**修改后**：
```python
# 根据配置选择使用 monitor 还是 controller
if app_config.PLAYBACK_MODE == "controller":
    from xiaoai_media.playback_controller import get_controller
    controller = get_controller()
    
    if not controller.running:
        await controller.check_and_resume()
else:
    from xiaoai_media.playback_monitor import get_monitor
    monitor = get_monitor()
    
    if not monitor.running:
        await monitor.check_and_resume()
```

#### 2.2 修改 `stop_playlist()` 方法

**位置**：`backend/src/xiaoai_media/services/playlist_service.py:455`

**新增**：
```python
# 通知 controller/monitor 停止播放
from xiaoai_media import config as app_config
if app_config.ENABLE_PLAYBACK_MONITOR:
    if app_config.PLAYBACK_MODE == "controller":
        from xiaoai_media.playback_controller import get_controller
        controller = get_controller()
        await controller.on_play_stopped(device_id or "default")
```

**效果**：
- 停止播放时，controller 会取消定时器和进度推送
- 清除设备状态
- 避免资源泄漏

### 3. 修复 controller 下一曲时没有触发创建计时器 ✅

**问题**：定时器触发播放下一曲后，没有为新歌曲创建定时器，导致无法继续自动播放。

**原因分析**：
1. `_play_next()` 调用 `PlaylistService.play_next_in_playlist()`
2. `play_next_in_playlist()` 调用 `play_playlist()`
3. `play_playlist()` 会调用 `controller.on_play_started()` 设置新的定时器
4. 但是旧的定时器和进度推送任务没有被取消

**解决方案**：

在 `_play_next()` 方法开始时，先取消旧的定时器和进度推送任务：

```python
async def _play_next(self, device_id: str, playlist_id: str):
    # 取消当前的定时器和进度推送
    await self._cancel_timer(device_id)
    await self._cancel_progress_task(device_id)
    
    # 停止当前播放
    await client.player_stop(device_id)
    
    # 播放下一曲（这会触发 play_playlist，进而调用 on_play_started 设置新的定时器）
    result = await PlaylistService.play_next_in_playlist(playlist_id, device_id)
```

**效果**：
- 播放下一曲时，旧的定时器和进度推送被正确取消
- 新的定时器和进度推送被正确创建
- 实现连续自动播放

## 修改文件清单

### 修改的文件

1. **backend/src/xiaoai_media/playback_controller.py**
   - 新增 `_progress_tasks` 字典，记录进度推送任务
   - 新增 `_cancel_progress_task()` 方法，取消进度推送任务
   - 新增 `_progress_push_loop()` 方法，每秒推送进度
   - 修改 `on_play_started()`，启动进度推送任务
   - 修改 `on_play_paused()`，取消进度推送任务
   - 修改 `on_play_stopped()`，取消进度推送任务
   - 修改 `_play_next()`，先取消旧的定时器和进度推送
   - 修改 `stop()`，取消所有进度推送任务

2. **backend/src/xiaoai_media/services/playlist_service.py**
   - 修改 `_delayed_monitor_check()`，支持 controller 模式
   - 修改 `stop_playlist()`，通知 controller 停止播放

## 测试验证

### 测试场景 1：进度推送

1. 启动服务，配置为定时器模式
2. 播放一首歌曲
3. 打开浏览器开发者工具，查看 Network 标签
4. 观察 SSE 连接，应该每秒收到一次进度更新
5. 前端播放进度条应该平滑移动

**预期结果**：
- 每秒收到一次 `event: state` 消息
- `position` 字段每秒增加约 1000（毫秒）
- 进度条平滑移动

### 测试场景 2：停止播放

1. 播放一首歌曲
2. 点击停止按钮
3. 查看日志

**预期结果**：
```
设备 xxx 停止播放，取消定时器和进度推送
已通知播放控制器停止播放
已取消设备 xxx 的定时器
已取消设备 xxx 的进度推送任务
```

### 测试场景 3：自动播放下一曲

1. 创建一个包含多首歌曲的播放列表
2. 播放第一首歌曲
3. 等待歌曲播放完成
4. 观察是否自动播放下一曲
5. 查看日志

**预期结果**：
```
设备 xxx 定时器触发，播放下一曲
准备播放下一曲: device_id=xxx, playlist_id=xxx
取消当前的定时器和进度推送
停止当前播放...
调用 PlaylistService.play_next_in_playlist...
设备 xxx 开始播放，时长 xxx ms，当前位置 0 ms
已设置播放定时器: duration=xxx, position=0
自动播放下一曲成功: 歌曲名
```

### 测试场景 4：暂停和继续

1. 播放一首歌曲
2. 点击暂停按钮
3. 等待几秒
4. 点击继续按钮
5. 观察进度是否正确

**预期结果**：
- 暂停时，进度推送停止
- 继续时，进度推送恢复
- 进度计算正确（考虑暂停时间）

## 性能影响

### 进度推送的性能开销

- **每秒推送一次**：相比轮询模式（每 3 秒调用一次 API），进度推送只是内存计算和 SSE 推送
- **无 API 调用**：进度计算基于本地时间，不需要调用设备 API
- **资源消耗**：极低，只有简单的数学计算和异步任务

### 对比

| 操作 | 轮询模式 | 定时器模式（无进度推送） | 定时器模式（有进度推送） |
|------|---------|----------------------|---------------------|
| API 调用（3分钟） | 60 次 | 2 次 | 2 次 |
| 进度更新频率 | 每 3 秒 | 无 | 每 1 秒 |
| CPU 占用 | 中等 | 极低 | 极低 |
| 内存占用 | 中等 | 极低 | 极低 |
| 用户体验 | 一般 | 差（无进度） | 好（平滑进度） |

## 已知问题和限制

1. **进度计算精度**：
   - 基于本地时间计算，可能与设备实际播放位置有微小偏差
   - 如果设备播放速度不稳定，进度可能不准确
   - 建议：定期（如每 30 秒）从设备读取一次实际位置进行校准

2. **暂停后继续**：
   - 当前实现会重新读取设备状态
   - 如果设备状态读取失败，可能导致进度不准确

3. **网络延迟**：
   - SSE 推送可能有网络延迟
   - 前端应该使用本地时间进行平滑插值

## 未来改进

1. **进度校准**：
   - 每 30 秒从设备读取一次实际位置
   - 自动校准本地计算的进度

2. **自适应推送频率**：
   - 根据网络状况调整推送频率
   - 在网络良好时提高到每 0.5 秒

3. **前端平滑插值**：
   - 前端使用 requestAnimationFrame 进行平滑插值
   - 减少对后端推送频率的依赖

4. **混合模式**：
   - 定时器为主，定期轮询为辅
   - 自动检测并纠正偏差

## 总结

本次更新解决了三个关键问题：

1. ✅ 添加了每秒进度推送，提升用户体验
2. ✅ 完善了 PlaylistService 中的 controller 桥接，确保功能完整
3. ✅ 修复了下一曲时没有创建定时器的问题，实现连续自动播放

定时器模式现在已经完全可用，并且提供了良好的用户体验！
