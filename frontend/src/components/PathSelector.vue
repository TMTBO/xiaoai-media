<template>
  <div class="path-selector">
    <!-- 当前选择显示 -->
    <div style="display: flex; align-items: center; gap: 8px">
      <el-input 
        :model-value="displayText" 
        :placeholder="placeholder"
        readonly
        style="cursor: pointer"
        @click="openBrowser"
      />
      <el-button @click="openBrowser">
        <el-icon style="margin-right: 4px">
          <FolderOpened />
        </el-icon>
        浏览
      </el-button>
    </div>
    <div
      v-if="hint"
      :style="{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px' }"
    >
      {{ hint }}
    </div>

    <!-- 已选择的内容 -->
    <div
      v-if="hasSelection"
      style="margin-top: 8px"
    >
      <!-- 已选择的目录（旧版单目录支持） -->
      <el-tag 
        v-if="selectedDirectory"
        closable
        type="success"
        style="margin-right: 8px; margin-bottom: 8px"
        @close="clearDirectory"
      >
        <el-icon style="margin-right: 4px">
          <Folder />
        </el-icon>
        {{ getFileName(selectedDirectory) }}
      </el-tag>
            
      <!-- 已选择的目录（新版多目录支持） -->
      <el-tag 
        v-for="(dir, index) in selectedDirectories" 
        :key="dir"
        closable
        type="success"
        style="margin-right: 8px; margin-bottom: 8px"
        @close="removeDirectory(index)"
      >
        <el-icon style="margin-right: 4px">
          <Folder />
        </el-icon>
        {{ getFileName(dir) }}
      </el-tag>
            
      <!-- 已选择的文件 -->
      <el-tag 
        v-for="(file, index) in selectedFiles" 
        :key="file"
        closable
        style="margin-right: 8px; margin-bottom: 8px"
        @close="removeFile(index)"
      >
        <el-icon style="margin-right: 4px">
          <Document />
        </el-icon>
        {{ getFileName(file) }}
      </el-tag>
    </div>

    <!-- 浏览器对话框 -->
    <el-dialog 
      v-model="showBrowser" 
      title="选择目录或文件" 
      width="600px"
    >
      <!-- 当前路径 -->
      <div style="margin-bottom: 16px">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px">
          <el-button 
            size="small" 
            :disabled="!currentPath || !parentPath"
            @click="browseParent"
          >
            <el-icon><ArrowUp /></el-icon>
            上级目录
          </el-button>
          <span :style="{ flex: 1, fontSize: '14px', color: 'var(--color-text-regular)' }">
            {{ currentPath || '加载中...' }}
          </span>
          <el-button 
            v-if="currentPath"
            size="small" 
            :type="isCurrentDirectorySelected ? 'success' : 'primary'"
            @click="selectCurrentDirectory"
          >
            <el-icon style="margin-right: 4px">
              <Select v-if="isCurrentDirectorySelected" />
              <Folder v-else />
            </el-icon>
            选择当前目录
          </el-button>
        </div>
      </div>

      <!-- 目录和文件列表 -->
      <el-scrollbar height="400px">
        <div v-loading="loading">
          <!-- 目录列表 -->
          <div 
            v-for="dir in browsedDirectories" 
            :key="dir.path"
            class="item directory-item"
            :class="{ 
              'item-disabled': !dir.is_accessible,
              'item-selected': isDirectorySelected(dir.path)
            }"
          >
            <el-checkbox 
              :model-value="isDirectorySelected(dir.path)"
              :disabled="!dir.is_accessible"
              style="margin-right: 8px"
              @change="() => toggleDirectory(dir.path)"
              @click.stop
            />
            <el-icon :style="{ marginRight: '8px', fontSize: '18px', color: 'var(--color-success)' }">
              <Folder />
            </el-icon>
            <span 
              style="flex: 1; cursor: pointer"
              @click="dir.is_accessible !== false && browseSub(dir.path)"
            >
              {{ dir.name }}
            </span>
            <el-icon 
              v-if="dir.is_accessible !== false" 
              :style="{ color: 'var(--color-text-secondary)', cursor: 'pointer' }"
              @click="browseSub(dir.path)"
            >
              <ArrowRight />
            </el-icon>
            <el-icon
              v-else
              :style="{ color: 'var(--color-danger)' }"
            >
              <Lock />
            </el-icon>
          </div>

          <!-- 文件列表 -->
          <div 
            v-for="file in allFiles" 
            :key="file.path"
            class="item file-item"
            :class="{ 
              'item-selected': isFileSelected(file.path),
              'item-disabled': !file.is_audio
            }"
            @click="file.is_audio && toggleFile(file.path)"
          >
            <el-checkbox 
              :model-value="isFileSelected(file.path)"
              :disabled="!file.is_audio"
              style="margin-right: 8px"
              @change="() => toggleFile(file.path)"
              @click.stop
            />
            <el-icon 
              :style="{ 
                marginRight: '8px', 
                fontSize: '18px',
                color: file.is_audio ? 'var(--color-primary)' : 'var(--color-text-disabled)' 
              }"
            >
              <Document />
            </el-icon>
            <span
              :style="{ 
                flex: 1, 
                color: file.is_audio ? 'var(--color-text-primary)' : 'var(--color-text-disabled)' 
              }"
            >
              {{ file.name }}
            </span>
            <span 
              :style="{ 
                fontSize: '12px', 
                color: file.is_audio ? 'var(--color-text-secondary)' : 'var(--color-text-disabled)' 
              }"
            >
              {{ formatSize(file.size) }}
            </span>
          </div>

          <el-empty 
            v-if="!loading && browsedDirectories.length === 0 && allFiles.length === 0" 
            description="此目录为空" 
          />
        </div>
      </el-scrollbar>

      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span :style="{ fontSize: '14px', color: 'var(--color-text-regular)' }">
            <span v-if="tempSelectedDirectories.length > 0 && tempSelectedFiles.length > 0">
              已选择 {{ tempSelectedDirectories.length }} 个目录和 {{ tempSelectedFiles.length }} 个文件
            </span>
            <span v-else-if="tempSelectedDirectories.length > 0">
              已选择 {{ tempSelectedDirectories.length }} 个目录
            </span>
            <span v-else-if="tempSelectedFiles.length > 0">
              已选择 {{ tempSelectedFiles.length }} 个文件
            </span>
            <span
              v-else
              :style="{ color: 'var(--color-text-disabled)' }"
            >
              请选择目录或文件
            </span>
          </span>
          <div>
            <el-button @click="showBrowser = false">
              取消
            </el-button>
            <el-button 
              type="primary" 
              :disabled="tempSelectedDirectories.length === 0 && tempSelectedFiles.length === 0"
              @click="confirmSelection"
            >
              确定
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { FolderOpened, Document, Folder, ArrowRight, ArrowUp, Lock, Select } from '@element-plus/icons-vue'
import { api, type DirectoryInfo, type FileInfo } from '@/api'

interface FileInfoExtended extends FileInfo {
    is_audio: boolean
}

interface Props {
    directory?: string
    directories?: string[]
    files?: string[]
    placeholder?: string
    hint?: string
    audioExtensions?: string[]
}

interface Emits {
    (e: 'update:directory', value: string): void
    (e: 'update:directories', value: string[]): void
    (e: 'update:files', value: string[]): void
}

const props = withDefaults(defineProps<Props>(), {
    directory: '',
    directories: () => [],
    files: () => [],
    placeholder: '点击输入框或浏览按钮选择目录或文件',
    hint: '可以选择一个或多个目录，或选择一个或多个文件',
    audioExtensions: () => ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma']
})

const emit = defineEmits<Emits>()

// 浏览器状态
const showBrowser = ref(false)
const loading = ref(false)
const currentPath = ref('')
const parentPath = ref<string | null>(null)
const browsedDirectories = ref<DirectoryInfo[]>([])
const allFiles = ref<FileInfoExtended[]>([])

// 临时选择状态
const tempSelectedDirectories = ref<string[]>([])
const tempSelectedFiles = ref<string[]>([])

// 已确认的选择
const selectedDirectory = computed(() => props.directory || '')
const selectedDirectories = computed(() => props.directories || [])
const selectedFiles = computed(() => props.files || [])

// 是否有选择
const hasSelection = computed(() => 
    selectedDirectory.value || 
    selectedDirectories.value.length > 0 || 
    selectedFiles.value.length > 0
)

// 使用传入的音频文件扩展名
const audioExtensions = computed(() => props.audioExtensions || ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma'])

// 显示文本
const displayText = computed(() => {
    const legacyDirCount = selectedDirectory.value ? 1 : 0
    const dirCount = selectedDirectories.value.length + legacyDirCount
    const fileCount = selectedFiles.value.length
    
    if (dirCount === 0 && fileCount === 0) {
        return ''
    }
    
    if (dirCount === 1 && fileCount === 0) {
        const singleDir = selectedDirectory.value || selectedDirectories.value[0]
        return getFileName(singleDir)
    }
    
    if (dirCount === 0 && fileCount === 1) {
        return getFileName(selectedFiles.value[0])
    }
    
    const parts = []
    if (dirCount > 0) parts.push(`${dirCount} 个目录`)
    if (fileCount > 0) parts.push(`${fileCount} 个文件`)
    return `已选择 ${parts.join('和')}`
})

// 获取文件名
function getFileName(path: string): string {
    return path.split('/').pop() || path
}

// 格式化文件大小
function formatSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 检查是否为音频文件
function isAudioFile(filename: string): boolean {
    const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase()
    return audioExtensions.value.includes(ext)
}

// 计算属性：当前目录是否已选中
const isCurrentDirectorySelected = computed(() => {
    return tempSelectedDirectories.value.includes(currentPath.value)
})

// 打开浏览器
function openBrowser(): void {
    // 初始化临时选择状态
    tempSelectedDirectories.value = [...selectedDirectories.value]
    // 兼容旧版单目录
    if (selectedDirectory.value && !tempSelectedDirectories.value.includes(selectedDirectory.value)) {
        tempSelectedDirectories.value.push(selectedDirectory.value)
    }
    tempSelectedFiles.value = [...selectedFiles.value]
    showBrowser.value = true
}

// 浏览子目录
async function browseSub(path: string): Promise<void> {
    loading.value = true
    try {
        const data = await api.browseDirectory(path)
        currentPath.value = data.current_path
        parentPath.value = data.parent_path
        browsedDirectories.value = data.directories
        
        // 处理文件列表，标记是否为音频文件
        allFiles.value = (data.files || []).map(file => ({
            ...file,
            is_audio: isAudioFile(file.name)
        }))
    } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } }; message?: string }
        ElMessage.error(`浏览目录失败: ${err.response?.data?.detail || err.message || '未知错误'}`)
    } finally {
        loading.value = false
    }
}

// 浏览父目录
async function browseParent(): Promise<void> {
    if (parentPath.value) {
        await browseSub(parentPath.value)
    }
}

// 选择当前目录
function selectCurrentDirectory(): void {
    if (currentPath.value) {
        toggleDirectory(currentPath.value)
    }
}

// 检查目录是否已选中（包括父目录被选中的情况）
function isDirectorySelected(path: string): boolean {
    // 标准化路径（移除尾部斜杠）
    const normalizedPath = path.endsWith('/') ? path.slice(0, -1) : path
    
    // 直接选中
    if (tempSelectedDirectories.value.some(dir => {
        const normalizedDir = dir.endsWith('/') ? dir.slice(0, -1) : dir
        return normalizedDir === normalizedPath
    })) {
        return true
    }
    
    // 检查是否有父目录被选中
    for (const selectedDir of tempSelectedDirectories.value) {
        const normalizedSelectedDir = selectedDir.endsWith('/') ? selectedDir.slice(0, -1) : selectedDir
        if (normalizedPath.startsWith(normalizedSelectedDir + '/')) {
            return true
        }
    }
    
    return false
}

// 切换目录选择状态
function toggleDirectory(path: string): void {
    const index = tempSelectedDirectories.value.indexOf(path)
    if (index > -1) {
        // 取消选择
        tempSelectedDirectories.value.splice(index, 1)
    } else {
        // 选择该目录
        tempSelectedDirectories.value.push(path)
    }
}

// 检查文件是否已选择（考虑目录选择）
function isFileSelected(path: string): boolean {
    // 如果文件在选中列表中
    if (tempSelectedFiles.value.includes(path)) {
        return true
    }
    
    // 如果选中了目录，检查文件是否在任一选中目录下且是音频文件
    for (const dir of tempSelectedDirectories.value) {
        const isInDirectory = path.startsWith(dir + '/')
        if (isInDirectory) {
            // 检查是否为音频文件
            const fileName = path.split('/').pop() || ''
            if (isAudioFile(fileName)) {
                return true
            }
        }
    }
    
    return false
}

// 切换文件选择状态
function toggleFile(path: string): void {
    const index = tempSelectedFiles.value.indexOf(path)
    if (index > -1) {
        tempSelectedFiles.value.splice(index, 1)
    } else {
        tempSelectedFiles.value.push(path)
    }
}

// 清除目录选择（旧版单目录）
function clearDirectory(): void {
    emit('update:directory', '')
}

// 移除目录（新版多目录）
function removeDirectory(index: number): void {
    const newDirs = [...selectedDirectories.value]
    newDirs.splice(index, 1)
    emit('update:directories', newDirs)
}

// 移除文件
function removeFile(index: number): void {
    const newFiles = [...selectedFiles.value]
    newFiles.splice(index, 1)
    emit('update:files', newFiles)
}

// 确认选择
function confirmSelection(): void {
    // 更新目录（新版多目录）
    emit('update:directories', [...tempSelectedDirectories.value])
    
    // 更新文件
    emit('update:files', [...tempSelectedFiles.value])
    
    showBrowser.value = false
    
    // 显示成功消息
    const dirCount = tempSelectedDirectories.value.length
    const fileCount = tempSelectedFiles.value.length
    
    if (dirCount > 0 && fileCount > 0) {
        ElMessage.success(`已选择 ${dirCount} 个目录和 ${fileCount} 个文件`)
    } else if (dirCount > 0) {
        ElMessage.success(`已选择 ${dirCount} 个目录`)
    } else if (fileCount > 0) {
        ElMessage.success(`已选择 ${fileCount} 个文件`)
    }
}

// 监听对话框打开
watch(showBrowser, (val) => {
    if (val) {
        // 打开时加载初始目录
        browseSub('')
    }
})
</script>

<style scoped>
.path-selector {
    width: 100%;
}

.item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--color-border-light);
    cursor: pointer;
    transition: background-color 0.2s;
}

.item:hover {
    background-color: var(--color-bg-secondary);
}

.item-disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.item-disabled:hover {
    background-color: transparent;
}

.item-selected {
    background-color: var(--color-table-row-active-bg);
}

.directory-item {
    /* 目录样式 */
}

.file-item {
    /* 文件样式 */
}

/* 让只读输入框看起来可点击 */
:deep(.el-input__wrapper) {
    cursor: pointer;
}
</style>
