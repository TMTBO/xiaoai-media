# 颜色系统使用指南

本项目已将所有颜色值抽离到统一的颜色定义文件中，并支持深色模式。

## 文件结构

- `colors.ts` - TypeScript 颜色定义文件，包含浅色和深色主题
- `theme.css` - CSS 变量定义文件，用于全局样式
- `../composables/useTheme.ts` - 主题切换 composable
- `../components/ThemeToggle.vue` - 主题切换按钮组件

## 使用方法

### 1. 在 Vue 组件中使用 CSS 变量

```vue
<style scoped>
.my-component {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}

.my-button {
  background: var(--color-primary);
  color: var(--color-text-white);
}

.my-button:hover {
  background: var(--color-primary-light);
}
</style>
```

### 2. 在 TypeScript 中使用颜色

```typescript
import { currentTheme, isDarkMode } from '@/styles/colors'

// 获取当前主题的颜色
const primaryColor = currentTheme.primary

// 检查是否为深色模式
if (isDarkMode()) {
  // 深色模式特定逻辑
}
```

### 3. 切换主题

```vue
<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme, setTheme } = useTheme()

// 切换主题
function handleToggle() {
  toggleTheme()
}

// 设置特定主题
function setDarkMode() {
  setTheme(true)
}

function setLightMode() {
  setTheme(false)
}
</script>
```

### 4. 使用主题切换组件

```vue
<template>
  <ThemeToggle />
</template>

<script setup lang="ts">
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>
```

## 可用的颜色变量

### 主色调
- `--color-primary` - 主色
- `--color-primary-light` - 主色（浅）
- `--color-primary-dark` - 主色（深）
- `--color-success` - 成功色
- `--color-warning` - 警告色
- `--color-danger` - 危险色
- `--color-info` - 信息色

### 文本颜色
- `--color-text-primary` - 主要文本
- `--color-text-regular` - 常规文本
- `--color-text-secondary` - 次要文本
- `--color-text-placeholder` - 占位符文本
- `--color-text-disabled` - 禁用文本
- `--color-text-white` - 白色文本

### 背景颜色
- `--color-bg-primary` - 主要背景
- `--color-bg-secondary` - 次要背景
- `--color-bg-tertiary` - 第三级背景
- `--color-bg-elevated` - 提升背景
- `--color-bg-overlay` - 遮罩背景

### 边框颜色
- `--color-border-base` - 基础边框
- `--color-border-light` - 浅色边框
- `--color-border-dark` - 深色边框

### 侧边栏颜色
- `--color-sidebar-bg` - 侧边栏背景
- `--color-sidebar-border` - 侧边栏边框
- `--color-sidebar-text` - 侧边栏文本
- `--color-sidebar-hover` - 侧边栏悬停
- `--color-sidebar-active` - 侧边栏激活

### 卡片颜色
- `--color-card-bg` - 卡片背景
- `--color-card-border` - 卡片边框
- `--color-card-shadow` - 卡片阴影

### 按钮颜色
- `--color-button-bg` - 按钮背景
- `--color-button-hover-bg` - 按钮悬停背景
- `--color-button-disabled-bg` - 按钮禁用背景
- `--color-button-disabled-text` - 按钮禁用文本

### 播放器颜色
- `--color-player-bg` - 播放器背景
- `--color-player-control-bg` - 播放器控制背景
- `--color-player-control-hover-bg` - 播放器控制悬停背景
- `--color-player-progress-bg` - 播放器进度条背景
- `--color-player-progress-bar` - 播放器进度条

### 图表颜色
- `--color-chart-item-bg` - 图表项背景
- `--color-chart-item-border` - 图表项边框
- `--color-chart-item-hover-border` - 图表项悬停边框
- `--color-chart-image-error-bg` - 图表图片错误背景
- `--color-chart-image-error-text` - 图表图片错误文本

### 阴影
- `--color-shadow-sm` - 小阴影
- `--color-shadow-md` - 中阴影
- `--color-shadow-lg` - 大阴影

## 深色模式

深色模式会自动应用到整个应用。主题切换时，所有使用 CSS 变量的组件都会自动更新颜色。

### 自动检测系统主题

应用会自动检测用户的系统主题偏好，并在首次加载时应用相应的主题。

### 保存用户偏好

用户手动切换主题后，偏好会保存到 localStorage，下次访问时会自动应用。

## 迁移指南

### 将硬编码颜色替换为 CSS 变量

**之前：**
```css
.my-component {
  background: #ffffff;
  color: #303133;
  border: 1px solid #e4e7ed;
}
```

**之后：**
```css
.my-component {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}
```

### 常见颜色映射

| 原颜色 | CSS 变量 | 说明 |
|--------|----------|------|
| `#ffffff` | `var(--color-bg-primary)` | 白色背景 |
| `#f5f7fa` | `var(--color-bg-secondary)` | 浅灰背景 |
| `#303133` | `var(--color-text-primary)` | 主要文本 |
| `#606266` | `var(--color-text-regular)` | 常规文本 |
| `#909399` | `var(--color-text-secondary)` | 次要文本 |
| `#c0c4cc` | `var(--color-text-placeholder)` | 占位符文本 |
| `#e4e7ed` | `var(--color-border-light)` | 浅色边框 |
| `#dcdfe6` | `var(--color-border-base)` | 基础边框 |
| `#409eff` | `var(--color-primary)` | 主色 |
| `#67c23a` | `var(--color-success)` | 成功色 |
| `#e6a23c` | `var(--color-warning)` | 警告色 |
| `#f56c6c` | `var(--color-danger)` | 危险色 |

## 注意事项

1. **优先使用 CSS 变量**：在编写新组件时，始终使用 CSS 变量而不是硬编码颜色值
2. **避免内联样式**：尽量避免在模板中使用内联样式的颜色值
3. **测试深色模式**：在开发新功能时，确保在浅色和深色模式下都进行测试
4. **保持一致性**：使用语义化的颜色变量名，确保整个应用的视觉一致性

## 扩展颜色系统

如果需要添加新的颜色变量：

1. 在 `colors.ts` 中的 `ColorTheme` 接口添加新属性
2. 在 `lightTheme` 和 `darkTheme` 中添加对应的颜色值
3. 在 `theme.css` 中添加对应的 CSS 变量定义
4. 更新本文档的颜色变量列表
