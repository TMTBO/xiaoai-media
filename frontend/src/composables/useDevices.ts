import { ref } from 'vue'
import { api, type Device } from '@/api'

// ---------------------------------------------------------------------------
// Module-level singleton state — shared across ALL useDevices() callers in
// the same app session. Devices are fetched once and reused; call
// loadDevices(true) to force a fresh fetch from the server.
// ---------------------------------------------------------------------------
const _devices = ref<Device[]>([])
const _deviceId = ref('')
const _loading = ref(false)
const _error = ref('')
// Tracks the in-flight init promise so concurrent callers don't double-fetch
let _initPromise: Promise<void> | null = null

function _init(): void {
    // 检查是否已登录，未登录则不初始化
    const token = localStorage.getItem('token')
    if (!token) {
        return
    }

    if (_initPromise) return
    _loading.value = true
    _error.value = ''
    _initPromise = Promise.all([
        api.listDevices(false),
        api.getConfig(),
    ]).then(([devData, cfg]) => {
        _devices.value = devData.devices
        if (!_deviceId.value && cfg.MI_DID) _deviceId.value = cfg.MI_DID
    }).catch((e: unknown) => {
        _error.value = e instanceof Error ? e.message : '获取设备列表失败'
        _initPromise = null  // allow retry on next mount
    }).finally(() => {
        _loading.value = false
    })
}

export function useDevices(): {
    devices: typeof _devices
    deviceId: typeof _deviceId
    devicesLoading: typeof _loading
    devicesError: typeof _error
    loadDevices: (forceRefresh?: boolean) => Promise<void>
} {
    /** Refresh device list. Pass forceRefresh=true to bypass backend cache. */
    async function loadDevices(forceRefresh = false): Promise<void> {
        _loading.value = true
        _error.value = ''
        try {
            const data = await api.listDevices(forceRefresh)
            _devices.value = data.devices
        } catch (e: unknown) {
            _error.value = e instanceof Error ? e.message : '获取设备列表失败'
        } finally {
            _loading.value = false
        }
    }

    // Kick off the one-time auto-init (no-op if already running or done)
    _init()

    return {
        devices: _devices,
        deviceId: _deviceId,
        devicesLoading: _loading,
        devicesError: _error,
        loadDevices,
    }
}
