<template>
    <div class="path-selector">
        <!-- 当前选择显示 -->
        <div style="display: flex; align-items: center; gap: 8px">
            <el-input 
                :model-value="displayText" 
                :placeholder="placeholder"
                readonly
                @click="openBrowser"
                style="cursor: pointer"
            />
            <el-button @click="openBrowser">
                <el-icon style="margin-right: 4px">
                    <FolderOpened />
                </el-icon>
                浏览
            </el-button>
        </div>
        <div v-if="hint" style="font-size: 12px; color: #909399; margin-top: 4px">
            {{ hint }}
        </div>

        <!-- 已选择的内容 -->
        <div v-if="hasSelection" style="margin-top: 8px">
            <!-- 已选择的目录 -->
            <el-tag 
                v-if="selectedDirectory"
                closable
                @close="clearDirectory"
                type="success"
                style="margin-right: 8px; margin-bottom: 8px"
            >
                <el-icon style="margin-right: 4px"><Folder /></el-icon>
                {{ getFileName(selectedDirectory) }}
            </el-tag>
            
            <!-- 已选择的文件 -->
            <el-tag 
                v-for="(file, index) in selectedFiles" 
                :key="file"
                closable
                @close="removeFile(index)"
                style="margin-right: 8px; margin-bottom: 8px"
            >
                <el-icon style="margin-right: 4px"><Document /></el-icon>
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
                    <span style="flex: 1; font-size: 14px; color: #606266">
                        {{ currentPath || '加载中...' }}
                    </span>
                    <el-button 
                        v-if="currentPath"
                        size="small" 
                        type="primary"
                        @click="selectCurrentDirectory"
                    >
                        <el-icon><Folder /></el-icon>
                        选择当前目录
                    </el-button>
                </div>
            </div>

            <!-- 目录和文件列表 -->
            <el-scrollbar height="400px">
                <div v-loading="loading">
                    <!-- 目录列表 -->
                    <div 
                        v-for="dir in directories" 
                        :key="dir.path"
                        class="item directory-item"
                        :class="{ 
                            'item-disabled': !dir.is_accessible,
                            'item-selected': tempSelectedDirectory === dir.path
                        }"
                    >
                        <el-checkbox 
                            :model-value="tempSelectedDirectory === dir.path"
                            :disabled="!dir.is_accessible"
                            @change="() => selectDirectory(dir.path)"
                            @click.stop
                            style="margin-right: 8px"
                        />
                        <el-icon style="margin-right: 8px; font-size: 18px; color: #67c23a">
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
                            style="color: #909399; cursor: pointer"
                            @click="browseSub(dir.path)"
                        >
                            <ArrowRight />
                        </el-icon>
                        <el-icon v-else style="color: #f56c6c">
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
                            @change="() => toggleFile(file.path)"
                            @click.stop
                            style="margin-right: 8px"
                        />
                        <el-icon 
                            style="margin-right: 8px; font-size: 18px"
                            :style="{ color: file.is_audio ? '#409eff' : '#c0c4cc' }"
                        >
                            <Document />
                        </el-icon>
                        <span style="flex: 1" :style="{ color: file.is_audio ? '' : '#c0c4cc' }">
                            {{ file.name }}
                        </span>
                        <span 
                            style="font-size: 12px; color: #909399"
                            :style="{ color: file.is_audio ? '#909399' : '#c0c4cc' }"
                        >
                            {{ formatSize(file.size) }}
                        </span>
                    </div>

                    <el-empty 
                        v-if="!loading && directories.length === 0 && allFiles.length === 0" 
                        description="此目录为空" 
                    />
                </div>
            </el-scrollbar>

            <template #footer>
                <div style="display: flex; justify-content: space-between; align-items: center">
                    <span style="font-size: 14px; color: #606266">
                        <span v-if="tempSelectedDirectory && tempSelectedFiles.length > 0">
                            已选择 1 个目录和 {{ tempSelectedFiles.length }} 个文件
                        </span>
                        <span v-else-if="tempSelectedDirectory">
                            已选择 1 个目录
                        </span>
                        <span v-else-if="tempSelectedFiles.length > 0">
                            已选择 {{ tempSelectedFiles.length }} 个文件
                        </span>
                        <span v-else style="color: #c0c4cc">
                            请选择目录或文件
                        </span>
                    </span>
                    <div>
                        <el-button @click="showBrowser = false">取消</el-button>
                        <el-button 
                            type="primary" 
                            @click="confirmSelection"
                            :disabled="!tempSelectedDirectory && tempSelectedFiles.length === 0"
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
import { FolderOpened, Document, Folder, ArrowRight, ArrowUp, Lock } from '@element-plus/icons-vue'
import { api, type DirectoryInfo, type FileInfo } from '@/api'

interface FileInfoExtended extends FileInfo {
    is_audio: boolean
}

interface Props {
    directory?: string
    files?: string[]
    placeholder?: string
    hint?: string
}

interface Emits {
    (e: 'update:directory', value: string): void
    (e: 'update:files', value: string[]): void
}

const props = withDefaults(defineProps<Props>(), {
    directory: '',
    files: () => [],
    placeholder: '点击输入框或浏览按钮选择目录或文件',
    hint: '可以选择一个目录，或选择一个或多个文件'
})

const emit = defineEmits<Emits>()

// 浏览器状态
const showBrowser = ref(false)
const loading = ref(false)
const currentPath = ref('')
const parentPath = ref<string | null>(null)
const directories = ref<DirectoryInfo[]>([])
const allFiles = ref<FileInfoExtended[]>([])

// 临时选择状态
const tempSelectedDirectory = ref('')
const tempSelectedFiles = ref<string[]>([])

// 已确认的选择
const selectedDirectory = computed(() => props.directory || '')
const selectedFiles = computed(() => props.files || [])

// 是否有选择
const hasSelection = computed(() => selectedDirectory.value || selectedFiles.value.length > 0)

// 音频文件扩展名
const audioExtensions = ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma']

// 显示文本
const displayText = computed(() => {
    const dirCount = selectedDirectory.value ? 1 : 0
    const fileCount = selectedFiles.value.length
    
    if (dirCount === 0 && fileCount === 0) {
        return ''
    }
    
    if (dirCount === 1 && fileCount === 0) {
        return getFileName(selectedDirectory.value)
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
    return audioExtensions.includes(ext)
}

// 打开浏览器
function openBrowser() {
    // 初始化临时选择状态
    tempSelectedDirectory.value = selectedDirectory.value
    tempSelectedFiles.value = [...selectedFiles.value]
    showBrowser.value = true
}

// 浏览子目录
async function browseSub(path: string) {
    loading.value = true
    try {
        const data = await api.browseDirectory(path)
        currentPath.value = data.current_path
        parentPath.value = data.parent_path
        directories.value = data.directories
        
        // 处理文件列表，标记是否为音频文件
        allFiles.value = (data.files || []).map(file => ({
            ...file,
            is_audio: isAudioFile(file.name)
        }))
    } catch (error: any) {
        ElMessage.error(`浏览目录失败: ${error.response?.data?.detail || error.message}`)
    } finally {
        loading.value = false
    }
}

// 浏览父目录
async function browseParent() {
    if (parentPath.value) {
        await browseSub(parentPath.value)
    }
}

// 选择当前目录
function selectCurrentDirectory() {
    if (currentPath.value) {
        if (tempSelectedDirectory.value === currentPath.value) {
            // 取消选择
            tempSelectedDirectory.value = ''
        } else {
            // 选择当前目录
            tempSelectedDirectory.value = currentPath.value
        }
    }
}

// 选择目录
function selectDirectory(path: string) {
    if (tempSelectedDirectory.value === path) {
        // 取消选择
        tempSelectedDirectory.value = ''
    } else {
        // 选择该目录
        tempSelectedDirectory.value = path
    }
}

// 检查文件是否已选择（考虑目录选择）
function isFileSelected(path: string): boolean {
    // 如果文件在选中列表中
    if (tempSelectedFiles.value.includes(path)) {
        return true
    }
    
    // 如果选中了目录，检查文件是否在该目录下且是音频文件
    if (tempSelectedDirectory.value) {
        const isInDirectory = path.startsWith(tempSelectedDirectory.value + '/')
        if (isInDirectory) {
            // 检查是否为音频文件
            const fileName = path.split('/').pop() || ''
            return isAudioFile(fileName)
        }
    }
    
    return false
}

// 切换文件选择状态
function toggleFile(path: string) {
    const index = tempSelectedFiles.value.indexOf(path)
    if (index > -1) {
        tempSelectedFiles.value.splice(index, 1)
    } else {
        tempSelectedFiles.value.push(path)
    }
}

// 清除目录选择
function clearDirectory() {
    emit('update:directory', '')
}

// 移除文件
function removeFile(index: number) {
    const newFiles = [...selectedFiles.value]
    newFiles.splice(index, 1)
    emit('update:files', newFiles)
}

// 确认选择
function confirmSelection() {
    // 更新目录
    emit('update:directory', tempSelectedDirectory.value)
    
    // 更新文件
    emit('update:files', [...tempSelectedFiles.value])
    
    showBrowser.value = false
    
    // 显示成功消息
    const dirCount = tempSelectedDirectory.value ? 1 : 0
    const fileCount = tempSelectedFiles.value.length
    
    if (dirCount > 0 && fileCount > 0) {
        ElMessage.success(`已选择 ${dirCount} 个目录和 ${fileCount} 个文件`)
    } else if (dirCount > 0) {
        ElMessage.success(`已选择目录: ${tempSelectedDirectory.value}`)
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
    border-bottom: 1px solid #ebeef5;
    cursor: pointer;
    transition: background-color 0.2s;
}

.item:hover {
    background-color: #f5f7fa;
}

.item-disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.item-disabled:hover {
    background-color: transparent;
}

.item-selected {
    background-color: #ecf5ff;
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
