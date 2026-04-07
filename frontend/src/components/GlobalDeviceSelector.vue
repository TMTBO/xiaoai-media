<template>
  <div class="global-device-selector">
    <!-- 设备信息显示区域 -->
    <div
      v-if="selectedDevice"
      class="device-info"
    >
      <div class="info-item">
        <el-tag
          :type="selectedDevice.isOnline ? 'success' : 'info'"
          size="small"
        >
          {{ selectedDevice.isOnline ? '在线' : '离线' }}
        </el-tag>
      </div>
      <div class="info-item">
        <el-tag
          :type="playStatusType"
          size="small"
        >
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
        :loading="stopping"
        :disabled="!isPlaying"
        @click="stopPlayback"
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
            <el-tag
              :type="d.isOnline ? 'success' : 'info'"
              size="small"
            >
              {{ d.isOnline ? '在线' : '离线' }}
            </el-tag>
          </div>
        </el-option>
      </el-select>
      <el-button
        :loading="devicesLoading"
        :icon="Refresh"
        @click="loadDevices(true)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Monitor, Connection, CircleClose, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useDevices } from '@/composables/useDevices'
import { useGlobalState } from '@/composables/useGlobalState'
import { api } from '@/api'

const { devices, deviceId, devicesLoading, loadDevices } = useDevices()
const { state, isPlaying } = useGlobalState(deviceId)
const stopping = ref(false)

const selectedDevice = computed(() => {
  if (!deviceId.value) return null
  return devices.value.find(d => d.deviceID === deviceId.value) || null
})

// 从全局状态中获取播放状态
const playStatus = computed(() => {
  if (!state.value) return 0
  
  const statusMap: Record<string, number> = {
    'stopped': 0,
    'playing': 1,
    'paused': 2
  }
  
  return statusMap[state.value.play_status] ?? 0
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

async function stopPlayback(): Promise<void> {
  stopping.value = true
  try {
    await api.sendCommand('停止播放', deviceId.value || undefined)
    ElMessage.success('已发送停止指令')
  } catch (e: unknown) {
    ElMessage.error(e instanceof Error ? e.message : '停止失败')
  } finally {
    stopping.value = false
  }
}
</script>

<style scoped>
.global-device-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-light);
  box-shadow: var(--color-shadow-sm);
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
  color: var(--color-text-regular);
}

.info-item .el-icon {
  font-size: 16px;
  color: var(--color-text-secondary);
}

.device-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
