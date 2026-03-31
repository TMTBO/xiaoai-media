<template>
  <el-card>
    <template #header>配置管理</template>
    <el-alert title="密码字段不会回显，留空则保持原值不变" type="info" show-icon :closable="false" style="margin-bottom: 20px" />
    <el-alert title="Token 自动管理：登录成功后 Token 会自动保存到 .mi.token 文件，无需手动配置" type="success" show-icon :closable="false" style="margin-bottom: 20px" />
    <el-form v-loading="loading" label-width="120px" @submit.prevent="save">
      <el-form-item label="小米账号">
        <el-input v-model="form.MI_USER" placeholder="your_account@example.com" />
      </el-form-item>
      <el-form-item label="小米密码">
        <el-input v-model="form.MI_PASS" type="password" placeholder="留空则不修改密码" show-password />
        <div class="el-form-item__explain">用于自动登录和 Token 刷新</div>
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
      <el-divider content-position="left" style="margin: 20px 0 16px">音乐服务</el-divider>
      <el-form-item label="服务地址">
        <el-input v-model="form.MUSIC_API_BASE_URL" placeholder="http://localhost:5050" />
      </el-form-item>
      <el-form-item label="默认平台">
        <el-select v-model="form.MUSIC_DEFAULT_PLATFORM">
          <el-option value="tx" label="腾讯音乐 (tx)" />
          <el-option value="kw" label="酷我音乐 (kw)" />
          <el-option value="kg" label="酷狗音乐 (kg)" />
          <el-option value="wy" label="网易云音乐 (wy)" />
          <el-option value="mg" label="咪咕音乐 (mg)" />
        </el-select>
      </el-form-item>
      <el-divider content-position="left" style="margin: 20px 0 16px">本服务配置</el-divider>
      <el-form-item label="服务地址">
        <el-input v-model="form.SERVER_BASE_URL" placeholder="http://192.168.1.100:8000" />
        <div class="el-form-item__explain">⚠️ 必须使用局域网 IP，不能使用 localhost</div>
      </el-form-item>
      <el-divider content-position="left" style="margin: 20px 0 16px">对话监听</el-divider>
      <el-form-item label="启用监听">
        <div style="width: 100%">
          <el-switch v-model="form.ENABLE_CONVERSATION_POLLING" />
          <div class="el-form-item__explain">持续监听音箱对话，自动拦截播放指令</div>
        </div>
      </el-form-item>
      <el-form-item label="轮询间隔">
        <div style="width: 100%">
          <div>
            <el-input-number v-model="form.CONVERSATION_POLL_INTERVAL" :min="0.1" :max="60" :step="0.1" :precision="1" />
            <span style="margin-left: 8px">秒</span>
          </div>
          <div class="el-form-item__explain">对话监听的轮询间隔时间</div>
        </div>
      </el-form-item>
      <el-divider content-position="left" style="margin: 20px 0 16px">播放监控</el-divider>
      <el-form-item label="启用监控">
        <div style="width: 100%">
          <el-switch v-model="form.ENABLE_PLAYBACK_MONITOR" />
          <div class="el-form-item__explain">监控播放状态，自动播放下一曲</div>
        </div>
      </el-form-item>
      <el-form-item label="监控模式">
        <div style="width: 100%">
          <el-radio-group v-model="form.PLAYBACK_MODE">
            <el-radio value="monitor">轮询模式</el-radio>
            <el-radio value="controller">定时器模式</el-radio>
          </el-radio-group>
          <div class="el-form-item__explain">
            轮询模式：定期检查播放状态（兼容性好，但较耗性能）<br />
            定时器模式：根据音频时长设置定时器（高效，但依赖准确的时长信息）
          </div>
        </div>
      </el-form-item>
      <el-form-item label="轮询间隔" v-if="form.PLAYBACK_MODE === 'monitor'">
        <div style="width: 100%">
          <div>
            <el-input-number v-model="form.PLAYBACK_MONITOR_INTERVAL" :min="0.5" :max="60" :step="0.1" :precision="1" />
            <span style="margin-left: 8px">秒</span>
          </div>
          <div class="el-form-item__explain">播放监控的轮询间隔时间（建议 2-5 秒）</div>
        </div>
      </el-form-item>
      <el-divider content-position="left" style="margin: 20px 0 16px">唤醒词配置</el-divider>
      <el-form-item label="唤醒词过滤">
        <div style="width: 100%">
          <el-switch v-model="form.ENABLE_WAKE_WORD_FILTER" />
          <div class="el-form-item__explain">只处理包含唤醒词的指令</div>
        </div>
      </el-form-item>
      <el-form-item label="唤醒词列表">
        <div style="width: 100%">
          <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px">
            <el-tag v-for="(word, index) in form.WAKE_WORDS" :key="index" closable @close="removeWakeWord(index)">
              {{ word }}
            </el-tag>
            <el-input v-if="showWakeWordInput" ref="wakeWordInputRef" v-model="newWakeWord" size="small"
              style="width: 120px" @blur="addWakeWord" @keyup.enter="addWakeWord" />
            <el-button v-else size="small" @click="showWakeWordInput = true">+ 添加唤醒词</el-button>
          </div>
          <div class="el-form-item__explain">只有包含这些唤醒词的指令才会被处理</div>
        </div>
      </el-form-item>
      <el-divider content-position="left" style="margin: 20px 0 16px">日志配置</el-divider>
      <el-form-item label="日志级别">
        <el-select v-model="form.LOG_LEVEL">
          <el-option value="DEBUG" label="DEBUG - 调试" />
          <el-option value="INFO" label="INFO - 信息" />
          <el-option value="WARNING" label="WARNING - 警告" />
          <el-option value="ERROR" label="ERROR - 错误" />
          <el-option value="CRITICAL" label="CRITICAL - 严重" />
        </el-select>
      </el-form-item>
      <el-divider content-position="left" style="margin: 20px 0 16px">代理访问控制</el-divider>
      <el-form-item label="局域网跳过认证">
        <div style="width: 100%">
          <el-switch v-model="form.PROXY_SKIP_AUTH_FOR_LAN" />
          <div class="el-form-item__explain">允许局域网内的设备（如小爱音箱）无需认证访问代理接口</div>
        </div>
      </el-form-item>
      <el-form-item label="局域网 IP 段">
        <div style="width: 100%">
          <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px">
            <el-tag v-for="(network, index) in form.PROXY_LAN_NETWORKS" :key="index" closable @close="removeLanNetwork(index)">
              {{ network }}
            </el-tag>
            <el-input v-if="showLanNetworkInput" ref="lanNetworkInputRef" v-model="newLanNetwork" size="small"
              style="width: 180px" placeholder="192.168.0.0/16" @blur="addLanNetwork" @keyup.enter="addLanNetwork" />
            <el-button v-else size="small" @click="showLanNetworkInput = true">+ 添加 IP 段</el-button>
          </div>
          <div class="el-form-item__explain">CIDR 格式的局域网 IP 段，如 192.168.0.0/16</div>
        </div>
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
import { ref, onMounted, nextTick, watch } from 'vue'
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
  MI_DID: '',
  MI_REGION: 'cn',
  MUSIC_API_BASE_URL: 'http://localhost:5050',
  MUSIC_DEFAULT_PLATFORM: 'tx',
  SERVER_BASE_URL: 'http://localhost:8000',
  ENABLE_CONVERSATION_POLLING: false,
  CONVERSATION_POLL_INTERVAL: 2.0,
  ENABLE_PLAYBACK_MONITOR: true,
  PLAYBACK_MONITOR_INTERVAL: 3.0,
  PLAYBACK_MODE: 'monitor',
  ENABLE_WAKE_WORD_FILTER: true,
  WAKE_WORDS: [],
  LOG_LEVEL: 'INFO',
  PROXY_SKIP_AUTH_FOR_LAN: true,
  PROXY_LAN_NETWORKS: ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12', '127.0.0.0/8'],
})

const showWakeWordInput = ref(false)
const newWakeWord = ref('')
const wakeWordInputRef = ref()

const showLanNetworkInput = ref(false)
const newLanNetwork = ref('')
const lanNetworkInputRef = ref()

// 当显示输入框时自动聚焦
watch(showWakeWordInput, (show) => {
  if (show) {
    nextTick(() => {
      wakeWordInputRef.value?.focus()
    })
  }
})

watch(showLanNetworkInput, (show) => {
  if (show) {
    nextTick(() => {
      lanNetworkInputRef.value?.focus()
    })
  }
})

async function addWakeWord() {
  const word = newWakeWord.value.trim()
  if (word && !form.value.WAKE_WORDS.includes(word)) {
    form.value.WAKE_WORDS.push(word)
    newWakeWord.value = ''
    showWakeWordInput.value = false
    // 自动保存配置
    await save()
  } else {
    newWakeWord.value = ''
    showWakeWordInput.value = false
  }
}

function removeWakeWord(index: number) {
  form.value.WAKE_WORDS.splice(index, 1)
}

async function addLanNetwork() {
  const network = newLanNetwork.value.trim()
  if (network && !form.value.PROXY_LAN_NETWORKS.includes(network)) {
    form.value.PROXY_LAN_NETWORKS.push(network)
    newLanNetwork.value = ''
    showLanNetworkInput.value = false
    // 自动保存配置
    await save()
  } else {
    newLanNetwork.value = ''
    showLanNetworkInput.value = false
  }
}

function removeLanNetwork(index: number) {
  form.value.PROXY_LAN_NETWORKS.splice(index, 1)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getConfig()
    // Password is always cleared for security
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
    // Don't send empty password (keep existing)
    if (!payload.MI_PASS) delete payload.MI_PASS
    await api.updateConfig(payload)
    success.value = true
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '保存配置失败'
  } finally {
    saving.value = false
  }
}

onMounted(() => { load(); loadDevices() })
</script>

<style scoped>
.el-form-item__explain {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  margin-top: 4px;
}
</style>
