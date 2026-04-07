/**
 * 播放器状态 SSE Hook
 * 
 * 使用 Server-Sent Events 实时接收播放状态变化，替代轮询方式
 */
import { ref, onUnmounted, watch, type Ref } from 'vue'

export interface PlayerStatus {
    device_id: string
    status: 'playing' | 'paused' | 'stopped'
    audio_id: string
    position: number
    duration: number
    media_type: number
}

export function usePlayerStatus(deviceId: Ref<string | null> | string | null): {
    status: Ref<PlayerStatus | null>
    error: Ref<Error | null>
    connected: Ref<boolean>
    reconnect: () => void
    disconnect: () => void
} {
    const status = ref<PlayerStatus | null>(null)
    const error = ref<Error | null>(null)
    const connected = ref(false)

    let eventSource: EventSource | null = null
    let reconnectTimer: number | null = null
    let reconnectAttempts = 0
    const maxReconnectAttempts = 5
    const reconnectDelay = 3000 // 3秒

    const deviceIdRef = isRef(deviceId) ? deviceId : ref(deviceId)

    function connect(): void {
        // 如果没有设备 ID，不连接
        if (!deviceIdRef.value) {
            disconnect()
            return
        }

        // 如果已经连接，先断开
        disconnect()

        try {
            const url = `/api/music/status/stream?device_id=${deviceIdRef.value}`
            eventSource = new EventSource(url)

            eventSource.addEventListener('status', (event: MessageEvent) => {
                try {
                    const data = JSON.parse(event.data)
                    status.value = data
                    error.value = null
                    reconnectAttempts = 0 // 重置重连次数
                } catch (err) {
                    error.value = err as Error
                }
            })

            eventSource.onopen = (): void => {
                connected.value = true
                error.value = null
            }

            eventSource.onerror = (): void => {
                connected.value = false
                error.value = new Error('SSE connection failed')

                // 自动重连
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++

                    reconnectTimer = window.setTimeout(() => {
                        connect()
                    }, reconnectDelay)
                }
            }
        } catch (err) {
            error.value = err as Error
        }
    }

    function disconnect(): void {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer)
            reconnectTimer = null
        }

        if (eventSource) {
            eventSource.close()
            eventSource = null
            connected.value = false
        }
    }

    // 监听设备 ID 变化
    watch(deviceIdRef, (newDeviceId, oldDeviceId) => {
        if (newDeviceId !== oldDeviceId) {
            status.value = null
            reconnectAttempts = 0
            connect()
        }
    }, { immediate: true })

    // 组件卸载时断开连接
    onUnmounted(() => {
        disconnect()
    })

    return {
        status,
        error,
        connected,
        reconnect: connect,
        disconnect
    }
}

// 辅助函数：检查是否为 Ref
function isRef<T>(value: unknown): value is Ref<T> {
    return value !== null && typeof value === 'object' && '__v_isRef' in value
}
