import { ref } from 'vue'
import { api, type Device } from '@/api'

export function useDevices() {
    const devices = ref<Device[]>([])
    const deviceId = ref('')
    const devicesLoading = ref(false)
    const devicesError = ref('')

    async function loadDevices() {
        devicesLoading.value = true
        devicesError.value = ''
        try {
            const data = await api.listDevices()
            devices.value = data.devices
        } catch (e: unknown) {
            devicesError.value = e instanceof Error ? e.message : '获取设备列表失败'
        } finally {
            devicesLoading.value = false
        }
    }

    // Auto-load on composable init: fetch devices and resolve default device ID
    api.getConfig().then(cfg => {
        if (!deviceId.value && cfg.MI_DID) {
            deviceId.value = cfg.MI_DID
        }
    }).catch(() => { })

    loadDevices()

    return { devices, deviceId, devicesLoading, devicesError, loadDevices }
}
