<template>
  <div class="global-device-selector">
    <!-- 设备信息显示区域 -->
    <div v-if="selectedDevice" class="device-info">
      <div class="info-item">
        <el-tag :type="selectedDevice.isOnline ? 'success' : 'info'" size="small">
          {{ selectedDevice.isOnline ? '在线' : '离线' }}
        </el-tag>
      </div>
      <div class="info-item">
        <el-tag :type="playStatusType" size="small">
          {{ playStatusText }}
        </el-tag>
      </div>
      <div class="info-item">
        <el-icon><Monitor /></el-icon>
        <span>{{ selectedDevice.hardware }}</span>
      </div>
      <div class="info-item">
        <el-icon><Connection /></el-icon>
        <span>{{ selectedDevice.localip || '未知' }}</span>
      </div>
      <el-button
        type="danger"
        size="small"
        :icon="CircleClose"
        @click="stopPlayback"
        :loading="stopping"
        :disabled="!isPlaying"
      >
        停止
      </el-button>
    </div>

    <!-- 设备选择器 -->
    <div class="device-selector">
      <el-select
        v-model="deviceId"
        placeholder="选择设备"
        style="width: 280px"
        :loading="devicesLoading"
        filterable
      >
        <el-option
          v-for="d in devices"
          :key="d.deviceID"
          :label="`${d.name} (${d.hardware})`"
          :value="d.deviceID"
        >
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>{{ d.name }}</span>
            <el-tag :type="d.isOnline ? 'success' : 'info'" size="small">
              {{ d.isOnline ? '在线' : '离线' }}
            </el-tag>
          </div>
        </el-option>
      </el-select>
      <el-button :loading="devicesLoading" @click="loadDevices(true)" :icon="Refresh" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { Monitor, Connection, CircleClose, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useDevices } from '@/composables/useDevices'
import { api } from '@/api'

const { devices, deviceId, devicesLoading, loadDevices } = useDevices()
const stopping = ref(false)
const playStatus = ref<number>(0) // 0=停止, 1=播放中, 2=暂停
let statusTimer: number | null = null

const selectedDevice = computed(() => {
  if (!deviceId.value) return null
  return devices.value.find(d => d.deviceID === deviceId.value) || null
})

const isPlaying = computed(() => {
  return playStatus.value === 1 || playStatus.value === 2
})

const playStatusText = computed(() => {
  const statusMap: Record<number, string> = {
    0: '未播放',
    1: '播放中',
    2: '已暂停'
  }
  return statusMap[playStatus.value] || '未知'
})

const playStatusType = computed(() => {
  const typeMap: Record<number, string> = {
    0: 'info',
    1: 'success',
    2: 'warning'
  }
  return typeMap[playStatus.value] || 'info'
})

async function fetchPlayStatus() {
  if (!deviceId.value) return
  
  try {
    const result = await api.getPlayerStatus(deviceId.value)
    const statusData = result?.status?.data
    
    if (statusData?.info) {
      try {
        const info = typeof statusData.info === 'string' 
          ? JSON.parse(statusData.info) 
          : statusData.info
        playStatus.value = info.status ?? 0
      } catch (e) {
        console.error('Failed to parse player status:', e)
        playStatus.value = 0
      }
    } else {
      playStatus.value = 0
    }
  } catch (e) {
    // 静默失败，不显示错误
    playStatus.value = 0
  }
}

function startStatusPolling() {
  stopStatusPolling()
  fetchPlayStatus()
  statusTimer = window.setInterval(() => {
    fetchPlayStatus()
  }, 3000) // 每3秒更新一次状态
}

function stopStatusPolling() {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
}

async function stopPlayback() {
  stopping.value = true
  try {
    await api.sendCommand('停止播放', deviceId.value || undefined)
    ElMessage.success('已发送停止指令')
    // 立即更新状态
    await fetchPlayStatus()
  } catch (e: unknown) {
    ElMessage.error(e instanceof Error ? e.message : '停止失败')
  } finally {
    stopping.value = false
  }
}

// 监听设备变化
watch(deviceId, () => {
  playStatus.value = 0
  if (deviceId.value) {
    startStatusPolling()
  } else {
    stopStatusPolling()
  }
})

// 组件挂载时开始轮询
onMounted(() => {
  if (deviceId.value) {
    startStatusPolling()
  }
})

// 组件卸载时停止轮询
onUnmounted(() => {
  stopStatusPolling()
})
</script>

<style scoped>
.global-device-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.device-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.info-item .el-icon {
  font-size: 16px;
  color: #909399;
}

.device-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
