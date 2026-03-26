<template>
  <el-card>
    <template #header>TTS 文字朗读</template>
    <el-form label-width="100px" @submit.prevent="submit">
      <el-form-item label="文字内容">
        <el-input v-model="text" type="textarea" :rows="4" placeholder="请输入要朗读的文字..." />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading">发送朗读</el-button>
      </el-form-item>
    </el-form>
    <el-alert v-if="error" :title="error" type="error" show-icon />
    <el-alert v-if="success" title="朗读指令已发送！" type="success" show-icon />
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/api'
import { useDevices } from '@/composables/useDevices'

const text = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)
const { deviceId } = useDevices()

async function submit() {
  if (!text.value.trim()) return
  loading.value = true
  error.value = ''
  success.value = false
  try {
    await api.textToSpeech(text.value, deviceId.value || undefined)
    success.value = true
    text.value = ''
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '发送失败'
  } finally {
    loading.value = false
  }
}
</script>
