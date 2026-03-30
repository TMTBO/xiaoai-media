# SSE 实时状态推送指南

Server-Sent Events (SSE) 实时推送播放状态，无需轮询。

---

## 📚 目录

- [快速开始](#快速开始)
- [API 端点](#api-端点)
- [前端使用](#前端使用)
- [功能验证](#功能验证)
- [故障排除](#故障排除)

---

## 快速开始

### 1. 启动服务

```bash
# 后端
cd backend
python run.py

# 前端（新终端）
cd frontend
npm run dev
```

### 2. 测试步骤

1. 打开浏览器访问 `http://localhost:5173`
2. 在顶部选择一个设备
3. 进入"音乐搜索"页面，搜索并播放音乐
4. 观察播放器栏自动出现在设备选择器下方
5. 测试播放控制按钮

### 3. 独立测试页面

访问 `http://localhost:5173/test-global-state.html` 查看详细的状态信息和日志。

---

## API 端点

### 状态流式推送

```
GET /api/music/status/stream?device_id={device_id}
```

#### 参数

- `device_id` (可选): 设备 ID，如果不指定则监听所有设备的状态变化

#### 响应格式

SSE 事件流，每个事件格式如下：

```
event: status
data: {"device_id": "xxx", "status": "playing", "audio_id": "xxx", "position": 12345, "duration": 234567, "media_type": 3}
```

#### 状态字段说明

- `device_id`: 设备 ID
- `status`: 播放状态 (`playing` | `paused` | `stopped`)
- `audio_id`: 当前播放的音频 ID
- `position`: 当前播放位置（毫秒）
- `duration`: 总时长（毫秒）
- `media_type`: 媒体类型（3 表示音乐）

---

## 前端使用

### JavaScript / TypeScript

```javascript
// 创建 EventSource 连接
const deviceId = 'e01467de-11ff-4fb0-b76b-51cde0bc3b19';
const eventSource = new EventSource(`/api/music/status/stream?device_id=${deviceId}`);

// 监听状态变化事件
eventSource.addEventListener('status', (event) => {
  const status = JSON.parse(event.data);
  console.log('播放状态变化:', status);
  
  // 更新 UI
  updatePlayerUI(status);
});

// 监听错误
eventSource.onerror = (error) => {
  console.error('SSE 连接错误:', error);
  eventSource.close();
  
  // 可以在这里实现重连逻辑
  setTimeout(() => {
    // 重新连接
  }, 5000);
};

// 关闭连接
// eventSource.close();
```

### React Hook 示例

```typescript
import { useEffect, useState } from 'react';

interface PlayerStatus {
  device_id: string;
  status: 'playing' | 'paused' | 'stopped';
  audio_id: string;
  position: number;
  duration: number;
  media_type: number;
}

export function usePlayerStatus(deviceId: string) {
  const [status, setStatus] = useState<PlayerStatus | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(
      `/api/music/status/stream?device_id=${deviceId}`
    );

    eventSource.addEventListener('status', (event) => {
      try {
        const data = JSON.parse(event.data);
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      }
    });

    eventSource.onerror = (err) => {
      console.error('SSE error:', err);
      setError(new Error('SSE connection failed'));
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [deviceId]);

  return { status, error };
}
```

### Vue 3 Composition API 示例

```typescript
import { ref, onMounted, onUnmounted } from 'vue';

export function usePlayerStatus(deviceId: string) {
  const status = ref(null);
  const error = ref(null);
  let eventSource: EventSource | null = null;

  onMounted(() => {
    eventSource = new EventSource(
      `/api/music/status/stream?device_id=${deviceId}`
    );

    eventSource.addEventListener('status', (event) => {
      try {
        status.value = JSON.parse(event.data);
        error.value = null;
      } catch (err) {
        error.value = err;
      }
    });

    eventSource.onerror = (err) => {
      console.error('SSE error:', err);
      error.value = new Error('SSE connection failed');
      eventSource?.close();
    };
  });

  onUnmounted(() => {
    eventSource?.close();
  });

  return { status, error };
}
```

---

## 功能验证

### 验证清单

- [ ] 选择设备后，SSE 自动连接
- [ ] 播放音乐后，播放器栏出现
- [ ] 显示歌曲封面、歌名、歌手、专辑
- [ ] 进度条实时更新
- [ ] 点击"暂停"按钮，状态立即更新
- [ ] 点击"下一曲"，切换到下一首歌
- [ ] 点击"上一曲"，切换到上一首歌
- [ ] 歌曲播放完成，自动播放下一曲
- [ ] 切换设备，播放器栏更新为新设备状态
- [ ] 停止播放，播放器栏消失

### 查看日志

#### 后端日志

```bash
# 查看状态变化通知
tail -f backend/logs/app.log | grep "通知.*订阅者"

# 查看 SSE 连接
tail -f backend/logs/app.log | grep "SSE"
```

#### 前端日志

打开浏览器开发者工具 Console 标签，查看：
- SSE 连接状态
- 状态更新事件
- 错误信息

### 网络监控

在浏览器开发者工具 Network 标签中：

1. 筛选 `state/stream`
2. 查看 EventStream 类型的连接
3. 观察实时推送的事件

---

## 故障排除

### Q: 播放器栏不显示？

A: 确保：
1. 已选择设备
2. 设备正在播放音乐
3. SSE 连接成功（查看 Console）

### Q: 状态更新延迟？

A: 正常延迟应该 < 1 秒。如果延迟较大：
1. 检查网络连接
2. 查看后端日志中的轮询间隔设置
3. 确认没有代理或 VPN 影响

### Q: 连接频繁断开？

A: 可能原因：
1. 网络不稳定
2. 服务器重启
3. 浏览器限制（同域名最多 6 个 SSE 连接）

解决方法：
- 已实现自动重连（最多 5 次）
- 检查是否有多个标签页同时连接
- 查看服务器日志排查问题

---

## 优势

相比轮询方式：

1. **减少服务器负载**: 不需要每隔几秒发送一次请求
2. **实时性更好**: 状态变化时立即推送，延迟更低
3. **节省带宽**: 只在状态变化时传输数据
4. **更简单**: 前端代码更简洁，不需要管理定时器

---

## 注意事项

1. **连接保持**: SSE 连接会保持打开状态，服务端每 30 秒发送心跳保持连接
2. **重连机制**: 建议实现自动重连逻辑，处理网络中断情况
3. **浏览器限制**: 同一域名下 SSE 连接数有限制（通常 6 个），注意管理连接
4. **兼容性**: 所有现代浏览器都支持 EventSource API

---

## 迁移指南

如果你当前使用轮询方式：

```javascript
// 旧方式：轮询
const pollInterval = setInterval(async () => {
  const response = await fetch(`/api/music/status?device_id=${deviceId}`);
  const status = await response.json();
  updatePlayerUI(status);
}, 2000);

// 清理
clearInterval(pollInterval);
```

改为 SSE 方式：

```javascript
// 新方式：SSE
const eventSource = new EventSource(`/api/music/status/stream?device_id=${deviceId}`);
eventSource.addEventListener('status', (event) => {
  const status = JSON.parse(event.data);
  updatePlayerUI(status);
});

// 清理
eventSource.close();
```

---

## 性能监控

### 查看 SSE 连接数

后端日志会显示：
```
添加状态变化回调，当前回调数: 1
```

### 查看推送频率

观察日志中的"通知订阅者"消息频率，正常情况下：
- 播放中: 每 3 秒左右（轮询间隔）
- 暂停/停止: 无推送

---

## 相关文档

- [API 参考](API_REFERENCE.md) - 完整 API 文档
- [故障排除](TROUBLESHOOTING_SSE.md) - SSE 故障排除详细指南

---

**最后更新**: 2026-03-30
