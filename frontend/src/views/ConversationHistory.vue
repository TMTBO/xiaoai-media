<template>
  <el-card>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center">
        <span>对话记录</span>
        <div style="display: flex; gap: 8px">
          <el-select v-model="deviceId" placeholder="选择设备" clearable style="width: 250px"
            :loading="devicesLoading" no-data-text="暂无设备，请先在配置页填写账号后点击刷新">
            <el-option v-for="d in devices" :key="d.deviceID" :label="`${d.name} (${d.deviceID})`" :value="d.deviceID" />
          </el-select>
          <el-button :loading="devicesLoading" @click="loadDevices">
            <el-icon>
              <Refresh />
            </el-icon>
          </el-button>
          <el-button type="primary" :loading="loading" @click="fetchConversations">
            <el-icon>
              <Search />
            </el-icon>
            查询对话
          </el-button>
        </div>
      </div>
    </template>

    <el-alert v-if="error" :title="error" type="error" show-icon style="margin-bottom: 16px" closable />

    <el-empty v-if="!loading && conversations.length === 0" description="暂无对话记录" />

    <el-timeline v-else>
      <el-timeline-item
        v-for="(conv, index) in conversations"
        :key="index"
        :timestamp="formatTimestamp(conv.timestamp_ms)"
        placement="top"
      >
        <el-card>
          <div class="conversation-item">
            <div class="question">
              <el-icon class="icon" color="#409eff">
                <User />
              </el-icon>
              <div class="content">
                <div class="label">用户问题</div>
                <div class="text">{{ conv.question }}</div>
              </div>
            </div>
            <el-divider />
            <div class="answer">
              <el-icon class="icon" color="#67c23a">
                <ChatDotRound />
              </el-icon>
              <div class="content">
                <div class="label">小爱回答</div>
                <div class="text">{{ conv.content }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <div v-if="loading" style="text-align: center; padding: 40px">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <div style="margin-top: 16px; color: #909399">加载中...</div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh, Search, User, ChatDotRound, Loading } from '@element-plus/icons-vue'
import { api } from '@/api'
import { useDevices } from '@/composables/useDevices'
import { ElMessage } from 'element-plus'

interface Conversation {
  timestamp_ms: number
  question: string
  content: string
}

const { devices, devicesLoading, loadDevices, deviceId } = useDevices()
const loading = ref(false)
const error = ref('')
const conversations = ref<Conversation[]>([])

function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 如果是今天
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`
  }
  
  // 如果是昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`
  }
  
  // 如果在一周内
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${days[date.getDay()]} ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`
  }
  
  // 其他情况显示完整日期
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

async function fetchConversations() {
  loading.value = true
  error.value = ''
  try {
    const result = await api.getConversation(deviceId.value || undefined)
    conversations.value = result.conversations || []
    
    if (conversations.value.length === 0) {
      ElMessage.info('暂无对话记录')
    } else {
      ElMessage.success(`成功获取 ${conversations.value.length} 条对话记录`)
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '获取对话记录失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.conversation-item {
  padding: 8px 0;
}

.question,
.answer {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.icon {
  font-size: 24px;
  margin-top: 4px;
  flex-shrink: 0;
}

.content {
  flex: 1;
}

.label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.text {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  word-break: break-word;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
}

:deep(.el-divider--horizontal) {
  margin: 12px 0;
}
</style>
