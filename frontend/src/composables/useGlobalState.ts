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

let eventSource: EventSource | null = null
let reconnectTimer: number | null = null
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const reconnectDelay = 3000

export function useGlobalState(deviceId: Ref<string | null> | string | null) {
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

    function connect() {
        // 如果没有设备 ID，不连接
        if (!deviceIdRef.value) {
            disconnect()
            return
        }

        // 如果已经连接到相同设备，不重复连接
        if (eventSource && globalState.value?.device_id === deviceIdRef.value) {
            return
        }

        // 断开旧连接
        disconnect()

        try {
            const url = `/api/state/stream?device_id=${deviceIdRef.value}`
            eventSource = new EventSource(url)

            eventSource.addEventListener('state', (event: MessageEvent) => {
                try {
                    const data = JSON.parse(event.data)
                    globalState.value = data
                    error.value = null
                    reconnectAttempts = 0
                } catch (err) {
                    console.error('Failed to parse SSE state data:', err)
                    error.value = err as Error
                }
            })

            eventSource.addEventListener('heartbeat', () => {
                // 心跳事件，保持连接
            })

            eventSource.onopen = () => {
                connected.value = true
                error.value = null
                console.log('Global state SSE connected:', deviceIdRef.value)
            }

            eventSource.onerror = (err) => {
                console.error('Global state SSE error:', err)
                connected.value = false
                error.value = new Error('SSE connection failed')

                // 自动重连
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++
                    console.log(`Reconnecting... (${reconnectAttempts}/${maxReconnectAttempts})`)

                    reconnectTimer = window.setTimeout(() => {
                        connect()
                    }, reconnectDelay)
                } else {
                    console.error('Max reconnect attempts reached')
                }
            }
        } catch (err) {
            console.error('Failed to create EventSource:', err)
            error.value = err as Error
        }
    }

    function disconnect() {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer)
            reconnectTimer = null
        }

        if (eventSource) {
            eventSource.close()
            eventSource = null
            connected.value = false
            console.log('Global state SSE disconnected')
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
