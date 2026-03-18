<template>
  <el-card>
    <template #header>语音指令</template>
    <el-form label-width="100px" @submit.prevent="submit">
      <el-form-item label="指令内容">
        <el-input v-model="command" placeholder="例如：查询天气、播放音乐" clearable />
      </el-form-item>
      <el-form-item label="目标设备">
        <el-select v-model="deviceId" placeholder="留空则使用默认设备" clearable style="flex: 1; margin-right: 8px"
          :loading="devicesLoading" no-data-text="暂无设备，请先在配置页填写账号后点击刷新">
          <el-option v-for="d in devices" :key="d.deviceID" :label="`${d.name} (${d.deviceID})`" :value="d.deviceID" />
        </el-select>
        <el-button :loading="devicesLoading" @click="loadDevices">
          <el-icon>
            <Refresh />
          </el-icon>
        </el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading">发送指令</el-button>
      </el-form-item>
    </el-form>
    <el-descriptions v-if="result" title="执行结果" border :column="1" style="margin-top: 16px">
      <el-descriptions-item label="设备 ID">{{ result.device }}</el-descriptions-item>
      <el-descriptions-item label="指令">{{ result.command }}</el-descriptions-item>
      <el-descriptions-item label="结果">{{ JSON.stringify(result.result) }}</el-descriptions-item>
      <el-descriptions-item label="方法">{{ result.method }}</el-descriptions-item>
    </el-descriptions>
    <el-alert v-if="error" :title="error" type="error" show-icon />
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { api } from '@/api'
import { useDevices } from '@/composables/useDevices'

const command = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<{ device: string; command: string; result: unknown; method: string } | null>(null)
const { devices, devicesLoading, loadDevices, deviceId } = useDevices()

async function submit() {
  if (!command.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await api.sendCommand(command.value, deviceId.value || undefined)
    command.value = ''
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '发送失败'
  } finally {
    loading.value = false
  }
}
</script>
