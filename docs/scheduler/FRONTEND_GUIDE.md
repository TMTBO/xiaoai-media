# 定时任务管理后台前端开发指南

## 页面结构

建议在管理后台添加一个"定时任务"菜单项，包含以下子页面：

1. 任务列表页
2. 创建任务页
3. 编辑任务页
4. 快捷操作面板

## 1. 任务列表页

### 功能需求

- 展示所有定时任务
- 按任务类型筛选（全部/播放音乐/播放播放列表/提醒）
- 显示任务状态（启用/禁用）
- 显示下次执行时间
- 快速启用/禁用开关
- 编辑和删除操作

### 参考实现（Vue 3 + TypeScript）

```vue
<template>
  <div class="scheduler-list">
    <div class="header">
      <h2>定时任务管理</h2>
      <button @click="showCreateDialog = true" class="btn-primary">
        创建任务
      </button>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <select v-model="filterType">
        <option value="">全部任务</option>
        <option value="play_music">播放音乐</option>
        <option value="play_playlist">播放播放列表</option>
        <option value="reminder">提醒</option>
      </select>
    </div>

    <!-- 任务列表 -->
    <div class="task-list">
      <div v-for="task in filteredTasks" :key="task.task_id" class="task-item">
        <div class="task-info">
          <div class="task-header">
            <h3>{{ task.name }}</h3>
            <span :class="['task-type', task.task_type]">
              {{ getTaskTypeLabel(task.task_type) }}
            </span>
          </div>
          
          <div class="task-details">
            <div class="detail-item">
              <span class="label">触发方式：</span>
              <span class="value">
                {{ task.trigger_type === 'cron' ? task.cron_expression : '一次性' }}
              </span>
            </div>
            
            <div class="detail-item" v-if="task.next_run_time">
              <span class="label">下次执行：</span>
              <span class="value">{{ formatDateTime(task.next_run_time) }}</span>
            </div>
            
            <div class="detail-item">
              <span class="label">参数：</span>
              <span class="value">{{ formatParams(task.params) }}</span>
            </div>
          </div>
        </div>

        <div class="task-actions">
          <label class="switch">
            <input 
              type="checkbox" 
              :checked="task.enabled"
              @change="toggleTask(task)"
            />
            <span class="slider"></span>
          </label>
          
          <button @click="editTask(task)" class="btn-icon">
            <i class="icon-edit"></i>
          </button>
          
          <button @click="deleteTask(task)" class="btn-icon btn-danger">
            <i class="icon-delete"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 快捷操作面板 -->
    <QuickActions />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'
import QuickActions from './QuickActions.vue'

interface Task {
  task_id: string
  task_type: string
  name: string
  trigger_type: string
  cron_expression?: string
  run_date?: string
  params: Record<string, any>
  enabled: boolean
  next_run_time?: string
  created_at: string
  updated_at: string
}

const tasks = ref<Task[]>([])
const filterType = ref('')
const showCreateDialog = ref(false)

const filteredTasks = computed(() => {
  if (!filterType.value) return tasks.value
  return tasks.value.filter(t => t.task_type === filterType.value)
})

async function loadTasks() {
  try {
    const response = await api.get('/api/scheduler/tasks')
    tasks.value = response.data
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

async function toggleTask(task: Task) {
  try {
    await api.put(`/api/scheduler/tasks/${task.task_id}`, {
      enabled: !task.enabled
    })
    await loadTasks()
  } catch (error) {
    console.error('切换任务状态失败:', error)
  }
}

async function deleteTask(task: Task) {
  if (!confirm(`确定要删除任务"${task.name}"吗？`)) return
  
  try {
    await api.delete(`/api/scheduler/tasks/${task.task_id}`)
    await loadTasks()
  } catch (error) {
    console.error('删除任务失败:', error)
  }
}

function editTask(task: Task) {
  // 跳转到编辑页面或打开编辑对话框
  console.log('编辑任务:', task)
}

function getTaskTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    play_music: '播放音乐',
    play_playlist: '播放播放列表',
    reminder: '提醒'
  }
  return labels[type] || type
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function formatParams(params: Record<string, any>): string {
  if (params.song_name) {
    return params.artist 
      ? `${params.song_name} - ${params.artist}`
      : params.song_name
  }
  if (params.playlist_id) {
    return `播放列表: ${params.playlist_id}`
  }
  if (params.message) {
    return params.message
  }
  return JSON.stringify(params)
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.scheduler-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  margin-bottom: 20px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-info {
  flex: 1;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.task-type {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.task-type.play_music {
  background: #e3f2fd;
  color: #1976d2;
}

.task-type.play_playlist {
  background: #f3e5f5;
  color: #7b1fa2;
}

.task-type.reminder {
  background: #fff3e0;
  color: #f57c00;
}

.task-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.detail-item .label {
  color: #666;
  font-weight: 500;
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4caf50;
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.btn-icon {
  padding: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: #f5f5f5;
}

.btn-icon.btn-danger:hover {
  background: #ffebee;
  color: #d32f2f;
}
</style>
```

## 2. 快捷操作面板

```vue
<template>
  <div class="quick-actions">
    <h3>快捷操作</h3>
    
    <div class="action-cards">
      <!-- 快速提醒 -->
      <div class="action-card">
        <h4>⏰ 快速提醒</h4>
        <input 
          v-model="reminderMessage" 
          placeholder="提醒内容"
          class="input"
        />
        <input 
          v-model.number="reminderMinutes" 
          type="number"
          placeholder="延迟分钟数"
          class="input"
          min="1"
          max="1440"
        />
        <button @click="createQuickReminder" class="btn-primary">
          创建提醒
        </button>
      </div>

      <!-- 快速播放音乐 -->
      <div class="action-card">
        <h4>🎵 定时播放音乐</h4>
        <input 
          v-model="musicSongName" 
          placeholder="歌曲名称"
          class="input"
        />
        <input 
          v-model="musicArtist" 
          placeholder="歌手（可选）"
          class="input"
        />
        <input 
          v-model="musicCron" 
          placeholder="Cron表达式 (如: 0 7 * * *)"
          class="input"
        />
        <button @click="createQuickPlayMusic" class="btn-primary">
          创建任务
        </button>
      </div>

      <!-- 快速播放播放列表 -->
      <div class="action-card">
        <h4>📋 定时播放播放列表</h4>
        <select v-model="playlistId" class="input">
          <option value="">选择播放列表</option>
          <option v-for="pl in playlists" :key="pl.id" :value="pl.id">
            {{ pl.name }}
          </option>
        </select>
        <input 
          v-model="playlistCron" 
          placeholder="Cron表达式 (如: 0 7 * * *)"
          class="input"
        />
        <button @click="createQuickPlayPlaylist" class="btn-primary">
          创建任务
        </button>
      </div>
    </div>

    <!-- Cron 表达式帮助 -->
    <div class="cron-help">
      <h4>Cron 表达式示例</h4>
      <ul>
        <li><code>0 7 * * *</code> - 每天早上7点</li>
        <li><code>30 20 * * 1-5</code> - 周一到周五晚上8点30分</li>
        <li><code>0 */2 * * *</code> - 每2小时</li>
        <li><code>0 12 * * 0</code> - 每周日中午12点</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const reminderMessage = ref('')
const reminderMinutes = ref(10)

const musicSongName = ref('')
const musicArtist = ref('')
const musicCron = ref('0 7 * * *')

const playlistId = ref('')
const playlistCron = ref('0 7 * * *')
const playlists = ref<Array<{id: string, name: string}>>([])

async function createQuickReminder() {
  if (!reminderMessage.value) {
    alert('请输入提醒内容')
    return
  }

  try {
    await api.post('/api/scheduler/quick/reminder', {
      message: reminderMessage.value,
      delay_minutes: reminderMinutes.value
    })
    alert('提醒创建成功')
    reminderMessage.value = ''
    reminderMinutes.value = 10
  } catch (error) {
    console.error('创建提醒失败:', error)
    alert('创建提醒失败')
  }
}

async function createQuickPlayMusic() {
  if (!musicSongName.value || !musicCron.value) {
    alert('请填写歌曲名称和Cron表达式')
    return
  }

  try {
    await api.post('/api/scheduler/quick/play-music', {
      song_name: musicSongName.value,
      artist: musicArtist.value || undefined,
      cron_expression: musicCron.value
    })
    alert('任务创建成功')
    musicSongName.value = ''
    musicArtist.value = ''
  } catch (error) {
    console.error('创建任务失败:', error)
    alert('创建任务失败')
  }
}

async function createQuickPlayPlaylist() {
  if (!playlistId.value || !playlistCron.value) {
    alert('请选择播放列表和Cron表达式')
    return
  }

  try {
    await api.post('/api/scheduler/quick/play-playlist', {
      playlist_id: playlistId.value,
      cron_expression: playlistCron.value
    })
    alert('任务创建成功')
    playlistId.value = ''
  } catch (error) {
    console.error('创建任务失败:', error)
    alert('创建任务失败')
  }
}

async function loadPlaylists() {
  try {
    const response = await api.get('/api/playlists')
    playlists.value = response.data
  } catch (error) {
    console.error('加载播放列表失败:', error)
  }
}

onMounted(() => {
  loadPlaylists()
})
</script>

<style scoped>
.quick-actions {
  margin-top: 32px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.action-card {
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-card h4 {
  margin-bottom: 12px;
}

.input {
  width: 100%;
  padding: 8px 12px;
  margin-bottom: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary {
  width: 100%;
  padding: 10px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-primary:hover {
  background: #1565c0;
}

.cron-help {
  margin-top: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.cron-help ul {
  list-style: none;
  padding: 0;
  margin-top: 12px;
}

.cron-help li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.cron-help li:last-child {
  border-bottom: none;
}

.cron-help code {
  padding: 2px 6px;
  background: #f5f5f5;
  border-radius: 3px;
  font-family: monospace;
  color: #d32f2f;
}
</style>
```

## 3. API 客户端封装

```typescript
// api/scheduler.ts
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export interface Task {
  task_id: string
  task_type: 'play_music' | 'play_playlist' | 'reminder'
  name: string
  trigger_type: 'cron' | 'date'
  cron_expression?: string
  run_date?: string
  params: Record<string, any>
  enabled: boolean
  next_run_time?: string
  created_at: string
  updated_at: string
}

export const schedulerApi = {
  // 列出所有任务
  listTasks: (taskType?: string) => {
    const params = taskType ? { task_type: taskType } : {}
    return axios.get<Task[]>(`${API_BASE}/scheduler/tasks`, { params })
  },

  // 获取任务详情
  getTask: (taskId: string) => {
    return axios.get<Task>(`${API_BASE}/scheduler/tasks/${taskId}`)
  },

  // 创建 Cron 任务
  createCronTask: (data: {
    task_type: string
    name: string
    cron_expression: string
    params: Record<string, any>
    enabled?: boolean
  }) => {
    return axios.post<Task>(`${API_BASE}/scheduler/tasks/cron`, data)
  },

  // 创建一次性任务
  createDateTask: (data: {
    task_type: string
    name: string
    run_date: string
    params: Record<string, any>
    enabled?: boolean
  }) => {
    return axios.post<Task>(`${API_BASE}/scheduler/tasks/date`, data)
  },

  // 创建延迟任务
  createDelayTask: (data: {
    task_type: string
    name: string
    delay_minutes: number
    params: Record<string, any>
  }) => {
    return axios.post<Task>(`${API_BASE}/scheduler/tasks/delay`, data)
  },

  // 更新任务
  updateTask: (taskId: string, data: Partial<{
    name: string
    cron_expression: string
    run_date: string
    params: Record<string, any>
    enabled: boolean
  }>) => {
    return axios.put<Task>(`${API_BASE}/scheduler/tasks/${taskId}`, data)
  },

  // 删除任务
  deleteTask: (taskId: string) => {
    return axios.delete(`${API_BASE}/scheduler/tasks/${taskId}`)
  },

  // 快速创建提醒
  quickReminder: (message: string, delayMinutes: number) => {
    return axios.post<Task>(`${API_BASE}/scheduler/quick/reminder`, {
      message,
      delay_minutes: delayMinutes
    })
  },

  // 快速播放音乐
  quickPlayMusic: (songName: string, artist: string | undefined, cronExpression: string) => {
    return axios.post<Task>(`${API_BASE}/scheduler/quick/play-music`, {
      song_name: songName,
      artist,
      cron_expression: cronExpression
    })
  },

  // 快速播放播放列表
  quickPlayPlaylist: (playlistId: string, cronExpression: string) => {
    return axios.post<Task>(`${API_BASE}/scheduler/quick/play-playlist`, {
      playlist_id: playlistId,
      cron_expression: cronExpression
    })
  }
}
```

## 4. 路由配置

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ... 其他路由
  {
    path: '/scheduler',
    name: 'Scheduler',
    component: () => import('@/views/Scheduler.vue'),
    meta: { title: '定时任务' }
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
```

## 5. 菜单配置

在侧边栏菜单中添加定时任务入口：

```vue
<template>
  <nav class="sidebar">
    <!-- ... 其他菜单项 -->
    <router-link to="/scheduler" class="menu-item">
      <i class="icon-clock"></i>
      <span>定时任务</span>
    </router-link>
  </nav>
</template>
```

## 测试建议

1. 创建各种类型的任务并验证执行
2. 测试启用/禁用功能
3. 测试编辑和删除功能
4. 验证任务持久化（重启应用后任务是否恢复）
5. 测试快捷操作的便捷性
6. 验证 Cron 表达式的正确性

## 用户体验优化建议

1. 添加 Cron 表达式可视化编辑器
2. 提供常用时间模板（每天早上、每周一等）
3. 任务执行历史记录
4. 任务执行失败通知
5. 批量操作（批量启用/禁用/删除）
6. 任务分组管理
7. 导入/导出任务配置
