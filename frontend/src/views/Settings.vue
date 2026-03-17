<template>
  <el-card>
    <template #header>配置管理</template>
    <el-alert title="密码/Token 字段不会回显，留空则保持原值不变" type="info" show-icon :closable="false" style="margin-bottom: 20px" />
    <el-form v-loading="loading" label-width="120px" @submit.prevent="save">
      <el-form-item label="小米账号">
        <el-input v-model="form.MI_USER" placeholder="your_account@example.com" />
      </el-form-item>
      <el-form-item label="小米密码">
        <el-input v-model="form.MI_PASS" type="password" placeholder="留空则不修改密码" show-password />
      </el-form-item>
      <el-form-item label="Pass Token">
        <el-input v-model="form.MI_PASS_TOKEN" type="password" placeholder="留空则不修改 Token" show-password />
        <div class="el-form-item__explain">可替代密码登录，从抓包或已有 Token 文件中获取</div>
      </el-form-item>
      <el-form-item label="默认设备">
        <el-select v-model="form.MI_DID" placeholder="留空则使用第一个设备" clearable style="flex: 1; margin-right: 8px"
          :loading="devicesLoading" no-data-text="暂无设备，请先保存账号配置后点击刷新">
          <el-option v-for="d in devices" :key="d.deviceID" :label="`${d.name} (${d.deviceID})`" :value="d.deviceID" />
        </el-select>
        <el-button :loading="devicesLoading" @click="loadDevices">
          <el-icon>
            <Refresh />
          </el-icon>
        </el-button>
      </el-form-item>
      <el-form-item label="区域">
        <el-select v-model="form.MI_REGION">
          <el-option value="cn" label="中国 (cn)" />
          <el-option value="de" label="德国 (de)" />
          <el-option value="us" label="美国 (us)" />
          <el-option value="sg" label="新加坡 (sg)" />
          <el-option value="ru" label="俄罗斯 (ru)" />
          <el-option value="i2" label="印度 (i2)" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" :loading="saving">保存配置</el-button>
        <el-button @click="load">重新加载</el-button>
      </el-form-item>
    </el-form>
    <el-alert v-if="error" :title="error" type="error" show-icon />
    <el-alert v-if="success" title="配置保存成功！" type="success" show-icon />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { api, type Config, type Device } from '@/api'

const loading = ref(false)
const saving = ref(false)
const devicesLoading = ref(false)
const error = ref('')
const success = ref(false)
const devices = ref<Device[]>([])

const form = ref<Config>({
  MI_USER: '',
  MI_PASS: '',
  MI_PASS_TOKEN: '',
  MI_DID: '',
  MI_REGION: 'cn',
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getConfig()
    // Keep masked sentinel (***) so user can see the field is already set.
    // Password is always cleared for security; token shows its masked state.
    form.value = { ...data, MI_PASS: '' }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '加载配置失败'
  } finally {
    loading.value = false
  }
}

async function loadDevices() {
  devicesLoading.value = true
  error.value = ''
  try {
    const data = await api.listDevices()
    devices.value = data.devices
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '获取设备列表失败，请确认账号配置正确'
  } finally {
    devicesLoading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = false
  try {
    const payload: Partial<Config> = { ...form.value }
    if (!payload.MI_PASS) delete payload.MI_PASS
    // '***' means "already set, don't overwrite"
    if (!payload.MI_PASS_TOKEN || payload.MI_PASS_TOKEN === '***') delete payload.MI_PASS_TOKEN
    await api.updateConfig(payload)
    success.value = true
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '保存配置失败'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
