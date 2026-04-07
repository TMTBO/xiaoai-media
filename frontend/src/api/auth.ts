import axios from 'axios'

const API_BASE = '/api'

// 创建axios实例
const api = axios.create({
    baseURL: API_BASE
})

// 标记是否正在跳转登录页
let isRedirecting = false

// 请求拦截器 - 添加token
api.interceptors.request.use(
    (config) => {
        // 如果正在跳转登录页，取消所有新请求
        if (isRedirecting) {
            return Promise.reject(new axios.Cancel('正在跳转登录页，取消请求'))
        }

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

// 响应拦截器 - 处理401错误
api.interceptors.response.use(
    (response) => {
        // 成功响应时重置跳转标志
        isRedirecting = false
        return response
    },
    (error) => {
        // 如果是取消的请求，直接返回
        if (axios.isCancel(error)) {
            return Promise.reject(error)
        }

        if (error.response?.status === 401) {
            // 避免重复跳转
            if (!isRedirecting) {
                isRedirecting = true

                // 清除token和用户信息
                localStorage.removeItem('token')
                localStorage.removeItem('username')
                localStorage.removeItem('role')

                // 跳转到登录页
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export interface LoginResponse {
    token: string
    username: string
    role: string
}

export interface UserInfo {
    username: string
    role: string
    created_at: string
    last_login?: string
    enabled: boolean
}

export interface UpdateUserRequest {
    new_username?: string
    password?: string
    role?: string
    enabled?: boolean
}

export async function login(username: string, password: string): Promise<LoginResponse> {
    // 登录时重置跳转标志，确保可以正常发送请求
    isRedirecting = false
    const response = await api.post('/auth/login', { username, password })
    return response.data
}

export async function getCurrentUser(): Promise<UserInfo> {
    const response = await api.get('/auth/me')
    return response.data
}

export async function listUsers(): Promise<UserInfo[]> {
    const response = await api.get('/users')
    return response.data
}

export async function createUser(username: string, password: string, role: string): Promise<UserInfo> {
    const response = await api.post('/users', { username, password, role })
    return response.data
}

export async function updateUser(username: string, data: UpdateUserRequest): Promise<UserInfo> {
    const response = await api.put(`/users/${username}`, data)
    return response.data
}

export async function deleteUser(username: string): Promise<void> {
    await api.delete(`/users/${username}`)
}

export function isAuthenticated(): boolean {
    return !!localStorage.getItem('token')
}

export function isAdmin(): boolean {
    return localStorage.getItem('role') === 'admin'
}

export function logout(): void {
    // 重置跳转标志，确保登录页面可以正常发送请求
    isRedirecting = false
    // 注意：这里仍然直接操作 localStorage，因为 logout 后会跳转到登录页
    // useAuth 的状态会在页面重新加载时重置
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    window.location.href = '/login'
}

export async function enableUser(username: string): Promise<UserInfo> {
    const response = await api.post(`/users/${username}/enable`)
    return response.data
}

export async function disableUser(username: string): Promise<UserInfo> {
    const response = await api.post(`/users/${username}/disable`)
    return response.data
}
