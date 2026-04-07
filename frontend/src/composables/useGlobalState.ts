/**
 * 全局状态 SSE Hook
 * 
 * 提供统一的全局状态管理，包括：
 * - 设备在线状态
 * - 播放状态
 * - 当前播放的播单
 * - 播放进度
 * - 当前播放的音频信息
 */
import { ref, computed, watch, isRef, type Ref } from 'vue'
import type { Song } from '@/api'

export interface CurrentSong {
    name: string
    singer: string
    album: string
    cover: string
    audio_id: string
}

export interface PlaylistInfo {
    id: string
    name: string
    current: number
    total: number
    play_mode: string
    songs?: Song[]
}

export interface GlobalState {
    device_id: string
    device_online: boolean
    device_name: string
    device_hardware: string
    play_status: 'playing' | 'paused' | 'stopped' | 'unknown'
    audio_id: string
    position: number
    duration: number
    media_type: number
    current_song: CurrentSong | null
    playlist: PlaylistInfo | null
}

// 全局单例状态，所有组件共享
const globalState = ref<GlobalState | null>(null)
const connected = ref(false)
const error = ref<Error | null>(null)

let abortController: AbortController | null = null
let reconnectTimer: number | null = null
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const reconnectDelay = 3000

export function useGlobalState(deviceId: Ref<string | null> | string | null): {
    state: typeof globalState
    connected: typeof connected
    error: typeof error
    isPlaying: ReturnType<typeof computed<boolean>>
    isPaused: ReturnType<typeof computed<boolean>>
    currentSong: ReturnType<typeof computed<CurrentSong | null>>
    playlist: ReturnType<typeof computed<PlaylistInfo | null>>
    progress: ReturnType<typeof computed<number>>
    reconnect: () => void
    disconnect: () => void
} {
    const deviceIdRef = isRef(deviceId) ? deviceId : ref(deviceId)

    // 计算属性
    const isPlaying = computed(() => {
        return globalState.value?.play_status === 'playing'
    })

    const isPaused = computed(() => {
        return globalState.value?.play_status === 'paused'
    })

    const currentSong = computed(() => {
        return globalState.value?.current_song || null
    })

    const playlist = computed(() => {
        return globalState.value?.playlist || null
    })

    const progress = computed(() => {
        if (!globalState.value) return 0
        const { position, duration } = globalState.value
        if (!duration) return 0
        return (position / duration) * 100
    })

    function connect(): void {
        // 检查是否已登录，未登录则不连接
        const token = localStorage.getItem('token')
        if (!token) {
            disconnect()
            return
        }

        // 如果没有设备 ID，不连接
        if (!deviceIdRef.value) {
            disconnect()
            return
        }

        // 如果已经连接到相同设备，不重复连接
        if (abortController && globalState.value?.device_id === deviceIdRef.value) {
            return
        }

        // 断开旧连接
        disconnect()

        // 创建新的 AbortController
        abortController = new AbortController()

        const url = `/api/state/stream?device_id=${deviceIdRef.value}`

        // 使用 fetch + ReadableStream 替代 EventSource，以支持自定义 headers
        fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'text/event-stream',
            },
            signal: abortController.signal,
        })
            .then(async (response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }

                connected.value = true
                error.value = null

                const reader = response.body?.getReader()
                const decoder = new TextDecoder()

                if (!reader) {
                    throw new Error('Response body is null')
                }

                let buffer = ''

                // eslint-disable-next-line no-constant-condition
                while (true) {
                    const { done, value } = await reader.read()

                    if (done) {
                        break
                    }

                    buffer += decoder.decode(value, { stream: true })

                    // 处理 SSE 消息
                    const lines = buffer.split('\n')
                    buffer = lines.pop() || '' // 保留最后一个不完整的行

                    let eventType = 'message'
                    let eventData = ''

                    for (const line of lines) {
                        if (line.startsWith('event:')) {
                            eventType = line.slice(6).trim()
                        } else if (line.startsWith('data:')) {
                            eventData = line.slice(5).trim()
                        } else if (line === '') {
                            // 空行表示消息结束
                            if (eventData) {
                                handleSSEMessage(eventType, eventData)
                                eventType = 'message'
                                eventData = ''
                            }
                        }
                    }
                }
            })
            .catch((err) => {
                if (err.name === 'AbortError') {
                    return
                }

                connected.value = false
                error.value = err as Error

                // 自动重连
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++

                    reconnectTimer = window.setTimeout(() => {
                        connect()
                    }, reconnectDelay)
                }
            })
    }

    function handleSSEMessage(eventType: string, data: string): void {
        if (eventType === 'state') {
            try {
                const parsedData = JSON.parse(data)
                globalState.value = parsedData
                error.value = null
                reconnectAttempts = 0
            } catch (err) {
                error.value = err as Error
            }
        } else if (eventType === 'heartbeat') {
            // 心跳事件，保持连接
        }
    }

    function disconnect(): void {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer)
            reconnectTimer = null
        }

        if (abortController) {
            abortController.abort()
            abortController = null
            connected.value = false
        }
    }

    // 监听设备 ID 变化
    watch(deviceIdRef, (newDeviceId, oldDeviceId) => {
        if (newDeviceId !== oldDeviceId) {
            globalState.value = null
            reconnectAttempts = 0
            if (newDeviceId) {
                connect()
            } else {
                disconnect()
            }
        }
    }, { immediate: true })

    // 组件卸载时不断开连接（因为是全局状态）
    // 但提供手动断开的方法

    return {
        state: globalState,
        connected,
        error,
        isPlaying,
        isPaused,
        currentSong,
        playlist,
        progress,
        reconnect: connect,
        disconnect
    }
}
