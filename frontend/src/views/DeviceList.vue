<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备列表</span>
          <el-button type="primary" :loading="devicesLoading" @click="loadDevices(true)">刷新</el-button>
        </div>
      </template>
      <el-alert v-if="devicesError" :title="devicesError" type="error" show-icon closable style="margin-bottom: 16px" />
      <el-table :data="devices" v-loading="devicesLoading" style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="hardware" label="硬件型号" width="100" />
        <el-table-column prop="model" label="固件型号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="deviceID" label="设备 UUID" min-width="280" show-overflow-tooltip />
        <el-table-column prop="miotDID" label="MiIO DID" width="120" />
        <el-table-column label="在线" width="80">
          <template #default="{ row }">
            <el-tag :type="row.isOnline ? 'success' : 'info'" size="small">
              {{ row.isOnline ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="localip" label="IP 地址" width="140" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useDevices } from '@/composables/useDevices'

const { devices, devicesLoading, devicesError, loadDevices } = useDevices()
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
