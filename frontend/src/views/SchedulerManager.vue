<template>
  <div class="scheduler-manager">
    <el-card class="header-card">
      <div class="header">
        <h2>定时任务管理</h2>
        <div class="header-actions">
          <el-select
            v-model="filterType"
            placeholder="任务类型"
            clearable
            style="width: 180px; margin-right: 12px;"
            @change="loadTasks"
          >
            <el-option
              label="全部任务"
              value=""
            />
            <el-option
              label="播放音乐"
              value="play_music"
            />
            <el-option
              label="播放播放列表"
              value="play_playlist"
            />
            <el-option
              label="提醒"
              value="reminder"
            />
            <el-option
              label="执行指令"
              value="command"
            />
          </el-select>
          <el-button
            type="primary"
            @click="openCreateDialog"
          >
            <el-icon style="margin-right: 6px;">
              <Plus />
            </el-icon>
            创建任务
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 任务列表 -->
    <el-card
      v-loading="loading"
      class="task-list-card"
    >
      <div
        v-if="tasks.length === 0"
        class="empty-state"
      >
        <el-empty description="暂无任务" />
      </div>
      
      <div
        v-else
        class="task-list"
      >
        <el-card
          v-for="task in tasks"
          :key="task.task_id"
          class="task-item"
          shadow="hover"
        >
          <div class="task-content">
            <div class="task-info">
              <div class="task-header">
                <h3>{{ task.name }}</h3>
                <el-tag
                  :type="getTaskTypeColor(task.task_type)"
                  size="small"
                >
                  {{ getTaskTypeLabel(task.task_type) }}
                </el-tag>
              </div>
              
              <div class="task-details">
                <div class="detail-item">
                  <el-icon><Clock /></el-icon>
                  <span class="label">触发方式：</span>
                  <span class="value">
                    {{ task.trigger_type === 'cron' ? task.cron_expression : '一次性' }}
                  </span>
                </div>
                
                <div
                  v-if="task.next_run_time"
                  class="detail-item"
                >
                  <el-icon><Timer /></el-icon>
                  <span class="label">下次执行：</span>
                  <span class="value">{{ formatDateTime(task.next_run_time) }}</span>
                </div>
                
                <div class="detail-item">
                  <el-icon><Document /></el-icon>
                  <span class="label">参数：</span>
                  <span class="value">{{ formatParams(task.params) }}</span>
                </div>
              </div>
            </div>

            <div class="task-actions">
              <el-switch
                v-model="task.enabled"
                active-text="启用"
                inactive-text="禁用"
                @change="toggleTask(task)"
              />
              
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="editTask(task)"
              >
                编辑
              </el-button>
              
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="deleteTask(task)"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 快捷操作面板 -->
    <el-card class="quick-actions-card">
      <template #header>
        <div class="card-header">
          <span>快捷操作</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <!-- 快速提醒 -->
        <el-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <el-card
            shadow="hover"
            class="action-card"
          >
            <template #header>
              <div class="action-header">
                <el-icon size="20">
                  <Bell />
                </el-icon>
                <span>快速提醒</span>
              </div>
            </template>
            
            <el-form
              :model="quickReminder"
              label-position="top"
            >
              <el-form-item label="提醒内容">
                <el-input
                  v-model="quickReminder.message"
                  placeholder="输入提醒内容"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
              
              <el-form-item label="延迟分钟数">
                <el-input-number
                  v-model="quickReminder.delay_minutes"
                  :min="1"
                  :max="1440"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
              
              <el-form-item label="设备（可选）">
                <el-select
                  v-model="quickReminder.device_id"
                  placeholder="默认设备"
                  style="width: 100%"
                  clearable
                  filterable
                >
                  <el-option
                    v-for="device in devices"
                    :key="device.deviceID"
                    :label="device.name"
                    :value="device.deviceID"
                  />
                </el-select>
              </el-form-item>
              
              <el-button
                type="primary"
                style="width: 100%"
                :loading="quickReminder.loading"
                @click="createQuickReminder"
              >
                创建提醒
              </el-button>
            </el-form>
          </el-card>
        </el-col>

        <!-- 快速播放音乐 -->
        <el-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <el-card
            shadow="hover"
            class="action-card"
          >
            <template #header>
              <div class="action-header">
                <el-icon size="20">
                  <Headset />
                </el-icon>
                <span>定时播放音乐</span>
              </div>
            </template>
            
            <el-form
              :model="quickMusic"
              label-position="top"
            >
              <el-form-item label="歌曲名称">
                <el-input
                  v-model="quickMusic.song_name"
                  placeholder="输入歌曲名称"
                />
              </el-form-item>
              
              <el-form-item label="歌手（可选）">
                <el-input
                  v-model="quickMusic.artist"
                  placeholder="输入歌手名称"
                />
              </el-form-item>
              
              <el-form-item label="Cron 表达式">
                <el-input
                  v-model="quickMusic.cron_expression"
                  placeholder="如: 0 7 * * *"
                />
              </el-form-item>
              
              <el-form-item label="设备（可选）">
                <el-select
                  v-model="quickMusic.device_id"
                  placeholder="默认设备"
                  style="width: 100%"
                  clearable
                  filterable
                >
                  <el-option
                    v-for="device in devices"
                    :key="device.deviceID"
                    :label="device.name"
                    :value="device.deviceID"
                  />
                </el-select>
              </el-form-item>
              
              <el-button
                type="primary"
                style="width: 100%"
                :loading="quickMusic.loading"
                @click="createQuickPlayMusic"
              >
                创建任务
              </el-button>
            </el-form>
          </el-card>
        </el-col>

        <!-- 快速播放播放列表 -->
        <el-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <el-card
            shadow="hover"
            class="action-card"
          >
            <template #header>
              <div class="action-header">
                <el-icon size="20">
                  <List />
                </el-icon>
                <span>定时播放播放列表</span>
              </div>
            </template>
            
            <el-form
              :model="quickPlaylist"
              label-position="top"
            >
              <el-form-item label="播放列表">
                <el-select
                  v-model="quickPlaylist.playlist_id"
                  placeholder="选择播放列表"
                  style="width: 100%"
                  filterable
                >
                  <el-option
                    v-for="pl in playlists"
                    :key="pl.id"
                    :label="pl.name"
                    :value="pl.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="Cron 表达式">
                <el-input
                  v-model="quickPlaylist.cron_expression"
                  placeholder="如: 0 7 * * *"
                />
              </el-form-item>
              
              <el-form-item label="设备（可选）">
                <el-select
                  v-model="quickPlaylist.device_id"
                  placeholder="默认设备"
                  style="width: 100%"
                  clearable
                  filterable
                >
                  <el-option
                    v-for="device in devices"
                    :key="device.deviceID"
                    :label="device.name"
                    :value="device.deviceID"
                  />
                </el-select>
              </el-form-item>
              
              <el-button
                type="primary"
                style="width: 100%"
                :loading="quickPlaylist.loading"
                @click="createQuickPlayPlaylist"
              >
                创建任务
              </el-button>
            </el-form>
          </el-card>
        </el-col>

        <!-- 快速执行指令 -->
        <el-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <el-card
            shadow="hover"
            class="action-card"
          >
            <template #header>
              <div class="action-header">
                <el-icon size="20">
                  <ChatDotRound />
                </el-icon>
                <span>定时/延迟执行指令</span>
              </div>
            </template>
            
            <el-form
              :model="quickCommand"
              label-position="top"
            >
              <el-form-item label="语音指令">
                <el-input
                  v-model="quickCommand.command"
                  placeholder="如: 播放周杰伦的歌"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
              
              <el-form-item label="执行方式">
                <el-radio-group v-model="quickCommand.mode">
                  <el-radio value="cron">
                    定时执行
                  </el-radio>
                  <el-radio value="delay">
                    延迟执行
                  </el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item 
                v-if="quickCommand.mode === 'cron'" 
                label="Cron 表达式"
              >
                <el-input
                  v-model="quickCommand.cron_expression"
                  placeholder="如: 0 7 * * *"
                />
              </el-form-item>
              
              <el-form-item 
                v-if="quickCommand.mode === 'delay'" 
                label="延迟分钟数"
              >
                <el-input-number
                  v-model="quickCommand.delay_minutes"
                  :min="1"
                  :max="1440"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
              
              <el-form-item label="设备（可选）">
                <el-select
                  v-model="quickCommand.device_id"
                  placeholder="默认设备"
                  style="width: 100%"
                  clearable
                  filterable
                >
                  <el-option
                    v-for="device in devices"
                    :key="device.deviceID"
                    :label="device.name"
                    :value="device.deviceID"
                  />
                </el-select>
              </el-form-item>
              
              <el-button
                type="primary"
                style="width: 100%"
                :loading="quickCommand.loading"
                @click="createQuickCommand"
              >
                创建任务
              </el-button>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- Cron 表达式帮助 -->
      <el-alert
        title="Cron 表达式示例"
        type="info"
        :closable="false"
        style="margin-top: 20px"
      >
        <ul class="cron-help">
          <li><code>0 7 * * *</code> - 每天早上7点</li>
          <li><code>30 20 * * 1-5</code> - 周一到周五晚上8点30分</li>
          <li><code>0 */2 * * *</code> - 每2小时</li>
          <li><code>0 12 * * 0</code> - 每周日中午12点</li>
        </ul>
        <div :style="{ marginTop: '10px', color: 'var(--color-text-secondary)', fontSize: '13px' }">
          💡 提示：执行指令功能支持所有语音命令，如播放音乐、播放列表、搜索、控制等
        </div>
      </el-alert>
    </el-card>

    <!-- 创建/编辑任务对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTask ? '编辑任务' : '创建任务'"
      width="600px"
      @close="resetTaskForm"
    >
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskFormRules"
        label-width="120px"
      >
        <el-form-item
          label="任务类型"
          prop="task_type"
        >
          <el-select
            v-model="taskForm.task_type"
            placeholder="选择任务类型"
            style="width: 100%"
            :disabled="!!editingTask"
          >
            <el-option
              label="播放音乐"
              value="play_music"
            />
            <el-option
              label="播放播放列表"
              value="play_playlist"
            />
            <el-option
              label="提醒"
              value="reminder"
            />
            <el-option
              label="执行指令"
              value="command"
            />
          </el-select>
        </el-form-item>

        <el-form-item
          label="任务名称"
          prop="name"
        >
          <el-input
            v-model="taskForm.name"
            placeholder="输入任务名称"
          />
        </el-form-item>

        <el-form-item
          label="触发方式"
          prop="trigger_type"
        >
          <el-radio-group
            v-model="taskForm.trigger_type"
            :disabled="!!editingTask"
          >
            <el-radio value="cron">
              周期性（Cron）
            </el-radio>
            <el-radio value="date">
              一次性
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="taskForm.trigger_type === 'cron'"
          label="Cron 表达式"
          prop="cron_expression"
        >
          <el-input
            v-model="taskForm.cron_expression"
            placeholder="如: 0 7 * * *"
          />
        </el-form-item>

        <el-form-item
          v-if="taskForm.trigger_type === 'date'"
          label="执行时间"
          prop="run_date"
        >
          <el-date-picker
            v-model="taskForm.run_date"
            type="datetime"
            placeholder="选择执行时间"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>

        <!-- 任务参数 -->
        <template v-if="taskForm.task_type === 'play_music'">
          <el-form-item
            label="歌曲名称"
            prop="song_name"
          >
            <el-input
              v-model="taskForm.song_name"
              placeholder="输入歌曲名称"
            />
          </el-form-item>
          <el-form-item label="歌手">
            <el-input
              v-model="taskForm.artist"
              placeholder="输入歌手名称（可选）"
            />
          </el-form-item>
        </template>

        <template v-if="taskForm.task_type === 'play_playlist'">
          <el-form-item
            label="播放列表"
            prop="playlist_id"
          >
            <el-select
              v-model="taskForm.playlist_id"
              placeholder="选择播放列表"
              style="width: 100%"
              filterable
            >
              <el-option
                v-for="pl in playlists"
                :key="pl.id"
                :label="pl.name"
                :value="pl.id"
              />
            </el-select>
          </el-form-item>
        </template>

        <template v-if="taskForm.task_type === 'reminder'">
          <el-form-item
            label="提醒内容"
            prop="message"
          >
            <el-input
              v-model="taskForm.message"
              type="textarea"
              :rows="3"
              placeholder="输入提醒内容"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </template>

        <template v-if="taskForm.task_type === 'command'">
          <el-form-item
            label="语音指令"
            prop="command"
          >
            <el-input
              v-model="taskForm.command"
              placeholder="如: 播放周杰伦的歌"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </template>

        <!-- 所有任务类型都支持设备选择 -->
        <el-form-item label="设备（可选）">
          <el-select
            v-model="taskForm.device_id"
            placeholder="不填则使用默认设备"
            style="width: 100%"
            clearable
            filterable
          >
            <el-option
              v-for="device in devices"
              :key="device.deviceID"
              :label="`${device.name} (${device.hardware})`"
              :value="device.deviceID"
            />
          </el-select>
          <template #extra>
            <span :style="{ fontSize: '12px', color: 'var(--color-text-secondary)' }">
              不选择则使用默认设备
            </span>
          </template>
        </el-form-item>

        <el-form-item label="启用">
          <el-switch v-model="taskForm.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="cancelTask">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="submitTask"
        >
          {{ editingTask ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  Clock,
  Timer,
  Document,
  Bell,
  Headset,
  List,
  ChatDotRound,
} from '@element-plus/icons-vue'
import { schedulerApi, type Task, type TaskType } from '@/api/scheduler'
import { api, type Device } from '@/api'

const loading = ref(false)
const tasks = ref<Task[]>([])
const filterType = ref<TaskType | ''>('') // 默认为空字符串表示"全部任务"
const playlists = ref<Array<{ id: string; name: string }>>([])
const devices = ref<Device[]>([])

const showCreateDialog = ref(false)
const editingTask = ref<Task | null>(null)
const submitting = ref(false)
const taskFormRef = ref<FormInstance>()

const taskForm = reactive({
  task_type: 'play_music' as TaskType,
  name: '',
  trigger_type: 'cron' as 'cron' | 'date',
  cron_expression: '0 7 * * *',
  run_date: null as Date | null,
  enabled: true,
  // 任务参数
  song_name: '',
  artist: '',
  playlist_id: '',
  message: '',
  command: '',
  device_id: '',  // 所有任务类型都支持设备选择
})

const taskFormRules: FormRules = {
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  trigger_type: [{ required: true, message: '请选择触发方式', trigger: 'change' }],
  cron_expression: [
    { required: true, message: '请输入 Cron 表达式', trigger: 'blur' },
  ],
  run_date: [{ required: true, message: '请选择执行时间', trigger: 'change' }],
  song_name: [{ required: true, message: '请输入歌曲名称', trigger: 'blur' }],
  playlist_id: [{ required: true, message: '请选择播放列表', trigger: 'change' }],
  message: [{ required: true, message: '请输入提醒内容', trigger: 'blur' }],
  command: [{ required: true, message: '请输入语音指令', trigger: 'blur' }],
}

const quickReminder = reactive({
  message: '',
  delay_minutes: 10,
  device_id: '',
  loading: false,
})

const quickMusic = reactive({
  song_name: '',
  artist: '',
  cron_expression: '0 7 * * *',
  device_id: '',
  loading: false,
})

const quickPlaylist = reactive({
  playlist_id: '',
  cron_expression: '0 7 * * *',
  device_id: '',
  loading: false,
})

const quickCommand = reactive({
  command: '',
  mode: 'cron' as 'cron' | 'delay',
  cron_expression: '0 7 * * *',
  delay_minutes: 10,
  device_id: '',
  loading: false,
})

async function loadTasks(): Promise<void> {
  loading.value = true
  try {
    tasks.value = await schedulerApi.listTasks(filterType.value || undefined)
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('加载任务失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

async function loadPlaylists(): Promise<void> {
  try {
    const data = await api.listPlaylists()
    playlists.value = data.playlists
  } catch (error: unknown) {
    // Silently fail - playlists are optional
  }
}

async function loadDevices(): Promise<void> {
  try {
    const data = await api.listDevices()
    devices.value = data.devices
  } catch (error: unknown) {
    // Silently fail - devices are optional
  }
}

async function toggleTask(task: Task): Promise<void> {
  try {
    await schedulerApi.updateTask(task.task_id, { enabled: task.enabled })
    ElMessage.success(task.enabled ? '任务已启用' : '任务已禁用')
  } catch (error: unknown) {
    task.enabled = !task.enabled // 恢复状态
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('操作失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  }
}

function editTask(task: Task): void {
  editingTask.value = task
  taskForm.task_type = task.task_type
  taskForm.name = task.name
  taskForm.trigger_type = task.trigger_type
  taskForm.cron_expression = task.cron_expression || '0 7 * * *'
  taskForm.run_date = task.run_date ? new Date(task.run_date) : null
  taskForm.enabled = task.enabled

  // 填充参数
  if (task.task_type === 'play_music') {
    taskForm.song_name = task.params.song_name || ''
    taskForm.artist = task.params.artist || ''
  } else if (task.task_type === 'play_playlist') {
    taskForm.playlist_id = task.params.playlist_id || ''
  } else if (task.task_type === 'reminder') {
    taskForm.message = task.params.message || ''
  } else if (task.task_type === 'command') {
    taskForm.command = task.params.command || ''
  }
  
  // 所有任务类型都可能有设备ID
  taskForm.device_id = task.params.device_id || ''

  showCreateDialog.value = true
}

async function deleteTask(task: Task): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务"${task.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await schedulerApi.deleteTask(task.task_id)
    ElMessage.success('任务已删除')
    await loadTasks()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { response?: { data?: { detail?: string } }; message?: string }
      ElMessage.error('删除失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
    }
  }
}

async function submitTask(): Promise<void> {
  if (!taskFormRef.value) return

  try {
    await taskFormRef.value.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    const params: Record<string, unknown> = {}

    if (taskForm.task_type === 'play_music') {
      params.song_name = taskForm.song_name
      if (taskForm.artist) params.artist = taskForm.artist
    } else if (taskForm.task_type === 'play_playlist') {
      params.playlist_id = taskForm.playlist_id
    } else if (taskForm.task_type === 'reminder') {
      params.message = taskForm.message
    } else if (taskForm.task_type === 'command') {
      params.command = taskForm.command
    }
    
    // 所有任务类型都支持设备选择
    if (taskForm.device_id) {
      params.device_id = taskForm.device_id
    }

    if (editingTask.value) {
      // 更新任务
      const updateData: Record<string, unknown> = {
        name: taskForm.name,
        params,
        enabled: taskForm.enabled,
      }

      if (taskForm.trigger_type === 'cron') {
        updateData.cron_expression = taskForm.cron_expression
      } else if (taskForm.run_date) {
        updateData.run_date = taskForm.run_date.toISOString()
      }

      await schedulerApi.updateTask(editingTask.value.task_id, updateData)
      ElMessage.success('任务已更新')
    } else {
      // 创建任务
      if (taskForm.trigger_type === 'cron') {
        await schedulerApi.createCronTask({
          task_type: taskForm.task_type,
          name: taskForm.name,
          cron_expression: taskForm.cron_expression,
          params,
          enabled: taskForm.enabled,
        })
      } else if (taskForm.run_date) {
        await schedulerApi.createDateTask({
          task_type: taskForm.task_type,
          name: taskForm.name,
          run_date: taskForm.run_date.toISOString(),
          params,
          enabled: taskForm.enabled,
        })
      }
      ElMessage.success('任务已创建')
    }

    showCreateDialog.value = false
    resetTaskForm()
    await loadTasks()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('操作失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

function resetTaskForm(): void {
  editingTask.value = null
  taskForm.task_type = 'play_music'
  taskForm.name = ''
  taskForm.trigger_type = 'cron'
  taskForm.cron_expression = '0 7 * * *'
  taskForm.run_date = null
  taskForm.enabled = true
  taskForm.song_name = ''
  taskForm.artist = ''
  taskForm.playlist_id = ''
  taskForm.message = ''
  taskForm.command = ''
  taskForm.device_id = ''
  taskFormRef.value?.clearValidate()
}

function cancelTask(): void {
  showCreateDialog.value = false
  resetTaskForm()
}

function openCreateDialog(): void {
  resetTaskForm()
  showCreateDialog.value = true
}

async function createQuickReminder(): Promise<void> {
  if (!quickReminder.message) {
    ElMessage.warning('请输入提醒内容')
    return
  }

  quickReminder.loading = true
  try {
    const data: Record<string, unknown> = {
      message: quickReminder.message,
      delay_minutes: quickReminder.delay_minutes,
    }
    if (quickReminder.device_id) {
      data.device_id = quickReminder.device_id
    }
    
    await schedulerApi.quickReminder(data)
    ElMessage.success('提醒已创建')
    quickReminder.message = ''
    quickReminder.delay_minutes = 10
    quickReminder.device_id = ''
    await loadTasks()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('创建失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    quickReminder.loading = false
  }
}

async function createQuickPlayMusic(): Promise<void> {
  if (!quickMusic.song_name || !quickMusic.cron_expression) {
    ElMessage.warning('请填写歌曲名称和 Cron 表达式')
    return
  }

  quickMusic.loading = true
  try {
    const data: Record<string, unknown> = {
      song_name: quickMusic.song_name,
      cron_expression: quickMusic.cron_expression,
    }
    if (quickMusic.artist) {
      data.artist = quickMusic.artist
    }
    if (quickMusic.device_id) {
      data.device_id = quickMusic.device_id
    }
    
    await schedulerApi.quickPlayMusic(data)
    ElMessage.success('任务已创建')
    quickMusic.song_name = ''
    quickMusic.artist = ''
    quickMusic.device_id = ''
    await loadTasks()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('创建失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    quickMusic.loading = false
  }
}

async function createQuickPlayPlaylist(): Promise<void> {
  if (!quickPlaylist.playlist_id || !quickPlaylist.cron_expression) {
    ElMessage.warning('请选择播放列表和 Cron 表达式')
    return
  }

  quickPlaylist.loading = true
  try {
    const data: Record<string, unknown> = {
      playlist_id: quickPlaylist.playlist_id,
      cron_expression: quickPlaylist.cron_expression,
    }
    if (quickPlaylist.device_id) {
      data.device_id = quickPlaylist.device_id
    }
    
    await schedulerApi.quickPlayPlaylist(data)
    ElMessage.success('任务已创建')
    quickPlaylist.playlist_id = ''
    quickPlaylist.device_id = ''
    await loadTasks()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('创建失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    quickPlaylist.loading = false
  }
}

function getTaskTypeLabel(type: TaskType): string {
  const labels: Record<TaskType, string> = {
    play_music: '播放音乐',
    play_playlist: '播放播放列表',
    reminder: '提醒',
    command: '执行指令',
  }
  return labels[type] || type
}

function getTaskTypeColor(type: TaskType): string {
  const colors: Record<TaskType, string> = {
    play_music: 'primary',
    play_playlist: 'success',
    reminder: 'warning',
    command: 'info',
  }
  return colors[type] || ''
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatParams(params: Record<string, unknown>): string {
  if (params.song_name) {
    return params.artist ? `${params.song_name} - ${params.artist}` : params.song_name
  }
  if (params.playlist_id) {
    const playlist = playlists.value.find(p => p.id === params.playlist_id)
    return playlist ? playlist.name : params.playlist_id
  }
  if (params.message) {
    return params.message
  }
  if (params.command) {
    return params.command
  }
  return JSON.stringify(params)
}

async function createQuickCommand(): Promise<void> {
  if (!quickCommand.command) {
    ElMessage.warning('请输入语音指令')
    return
  }

  if (quickCommand.mode === 'cron' && !quickCommand.cron_expression) {
    ElMessage.warning('请输入 Cron 表达式')
    return
  }

  quickCommand.loading = true
  try {
    const data: Record<string, unknown> = {
      command: quickCommand.command,
    }

    if (quickCommand.mode === 'cron') {
      data.cron_expression = quickCommand.cron_expression
    } else {
      data.delay_minutes = quickCommand.delay_minutes
    }
    
    if (quickCommand.device_id) {
      data.device_id = quickCommand.device_id
    }

    await schedulerApi.quickCommand(data)
    ElMessage.success('任务已创建')
    quickCommand.command = ''
    quickCommand.mode = 'cron'
    quickCommand.cron_expression = '0 7 * * *'
    quickCommand.delay_minutes = 10
    quickCommand.device_id = ''
    await loadTasks()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    ElMessage.error('创建失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    quickCommand.loading = false
  }
}

function disabledDate(date: Date): boolean {
  return date.getTime() < Date.now()
}

onMounted(() => {
  loadTasks()
  loadPlaylists()
  loadDevices()
})
</script>

<style scoped>
.scheduler-manager {
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
}

.task-list-card {
  margin-bottom: 20px;
}

.empty-state {
  padding: 40px 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  transition: all 0.3s;
}

.task-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.task-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.task-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-regular);
}

.detail-item .label {
  font-weight: 500;
}

.detail-item .value {
  color: var(--color-text-secondary);
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.quick-actions-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.action-card {
  height: 100%;
}

.action-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.cron-help {
  list-style: none;
  padding: 0;
  margin: 10px 0 0 0;
}

.cron-help li {
  padding: 4px 0;
}

.cron-help code {
  padding: 2px 6px;
  background: var(--color-code-bg);
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: var(--color-code-text);
  font-weight: 500;
}

@media (max-width: 768px) {
  .task-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .task-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
