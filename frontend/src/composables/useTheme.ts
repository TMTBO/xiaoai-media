import { ref, watch } from 'vue'

const THEME_KEY = 'app-theme'
type ThemeMode = 'light' | 'dark' | 'auto'

const themeMode = ref<ThemeMode>('auto')
const isDark = ref(false)

// 获取系统主题偏好
function getSystemTheme(): boolean {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
}

// 初始化主题
function initTheme(): void {
    // 从本地存储读取主题偏好
    const savedTheme = localStorage.getItem(THEME_KEY) as ThemeMode | null

    if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
        themeMode.value = savedTheme
    } else {
        themeMode.value = 'auto'
    }

    updateTheme()

    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        // 只有在自动模式下才跟随系统
        if (themeMode.value === 'auto') {
            updateTheme()
        }
    })
}

// 更新主题状态
function updateTheme(): void {
    if (themeMode.value === 'auto') {
        isDark.value = getSystemTheme()
    } else {
        isDark.value = themeMode.value === 'dark'
    }
    applyTheme()
}

// 应用主题
function applyTheme(): void {
    if (isDark.value) {
        document.documentElement.setAttribute('data-theme', 'dark')
        document.documentElement.classList.add('dark')
    } else {
        document.documentElement.setAttribute('data-theme', 'light')
        document.documentElement.classList.remove('dark')
    }
}

// 切换主题（循环切换：浅色 -> 深色 -> 跟随系统）
function toggleTheme(): void {
    if (themeMode.value === 'light') {
        themeMode.value = 'dark'
    } else if (themeMode.value === 'dark') {
        themeMode.value = 'auto'
    } else {
        themeMode.value = 'light'
    }
    localStorage.setItem(THEME_KEY, themeMode.value)
    updateTheme()
}

// 设置主题模式
function setThemeMode(mode: ThemeMode): void {
    themeMode.value = mode
    localStorage.setItem(THEME_KEY, mode)
    updateTheme()
}

// 监听主题变化
watch(isDark, () => {
    applyTheme()
})

export function useTheme(): {
    isDark: typeof isDark
    themeMode: typeof themeMode
    toggleTheme: typeof toggleTheme
    setThemeMode: typeof setThemeMode
    initTheme: typeof initTheme
} {
    return {
        isDark,
        themeMode,
        toggleTheme,
        setThemeMode,
        initTheme,
    }
}
