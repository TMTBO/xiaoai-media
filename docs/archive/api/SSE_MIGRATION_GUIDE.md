# SSE 状态推送迁移指南

## 概述

本次更新将播放状态获取从**轮询模式**改为 **SSE (Server-Sent Events) 推送模式**，大幅降低服务器负载和网络流量。

## 改动内容

### 后端改动

1. **playback_monitor.py** - 添加状态变化通知机制
   - 新增 `StatusChangeCallback` 类型
   - 添加 `add_status_callback()` / `remove_status_callback()` 方法
   - 状态变化时自动通知所有订阅者
   - 新增 `get_monitor()` 全局实例获取函数

2. **music.py** - 新增 SSE 端点
   - `GET /api/music/status/stream` - 流式推送状态变化
   - 支持 `device_id` 参数过滤特定设备
   - 首次连接立即发送当前状态
   - 每 30 秒发送心跳保持连接
   - 自动清理断开的连接

### 前端改动

1. **新增 composable**: `frontend/src/composables/usePlayerStatus.ts`
   - 封装 SSE 连接逻辑
   - 自动重连机制（最多 5 次）
   - 响应式状态管理
   - 自动清理资源

2. **更新组件**: `frontend/src/components/GlobalDeviceSelector.vue`
   - 移除轮询逻辑（`setInterval`）
   - 使用 `usePlayerStatus` composable
   - 简化代码，减少约 50 行

## 性能对比

### 轮询模式（旧）
```
请求频率: 每 3 秒 1 次
每小时请求: 1200 次
每天请求: 28,800 次
带宽消耗: ~1.4 MB/小时（假设每次响应 1KB）
```

### SSE 模式（新）
```
请求频率: 仅在状态变化时
每小时请求: ~10-50 次（取决于播放活动）
每天请求: ~240-1200 次
带宽消耗: ~0.05-0.25 MB/小时
节省: 约 95% 的请求和带宽
```

## 使用方式

### 前端使用

```typescript
import { usePlayerStatus } from '@/composables/usePlayerStatus'

// 在组件中使用
const { status, error, connected } = usePlayerStatus(deviceId)

// status.value 包含:
// - device_id: 设备 ID
// - status: 'playing' | 'paused' | 'stopped'
// - audio_id: 音频 ID
// - position: 播放位置（毫秒）
// - duration: 总时长（毫秒）
// - media_type: 媒体类型
```

### 测试

1. 启动后端服务
2. 在浏览器中打开测试页面：
   ```
   frontend/src/composables/__tests__/usePlayerStatus.test.html
   ```
3. 输入设备 ID，点击"连接 SSE"
4. 播放音乐，观察状态实时更新

## 兼容性

- 保留了原有的 `GET /api/music/status` 接口，向后兼容
- 新增 `GET /api/music/status/stream` SSE 端点
- 前端可以选择使用轮询或 SSE 方式

## 注意事项

1. **浏览器限制**: 同一域名下 SSE 连接数限制为 6 个
2. **重连机制**: 已实现自动重连，最多尝试 5 次
3. **心跳保持**: 服务端每 30 秒发送心跳，防止连接超时
4. **资源清理**: 组件卸载时自动断开连接

## 故障排查

### 连接失败
- 检查后端服务是否正常运行
- 检查浏览器控制台是否有 CORS 错误
- 确认 `/api/music/status/stream` 端点可访问

### 状态不更新
- 检查设备是否在线
- 确认设备正在播放音乐
- 查看后端日志中的状态变化通知

### 连接频繁断开
- 检查网络稳定性
- 查看服务器日志是否有异常
- 确认没有代理或防火墙阻止 SSE 连接

## 回滚方案

如果遇到问题需要回滚到轮询模式，只需在 `GlobalDeviceSelector.vue` 中：

1. 移除 `usePlayerStatus` 导入
2. 恢复原有的 `fetchPlayStatus()` 和 `startStatusPolling()` 逻辑
3. 在 `onMounted` 中调用 `startStatusPolling()`

原有的 `/api/music/status` 接口仍然可用。
