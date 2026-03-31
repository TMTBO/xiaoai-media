# 播放控制器（定时器模式）

## 概述

播放控制器是一个基于定时器的播放监控方案，相比传统的轮询模式，它更加高效，减少了不必要的 API 调用。

## 两种模式对比

### 轮询模式（Playback Monitor）

- **工作原理**：定期（如每 3 秒）调用 API 检查播放状态
- **优点**：
  - 兼容性好，不依赖音频时长信息
  - 能检测到各种异常情况（如手动停止、网络中断等）
- **缺点**：
  - 频繁调用 API，消耗更多资源
  - 响应延迟（取决于轮询间隔）
  - 在播放长音频时会产生大量无用的 API 调用

### 定时器模式（Playback Controller）

- **工作原理**：根据音频时长设置定时器，在歌曲结束前触发下一曲
- **优点**：
  - 高效，只在需要时调用 API
  - 响应及时，在歌曲结束前准确触发
  - 减少服务器和设备负载
- **缺点**：
  - 依赖准确的音频时长信息
  - 无法检测手动停止等异常情况（除非主动查询）

## 配置方式

### 1. 在 user_config.py 中配置

```python
# 启用播放监控
ENABLE_PLAYBACK_MONITOR = True

# 选择播放模式
# "monitor" - 轮询模式（默认）
# "controller" - 定时器模式
PLAYBACK_MODE = "controller"

# 轮询间隔（仅在轮询模式下使用）
PLAYBACK_MONITOR_INTERVAL = 3.0
```

### 2. 在前端配置页面中配置

1. 打开"配置管理"页面
2. 找到"播放监控"部分
3. 启用"启用监控"开关
4. 选择"监控模式"：
   - 轮询模式：定期检查播放状态（兼容性好，但较耗性能）
   - 定时器模式：根据音频时长设置定时器（高效，但依赖准确的时长信息）
5. 如果选择轮询模式，可以调整"轮询间隔"
6. 点击"保存配置"

## 工作流程

### 播放开始

1. 播放器调用 `PlaylistService.play_playlist()` 播放歌曲
2. 等待 0.5 秒让设备开始播放
3. 获取当前播放状态（包括 duration 和 position）
4. 调用 `controller.on_play_started(device_id, duration, position)`
5. 控制器计算剩余播放时间：`remaining = (duration - position) / 1000 - buffer_time`
6. 设置定时器，在剩余时间后触发下一曲

### 暂停播放

1. 用户暂停播放
2. 调用 `controller.on_play_paused(device_id)`
3. 控制器取消定时器
4. 更新设备状态为"paused"

### 继续播放

1. 用户继续播放
2. 调用 `controller.on_play_resumed(device_id)`
3. 控制器重新读取播放状态
4. 根据新的 duration 和 position 重新设置定时器

### 停止播放

1. 用户停止播放
2. 调用 `controller.on_play_stopped(device_id)`
3. 控制器取消定时器
4. 清除设备状态和播单信息

### 下一曲

1. 定时器触发
2. 控制器调用 `_play_next(device_id, playlist_id)`
3. 停止当前播放
4. 调用 `PlaylistService.play_next_in_playlist()` 播放下一曲
5. 重复"播放开始"流程

## API 接口

### PlaybackController 类

```python
class PlaybackController:
    def __init__(self, buffer_time: float = 1.0):
        """初始化播放控制器
        
        Args:
            buffer_time: 定时器缓冲时间（秒），在歌曲结束前多久触发下一曲
        """
        
    async def start(self):
        """启动播放控制器"""
        
    async def stop(self):
        """停止播放控制器"""
        
    async def check_and_resume(self):
        """检查设备播放状态并恢复监听"""
        
    async def on_play_started(self, device_id: str, duration: int, position: int = 0):
        """播放开始时调用
        
        Args:
            device_id: 设备 ID
            duration: 音频总时长（毫秒）
            position: 当前播放位置（毫秒）
        """
        
    async def on_play_paused(self, device_id: str):
        """播放暂停时调用"""
        
    async def on_play_resumed(self, device_id: str):
        """播放继续时调用"""
        
    async def on_play_stopped(self, device_id: str):
        """播放停止时调用"""
        
    def add_status_callback(self, callback: StatusChangeCallback):
        """添加状态变化回调"""
        
    def remove_status_callback(self, callback: StatusChangeCallback):
        """移除状态变化回调"""
```

### 获取全局实例

```python
from xiaoai_media.playback_controller import get_controller

controller = get_controller()
```

## 状态推送（SSE）

定时器模式完全兼容 SSE 状态推送功能：

1. 前端连接 `/api/state/stream` 端点
2. 控制器在状态变化时调用注册的回调函数
3. SSE 路由将状态推送给前端
4. 前端实时更新播放进度和歌曲信息

## 注意事项

1. **时长信息准确性**：定时器模式依赖音频文件的时长信息，如果时长不准确，可能导致切换时机不对
2. **缓冲时间**：默认缓冲时间为 1 秒，可以根据实际情况调整
3. **异常处理**：定时器模式无法检测手动停止等异常情况，建议配合前端状态监控使用
4. **模式切换**：修改配置后需要重启服务或重新加载配置才能生效

## 测试

运行测试：

```bash
cd backend
pytest tests/test_playback_controller.py -v
```

## 故障排查

### 问题：定时器没有触发下一曲

1. 检查是否启用了播放监控：`ENABLE_PLAYBACK_MONITOR = True`
2. 检查是否选择了定时器模式：`PLAYBACK_MODE = "controller"`
3. 检查日志，确认定时器是否正确设置
4. 检查音频时长信息是否准确

### 问题：切换时机不准确

1. 调整缓冲时间（默认 1 秒）
2. 检查音频文件的时长信息是否准确
3. 考虑切换回轮询模式

### 问题：配置修改后没有生效

1. 在前端配置页面点击"保存配置"
2. 或者重启服务：`make restart`
3. 检查日志确认配置已重新加载

## 性能对比

假设播放一首 3 分钟的歌曲：

- **轮询模式**（3 秒间隔）：需要调用 60 次 API
- **定时器模式**：只需要调用 2 次 API（开始播放时 1 次，播放下一曲时 1 次）

性能提升：**约 30 倍**

## 未来改进

1. 支持混合模式：定时器为主，定期轮询为辅
2. 自动检测音频时长准确性，动态切换模式
3. 支持更多的播放事件（如快进、快退等）
4. 优化缓冲时间的自适应调整
