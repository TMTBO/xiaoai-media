import { ref, computed } from 'vue'

// 响应式的用户状态
const userRole = ref<string | null>(localStorage.getItem('role'))
const username = ref<string | null>(localStorage.getItem('username'))
const token = ref<string | null>(localStorage.getItem('token'))

export function useAuth(): {
    isAuthenticated: ReturnType<typeof computed<boolean>>
    isAdmin: ReturnType<typeof computed<boolean>>
    username: typeof username
    role: typeof userRole
    setAuth: (authToken: string, authUsername: string, authRole: string) => void
    clearAuth: () => void
    getToken: () => string | null
    getUsername: () => string | null
    getRole: () => string | null
} {
    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => userRole.value === 'admin')

    const setAuth = (authToken: string, authUsername: string, authRole: string): void => {
        token.value = authToken
        username.value = authUsername
        userRole.value = authRole

        localStorage.setItem('token', authToken)
        localStorage.setItem('username', authUsername)
        localStorage.setItem('role', authRole)
    }

    const clearAuth = (): void => {
        token.value = null
        username.value = null
        userRole.value = null

        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('role')
    }

    const getToken = (): string | null => token.value
    const getUsername = (): string | null => username.value
    const getRole = (): string | null => userRole.value

    return {
        isAuthenticated,
        isAdmin,
        username,
        role: userRole,
        setAuth,
        clearAuth,
        getToken,
        getUsername,
        getRole
    }
}

// 导出非响应式的检查函数，供路由守卫等非组件上下文使用
export function isAuthenticated(): boolean {
    return !!token.value
}

export function isAdmin(): boolean {
    return userRole.value === 'admin'
}
