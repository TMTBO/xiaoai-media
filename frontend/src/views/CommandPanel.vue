<template>
  <el-card>
    <template #header>语音指令</template>
    
    <!-- Quick command buttons -->
    <div style="margin-bottom: 16px">
      <el-text style="display: block; margin-bottom: 8px; font-weight: 500">快捷指令</el-text>
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px">
        <el-button size="small" @click="sendQuickCommand('上一首')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><CaretLeft /></el-icon>
          <span style="font-size: 12px">上一首</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('下一首')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><CaretRight /></el-icon>
          <span style="font-size: 12px">下一首</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('暂停')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><VideoPause /></el-icon>
          <span style="font-size: 12px">暂停</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('继续播放')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><VideoPlay /></el-icon>
          <span style="font-size: 12px">继续</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('停止播放')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><CircleClose /></el-icon>
          <span style="font-size: 12px">停止</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('音量加大')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><Plus /></el-icon>
          <span style="font-size: 12px">音量+</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('音量减小')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><Minus /></el-icon>
          <span style="font-size: 12px">音量-</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('现在几点')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><Clock /></el-icon>
          <span style="font-size: 12px">时间</span>
        </el-button>
        <el-button size="small" @click="sendQuickCommand('今天天气怎么样')" :loading="loading" 
          style="width: 100%; height: 60px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px;">
          <el-icon style="font-size: 20px; margin-bottom: 4px"><Sunny /></el-icon>
          <span style="font-size: 12px">天气</span>
        </el-button>
      </div>
    </div>

    <el-divider />

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
import { 
  Refresh, 
  CaretLeft, 
  CaretRight, 
  VideoPause, 
  VideoPlay, 
  CircleClose,
  Plus,
  Minus,
  Clock,
  Sunny
} from '@element-plus/icons-vue'
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

async function sendQuickCommand(cmd: string) {
  command.value = cmd
  await submit()
}
</script>
