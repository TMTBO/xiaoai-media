# SSE 状态流式推送

## 概述

为了避免前端频繁轮询 `/api/music/status` 接口，现在提供了 SSE (Server-Sent Events) 端点，当播放状态发生变化时，服务端会主动推送给前端。

## API 端点

```
GET /api/music/status/stream?device_id={device_id}
```

### 参数

- `device_id` (可选): 设备 ID，如果不指定则监听所有设备的状态变化

### 响应格式

SSE 事件流，每个事件格式如下：

```
event: status
data: {"device_id": "xxx", "status": "playing", "audio_id": "xxx", "position": 12345, "duration": 234567, "media_type": 3}
```

### 状态字段说明

- `device_id`: 设备 ID
- `status`: 播放状态 (`playing` | `paused` | `stopped`)
- `audio_id`: 当前播放的音频 ID
- `position`: 当前播放位置（毫秒）
- `duration`: 总时长（毫秒）
- `media_type`: 媒体类型（3 表示音乐）

## 前端使用示例

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

## 优势

相比轮询方式：

1. **减少服务器负载**: 不需要每隔几秒发送一次请求
2. **实时性更好**: 状态变化时立即推送，延迟更低
3. **节省带宽**: 只在状态变化时传输数据
4. **更简单**: 前端代码更简洁，不需要管理定时器

## 注意事项

1. **连接保持**: SSE 连接会保持打开状态，服务端每 30 秒发送心跳保持连接
2. **重连机制**: 建议实现自动重连逻辑，处理网络中断情况
3. **浏览器限制**: 同一域名下 SSE 连接数有限制（通常 6 个），注意管理连接
4. **兼容性**: 所有现代浏览器都支持 EventSource API

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
