<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备列表</span>
          <el-button type="primary" :loading="loading" @click="fetchDevices">刷新</el-button>
        </div>
      </template>
      <el-alert v-if="error" :title="error" type="error" show-icon closable style="margin-bottom: 16px" />
      <el-table :data="devices" v-loading="loading" style="width: 100%">
        <el-table-column prop="deviceID" label="设备 ID" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="model" label="型号" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type Device } from '@/api'

const devices = ref<Device[]>([])
const loading = ref(false)
const error = ref('')

async function fetchDevices() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.listDevices()
    devices.value = data.devices
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '获取设备列表失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchDevices)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
