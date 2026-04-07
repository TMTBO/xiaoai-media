import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

// 请求拦截器 - 添加 token
http.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器 - 处理 401 错误
http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // 清除 token 并跳转到登录页
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            localStorage.removeItem('role')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export type TaskType = 'play_music' | 'play_playlist' | 'reminder' | 'command'
export type TriggerType = 'cron' | 'date'

export interface Task {
    task_id: string
    task_type: TaskType
    name: string
    trigger_type: TriggerType
    cron_expression?: string
    run_date?: string
    params: Record<string, unknown>
    enabled: boolean
    next_run_time?: string
    created_at: string
    updated_at: string
}

export interface CreateCronTaskRequest {
    task_type: TaskType
    name: string
    cron_expression: string
    params?: Record<string, unknown>
    enabled?: boolean
}

export interface CreateDateTaskRequest {
    task_type: TaskType
    name: string
    run_date: string
    params?: Record<string, unknown>
    enabled?: boolean
}

export interface CreateDelayTaskRequest {
    task_type: TaskType
    name: string
    delay_minutes: number
    params?: Record<string, unknown>
}

export interface UpdateTaskRequest {
    name?: string
    cron_expression?: string
    run_date?: string
    params?: Record<string, unknown>
    enabled?: boolean
}

export interface QuickReminderRequest {
    message: string
    delay_minutes: number
}

export interface QuickPlayMusicRequest {
    song_name: string
    artist?: string
    cron_expression: string
}

export interface QuickPlayPlaylistRequest {
    playlist_id: string
    cron_expression: string
}

export interface QuickCommandRequest {
    command: string
    cron_expression?: string
    delay_minutes?: number
    device_id?: string
}

export const schedulerApi = {
    // 列出所有任务
    listTasks: (taskType?: TaskType) => {
        const params = taskType ? { task_type: taskType } : {}
        return http.get<Task[]>('/scheduler/tasks', { params }).then(r => r.data)
    },

    // 获取任务详情
    getTask: (taskId: string) => {
        return http.get<Task>(`/scheduler/tasks/${taskId}`).then(r => r.data)
    },

    // 创建 Cron 任务
    createCronTask: (data: CreateCronTaskRequest) => {
        return http.post<Task>('/scheduler/tasks/cron', data).then(r => r.data)
    },

    // 创建一次性任务
    createDateTask: (data: CreateDateTaskRequest) => {
        return http.post<Task>('/scheduler/tasks/date', data).then(r => r.data)
    },

    // 创建延迟任务
    createDelayTask: (data: CreateDelayTaskRequest) => {
        return http.post<Task>('/scheduler/tasks/delay', data).then(r => r.data)
    },

    // 更新任务
    updateTask: (taskId: string, data: UpdateTaskRequest) => {
        return http.put<Task>(`/scheduler/tasks/${taskId}`, data).then(r => r.data)
    },

    // 删除任务
    deleteTask: (taskId: string) => {
        return http.delete(`/scheduler/tasks/${taskId}`).then(r => r.data)
    },

    // 快速创建提醒
    quickReminder: (data: QuickReminderRequest) => {
        return http.post<Task>('/scheduler/quick/reminder', data).then(r => r.data)
    },

    // 快速播放音乐
    quickPlayMusic: (data: QuickPlayMusicRequest) => {
        return http.post<Task>('/scheduler/quick/play-music', data).then(r => r.data)
    },

    // 快速播放播放列表
    quickPlayPlaylist: (data: QuickPlayPlaylistRequest) => {
        return http.post<Task>('/scheduler/quick/play-playlist', data).then(r => r.data)
    },

    // 快速执行指令
    quickCommand: (data: QuickCommandRequest) => {
        return http.post<Task>('/scheduler/quick/command', data).then(r => r.data)
    },
}
