# PathSelector 组件

统一的路径选择器组件，支持同时选择目录和文件。

## 功能特点

- 🎯 统一界面：目录和文件在同一个列表中显示
- ✅ 灵活选择：可以同时选择目录和多个文件
- 📁 目录导航：支持浏览文件系统，上下级目录切换
- 🎵 智能标识：音频文件正常显示，非音频文件灰色不可选
- 💾 文件信息：显示文件大小
- 🏷️ 标签显示：已选项以标签形式展示，可单独移除
- 🔘 快捷选择：顶部按钮可快速选择当前目录

## 使用方法

### 基本用法

```vue
<template>
  <PathSelector 
    v-model:directory="selectedDirectory"
    v-model:files="selectedFiles"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PathSelector from '@/components/PathSelector.vue'

const selectedDirectory = ref('')
const selectedFiles = ref<string[]>([])
</script>
```

### 完整示例

```vue
<template>
  <div>
    <PathSelector 
      v-model:directory="selectedDirectory"
      v-model:files="selectedFiles"
      placeholder="选择目录或文件"
      hint="可以选择一个目录，或选择一个或多个文件"
    />
    
    <div v-if="selectedDirectory">
      已选择目录: {{ selectedDirectory }}
    </div>
    
    <div v-if="selectedFiles.length > 0">
      已选择 {{ selectedFiles.length }} 个文件:
      <ul>
        <li v-for="file in selectedFiles" :key="file">{{ file }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PathSelector from '@/components/PathSelector.vue'

const selectedDirectory = ref('')
const selectedFiles = ref<string[]>([])
</script>
```

## Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| directory | `string` | `''` | 已选择的目录路径 |
| files | `string[]` | `[]` | 已选择的文件路径列表 |
| placeholder | `string` | `'点击输入框或浏览按钮选择目录或文件'` | 输入框占位符 |
| hint | `string` | `'可以选择一个目录，或选择一个或多个文件'` | 提示文本 |

## Events

| 事件 | 参数 | 说明 |
|------|------|------|
| update:directory | `value: string` | 目录选择变化时触发 |
| update:files | `value: string[]` | 文件选择变化时触发 |

## 交互说明

### 目录操作

- **选择目录**：点击目录旁的复选框
- **进入目录**：点击目录名称或右箭头
- **选择当前目录**：点击顶部的"选择当前目录"按钮

### 文件操作

- **选择文件**：点击文件旁的复选框（仅音频文件可选）
- **多选文件**：可以选择多个文件
- **非音频文件**：显示为灰色，不可选择

### 已选项管理

- 已选择的目录和文件会在输入框下方显示为标签
- 目录标签显示为绿色，带文件夹图标
- 文件标签显示为默认颜色，带文档图标
- 点击标签上的 × 可以移除该项

## 支持的音频格式

- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- WAV (.wav)
- OGG (.ogg)
- AAC (.aac)
- WMA (.wma)

## 注意事项

1. 可以同时选择目录和文件
2. 非音频文件会显示为灰色且不可选
3. 需要后端 API 支持 `/playlists/directories/browse` 端点
4. 文件路径使用绝对路径

## 依赖

- Element Plus
- @element-plus/icons-vue
- 后端 API (`api.browseDirectory`)

