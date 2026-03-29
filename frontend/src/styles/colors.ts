/**
 * 颜色定义文件
 * 统一管理应用中使用的所有颜色值，支持深色模式
 */

export interface ColorTheme {
    // 主色调
    primary: string
    primaryLight: string
    primaryDark: string
    success: string
    warning: string
    danger: string
    info: string

    // 文本颜色
    textPrimary: string
    textRegular: string
    textSecondary: string
    textPlaceholder: string
    textDisabled: string
    textWhite: string

    // 背景颜色
    bgPrimary: string
    bgSecondary: string
    bgTertiary: string
    bgElevated: string
    bgOverlay: string

    // 边框颜色
    borderBase: string
    borderLight: string
    borderDark: string

    // 侧边栏颜色
    sidebarBg: string
    sidebarBorder: string
    sidebarText: string
    sidebarHover: string
    sidebarActive: string

    // 卡片颜色
    cardBg: string
    cardBorder: string
    cardShadow: string

    // 按钮颜色
    buttonBg: string
    buttonHoverBg: string
    buttonDisabledBg: string
    buttonDisabledText: string

    // 输入框颜色
    inputBg: string
    inputBorder: string
    inputFocusBorder: string

    // 表格颜色
    tableHeaderBg: string
    tableRowHoverBg: string
    tableRowActiveBg: string

    // 滚动条颜色
    scrollbarThumb: string
    scrollbarThumbHover: string
    scrollbarTrack: string

    // 渐变色
    gradientStart: string
    gradientEnd: string

    // 图标颜色
    iconPrimary: string
    iconSecondary: string
    iconSuccess: string
    iconWarning: string
    iconDanger: string

    // 代码/标签颜色
    codeBg: string
    codeText: string
    tagBg: string

    // 播放器颜色
    playerBg: string
    playerControlBg: string
    playerControlHoverBg: string
    playerProgressBg: string
    playerProgressBar: string

    // 图表颜色
    chartItemBg: string
    chartItemBorder: string
    chartItemHoverBorder: string
    chartImageErrorBg: string
    chartImageErrorText: string

    // 阴影
    shadowSm: string
    shadowMd: string
    shadowLg: string
}

// 浅色主题
export const lightTheme: ColorTheme = {
    // 主色调
    primary: '#409eff',
    primaryLight: '#66b1ff',
    primaryDark: '#3a8ee6',
    success: '#67c23a',
    warning: '#e6a23c',
    danger: '#f56c6c',
    info: '#909399',

    // 文本颜色
    textPrimary: '#303133',
    textRegular: '#606266',
    textSecondary: '#909399',
    textPlaceholder: '#c0c4cc',
    textDisabled: '#c0c4cc',
    textWhite: '#ffffff',

    // 背景颜色
    bgPrimary: '#ffffff',
    bgSecondary: '#f5f7fa',
    bgTertiary: '#f0f2f5',
    bgElevated: '#ffffff',
    bgOverlay: 'rgba(0, 0, 0, 0.5)',

    // 边框颜色
    borderBase: '#dcdfe6',
    borderLight: '#e4e7ed',
    borderDark: '#c0c4cc',

    // 侧边栏颜色
    sidebarBg: '#1d2d44',
    sidebarBorder: '#2e4060',
    sidebarText: '#c0cfe0',
    sidebarHover: '#2e4060',
    sidebarActive: '#ffffff',

    // 卡片颜色
    cardBg: '#ffffff',
    cardBorder: '#e4e7ed',
    cardShadow: 'rgba(0, 0, 0, 0.04)',

    // 按钮颜色
    buttonBg: '#f5f7fa',
    buttonHoverBg: '#e4e7ed',
    buttonDisabledBg: '#f5f7fa',
    buttonDisabledText: '#c0c4cc',

    // 输入框颜色
    inputBg: '#ffffff',
    inputBorder: '#dcdfe6',
    inputFocusBorder: '#409eff',

    // 表格颜色
    tableHeaderBg: '#f5f7fa',
    tableRowHoverBg: '#f5f7fa',
    tableRowActiveBg: '#ecf5ff',

    // 滚动条颜色
    scrollbarThumb: '#dcdfe6',
    scrollbarThumbHover: '#c0c4cc',
    scrollbarTrack: 'transparent',

    // 渐变色
    gradientStart: '#667eea',
    gradientEnd: '#764ba2',

    // 图标颜色
    iconPrimary: '#409eff',
    iconSecondary: '#909399',
    iconSuccess: '#67c23a',
    iconWarning: '#e6a23c',
    iconDanger: '#f56c6c',

    // 代码/标签颜色
    codeBg: '#f5f7fa',
    codeText: '#e6a23c',
    tagBg: '#f0f2f5',

    // 播放器颜色
    playerBg: '#ffffff',
    playerControlBg: '#f5f7fa',
    playerControlHoverBg: '#e4e7ed',
    playerProgressBg: '#e4e7ed',
    playerProgressBar: '#409eff',

    // 图表颜色
    chartItemBg: '#ffffff',
    chartItemBorder: '#e4e7ed',
    chartItemHoverBorder: '#409eff',
    chartImageErrorBg: '#f5f7fa',
    chartImageErrorText: '#c0c4cc',

    // 阴影
    shadowSm: '0 2px 4px rgba(0, 0, 0, 0.04)',
    shadowMd: '0 2px 8px rgba(0, 0, 0, 0.1)',
    shadowLg: '0 4px 12px rgba(0, 0, 0, 0.15)',
}

// 深色主题
export const darkTheme: ColorTheme = {
    // 主色调
    primary: '#409eff',
    primaryLight: '#66b1ff',
    primaryDark: '#3a8ee6',
    success: '#67c23a',
    warning: '#e6a23c',
    danger: '#f56c6c',
    info: '#909399',

    // 文本颜色
    textPrimary: '#e5e7eb',
    textRegular: '#d1d5db',
    textSecondary: '#9ca3af',
    textPlaceholder: '#6b7280',
    textDisabled: '#4b5563',
    textWhite: '#ffffff',

    // 背景颜色
    bgPrimary: '#1f2937',
    bgSecondary: '#111827',
    bgTertiary: '#0f172a',
    bgElevated: '#374151',
    bgOverlay: 'rgba(0, 0, 0, 0.7)',

    // 边框颜色
    borderBase: '#374151',
    borderLight: '#4b5563',
    borderDark: '#1f2937',

    // 侧边栏颜色
    sidebarBg: '#0f172a',
    sidebarBorder: '#1e293b',
    sidebarText: '#94a3b8',
    sidebarHover: '#1e293b',
    sidebarActive: '#ffffff',

    // 卡片颜色
    cardBg: '#1f2937',
    cardBorder: '#374151',
    cardShadow: 'rgba(0, 0, 0, 0.3)',

    // 按钮颜色
    buttonBg: '#374151',
    buttonHoverBg: '#4b5563',
    buttonDisabledBg: '#1f2937',
    buttonDisabledText: '#6b7280',

    // 输入框颜色
    inputBg: '#374151',
    inputBorder: '#4b5563',
    inputFocusBorder: '#409eff',

    // 表格颜色
    tableHeaderBg: '#374151',
    tableRowHoverBg: '#374151',
    tableRowActiveBg: '#1e3a5f',

    // 滚动条颜色
    scrollbarThumb: '#4b5563',
    scrollbarThumbHover: '#6b7280',
    scrollbarTrack: 'transparent',

    // 渐变色
    gradientStart: '#4c1d95',
    gradientEnd: '#5b21b6',

    // 图标颜色
    iconPrimary: '#60a5fa',
    iconSecondary: '#9ca3af',
    iconSuccess: '#67c23a',
    iconWarning: '#e6a23c',
    iconDanger: '#f56c6c',

    // 代码/标签颜色
    codeBg: '#374151',
    codeText: '#fbbf24',
    tagBg: '#374151',

    // 播放器颜色
    playerBg: '#1f2937',
    playerControlBg: '#374151',
    playerControlHoverBg: '#4b5563',
    playerProgressBg: '#4b5563',
    playerProgressBar: '#60a5fa',

    // 图表颜色
    chartItemBg: '#1f2937',
    chartItemBorder: '#374151',
    chartItemHoverBorder: '#60a5fa',
    chartImageErrorBg: '#374151',
    chartImageErrorText: '#6b7280',

    // 阴影
    shadowSm: '0 2px 4px rgba(0, 0, 0, 0.3)',
    shadowMd: '0 2px 8px rgba(0, 0, 0, 0.4)',
    shadowLg: '0 4px 12px rgba(0, 0, 0, 0.5)',
}

// 导出当前主题（默认浅色）
export let currentTheme: ColorTheme = lightTheme

// 切换主题
export function setTheme(isDark: boolean) {
    currentTheme = isDark ? darkTheme : lightTheme
    applyTheme()
}

// 应用主题到 CSS 变量
export function applyTheme() {
    const root = document.documentElement

    Object.entries(currentTheme).forEach(([key, value]) => {
        // 将驼峰命名转换为 kebab-case
        const cssVarName = `--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`
        root.style.setProperty(cssVarName, value)
    })
}

// 初始化主题
export function initTheme() {
    // 检查用户偏好或本地存储
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const savedTheme = localStorage.getItem('theme')

    const isDark = savedTheme ? savedTheme === 'dark' : prefersDark
    setTheme(isDark)

    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches)
        }
    })
}

// 切换主题并保存偏好
export function toggleTheme() {
    const isDark = currentTheme === darkTheme
    setTheme(!isDark)
    localStorage.setItem('theme', isDark ? 'light' : 'dark')
}

// 获取当前主题模式
export function isDarkMode(): boolean {
    return currentTheme === darkTheme
}
