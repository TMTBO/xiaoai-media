<template>
  <el-card>
    <template #header>
      音量控制
    </template>
    <el-form label-width="100px">
      <el-form-item label="音量">
        <el-slider
          v-model="volume"
          :min="0"
          :max="100"
          show-input
          style="width: 400px"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="submit"
        >
          设置音量
        </el-button>
      </el-form-item>
    </el-form>
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
    />
    <el-alert
      v-if="success"
      :title="`音量已设置为 ${lastVolume}`"
      type="success"
      show-icon
    />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { api } from '@/api'
import { useDevices } from '@/composables/useDevices'

const volume = ref(50)
const loading = ref(false)
const error = ref('')
const success = ref(false)
const lastVolume = ref(0)
const { deviceId } = useDevices()

async function loadCurrentVolume(): Promise<void> {
  try {
    const result = await api.getVolume(deviceId.value || undefined)
    if (result.volume !== null && result.volume !== undefined) {
      volume.value = result.volume
    }
  } catch (e: unknown) {
    error.value = 'Failed to load current volume'
  }
}

async function submit(): Promise<void> {
  loading.value = true
  error.value = ''
  success.value = false
  try {
    await api.setVolume(volume.value, deviceId.value || undefined)
    lastVolume.value = volume.value
    success.value = true
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '设置失败'
  } finally {
    loading.value = false
  }
}

// Load current volume when component mounts
onMounted(() => {
  loadCurrentVolume()
})

// Reload volume when device changes
watch(deviceId, () => {
  loadCurrentVolume()
})
</script>
