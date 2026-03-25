<template>
    <div class="playlist-manager">
        <!-- 设备选择器 -->
        <el-card shadow="never" class="device-selector">
            <el-form inline>
                <el-form-item label="目标设备">
                    <el-select v-model="deviceId" placeholder="留空则使用默认设备" clearable style="width: 240px"
                        :loading="devicesLoading" no-data-text="暂无设备，请先在配置页填写账号后点击刷新">
                        <el-option v-for="d in devices" :key="d.deviceID" :label="`${d.name} (${d.deviceID})`"
                            :value="d.deviceID" />
                    </el-select>
                    <el-button :loading="devicesLoading" style="margin-left: 8px" @click="loadDevices">
                        <el-icon>
                            <Refresh />
                        </el-icon>
                    </el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 播单列表 -->
        <el-card style="margin-top: 16px">
            <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center">
                    <span>
                        <el-icon style="vertical-align: middle; margin-right: 6px">
                            <List />
                        </el-icon>播单管理
                    </span>
                    <el-button type="primary" size="small" @click="showCreateDialog = true">
                        <el-icon style="margin-right: 4px">
                            <Plus />
                        </el-icon>新建播单
                    </el-button>
                </div>
            </template>

            <el-table :data="playlists" v-loading="playlistsLoading" style="width: 100%" empty-text="暂无播单，点击上方按钮创建新播单">
                <el-table-column prop="name" label="播单名称" min-width="150" />
                <el-table-column prop="type" label="类型" width="120" />
                <el-table-column label="项目数" width="100">
                    <template #default="{ row }">
                        {{ row.item_count }}
                    </template>
                </el-table-column>
                <el-table-column prop="voice_keywords" label="语音关键词" min-width="200">
                    <template #default="{ row }">
                        <el-tag v-for="keyword in row.voice_keywords" :key="keyword" size="small"
                            style="margin-right: 4px">
                            {{ keyword }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="播放模式" width="120">
                    <template #default="{ row }">
                        <el-select v-model="row.play_mode" size="small" @change="handlePlayModeChange(row)">
                            <el-option label="列表循环" value="loop" />
                            <el-option label="单曲循环" value="single" />
                            <el-option label="随机播放" value="random" />
                        </el-select>
                    </template>
                </el-table-column>
                <el-table-column label="当前位置" width="100">
                    <template #default="{ row }">
                        {{ row.current_index + 1 }} / {{ row.item_count }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="280" fixed="right">
                    <template #default="{ row }">
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <div style="display: flex; gap: 4px;">
                                <el-button size="small" type="success" :disabled="!row.item_count" @click="handlePlay(row)" style="flex: 1;">
                                    <el-icon style="margin-right: 4px">
                                        <VideoPlay />
                                    </el-icon>播放
                                </el-button>
                                <el-button size="small" type="primary" :disabled="!row.item_count" @click="handleContinue(row)" style="flex: 1;">
                                    <el-icon style="margin-right: 4px">
                                        <CaretRight />
                                    </el-icon>继续
                                </el-button>
                                <el-button size="small" type="warning" :disabled="!row.item_count" @click="handleStop(row)" style="flex: 1;">
                                    <el-icon style="margin-right: 4px">
                                        <VideoPause />
                                    </el-icon>停止
                                </el-button>
                            </div>
                            <div style="display: flex; gap: 4px;">
                                <el-button size="small" @click="handleEdit(row)" style="flex: 1;">编辑</el-button>
                                <el-button size="small" @click="handleManageItems(row)" style="flex: 1;">项目</el-button>
                                <el-button size="small" type="danger" @click="handleDelete(row)" style="flex: 1;">删除</el-button>
                            </div>
                        </div>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <!-- 创建/编辑播单对话框 -->
        <el-dialog v-model="showCreateDialog" :title="editingPlaylist ? '编辑播单' : '创建播单'" width="600px">
            <el-form :model="playlistForm" label-width="100px">
                <el-form-item label="播单名称" required>
                    <el-input v-model="playlistForm.name" placeholder="例如：我的音乐" />
                </el-form-item>
                <el-form-item label="类型">
                    <el-select v-model="playlistForm.type" placeholder="请选择播单类型" clearable style="width: 100%">
                        <el-option label="音乐" value="music" />
                        <el-option label="有声书" value="audiobook" />
                        <el-option label="播客" value="podcast" />
                        <el-option label="广播剧" value="radio_drama" />
                        <el-option label="其他" value="other" />
                    </el-select>
                </el-form-item>
                <el-form-item label="描述">
                    <el-input v-model="playlistForm.description" type="textarea" :rows="3" placeholder="播单描述（可选）" />
                </el-form-item>
                <el-form-item label="播放间隔">
                    <el-input v-model="playlistForm.interval" placeholder="秒数或时长（如 300 或 04:32）" />
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        播放间隔，可以是秒数（如 300）或时长字符串（如 04:32），可选
                    </div>
                </el-form-item>
                <el-form-item label="封面图片">
                    <el-input v-model="playlistForm.pic_url" placeholder="封面图片URL（可选）" />
                </el-form-item>
                <el-form-item label="语音关键词">
                    <el-select v-model="playlistForm.voice_keywords" multiple filterable allow-create
                        default-first-option placeholder="输入关键词后按回车添加，例如：音乐、我的歌单" style="width: 100%">
                    </el-select>
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        语音关键词用于语音命令识别，例如："播放音乐播单"
                    </div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showCreateDialog = false">取消</el-button>
                <el-button type="primary" @click="handleSavePlaylist" :loading="saving">
                    {{ editingPlaylist ? '保存' : '创建' }}
                </el-button>
            </template>
        </el-dialog>

        <!-- 编辑播单项对话框 -->
        <el-dialog v-model="showItemsDialog" :title="`编辑播单：${currentPlaylist?.name}`" width="900px">
            <div style="margin-bottom: 16px">
                <el-button type="primary" size="small" @click="showAddItemDialog = true">
                    <el-icon style="margin-right: 4px">
                        <Plus />
                    </el-icon>添加项目
                </el-button>
                <el-button type="success" size="small" @click="showBatchImportDialog = true" style="margin-left: 8px">
                    <el-icon style="margin-right: 4px">
                        <FolderOpened />
                    </el-icon>批量导入
                </el-button>
            </div>

            <el-table :data="currentPlaylist?.items" style="width: 100%" empty-text="暂无项目，点击上方按钮添加">
                <el-table-column type="index" label="#" width="50" />
                <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
                <el-table-column prop="artist" label="艺术家" width="120" show-overflow-tooltip />
                <el-table-column prop="album" label="专辑" width="120" show-overflow-tooltip />
                <el-table-column label="URL" width="100">
                    <template #default="{ row }">
                        <el-tag v-if="row.url" type="success" size="small">有</el-tag>
                        <el-tag v-else type="info" size="small">动态获取</el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="100">
                    <template #default="{ $index }">
                        <el-button size="small" type="danger" @click="handleDeleteItem($index)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

            <template #footer>
                <el-button @click="showItemsDialog = false">关闭</el-button>
            </template>
        </el-dialog>

        <!-- 添加项目对话框 -->
        <el-dialog v-model="showAddItemDialog" title="添加项目" width="600px">
            <el-form :model="itemForm" label-width="100px">
                <el-form-item label="标题" required>
                    <el-input v-model="itemForm.title" placeholder="歌曲名" />
                </el-form-item>
                <el-form-item label="艺术家">
                    <el-input v-model="itemForm.artist" placeholder="艺术家" />
                </el-form-item>
                <el-form-item label="专辑">
                    <el-input v-model="itemForm.album" placeholder="专辑名" />
                </el-form-item>
                <el-form-item label="音频ID">
                    <el-input v-model="itemForm.audio_id" placeholder="音频ID（可选）" />
                </el-form-item>
                <el-form-item label="音频 URL">
                    <el-input v-model="itemForm.url" type="textarea" :rows="2"
                        placeholder="如果留空，则需要配置音频ID或自定义参数通过 user_config.py 动态获取" />
                </el-form-item>
                <el-form-item label="播放间隔">
                    <el-input v-model="itemForm.interval" placeholder="秒数或时长（如 300 或 04:32）" />
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        播放间隔，可以是秒数（如 300）或时长字符串（如 04:32），可选
                    </div>
                </el-form-item>
                <el-form-item label="封面图片">
                    <el-input v-model="itemForm.pic_url" placeholder="封面图片URL（可选）" />
                </el-form-item>
                <el-form-item label="自定义参数">
                    <el-input v-model="customParamsText" type="textarea" :rows="4"
                        placeholder='JSON 格式，例如：{"type": "music", "platform": "tx", "song_id": "123"}' />
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        当音频 URL 为空时，会将此参数传递给 user_config.py 中的 get_audio_url 函数
                    </div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddItemDialog = false">取消</el-button>
                <el-button type="primary" @click="handleAddItem" :loading="saving">添加</el-button>
            </template>
        </el-dialog>

        <!-- 批量导入对话框 -->
        <el-dialog v-model="showBatchImportDialog" title="批量导入音频文件" width="700px">
            <!-- 环境提示 -->
            <el-alert 
                :title="isDockerEnv ? 'Docker模式' : '本地模式'" 
                :type="isDockerEnv ? 'info' : 'success'"
                :description="environmentMessage"
                style="margin-bottom: 20px"
                show-icon
                :closable="false"
            />

            <el-form :model="importForm" label-width="120px">
                <!-- 导入模式选择 -->
                <el-form-item label="导入模式">
                    <el-radio-group v-model="importMode">
                        <el-radio label="path">从服务器路径导入</el-radio>
                        <el-radio label="upload">从浏览器上传</el-radio>
                    </el-radio-group>
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        <div v-if="importMode === 'path'">从服务器文件系统导入（适合Docker或本地服务器）</div>
                        <div v-else>直接从浏览器上传文件（适合少量文件）</div>
                    </div>
                </el-form-item>

                <!-- 路径导入模式 -->
                <template v-if="importMode === 'path'">
                    <!-- 统一的路径选择器 -->
                    <el-form-item label="选择路径" required>
                        <PathSelector 
                            v-model:directory="importForm.directory"
                            v-model:files="importForm.files"
                            placeholder="点击选择目录或文件"
                            hint="可以选择一个目录批量导入，或选择一个或多个文件精确导入"
                        />
                    </el-form-item>

                <!-- 导入选项（仅目录模式） -->
                <el-form-item v-if="importForm.directory" label="扫描选项">
                    <el-checkbox v-model="importForm.recursive">
                        递归扫描子目录
                    </el-checkbox>
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        开启后会扫描所有子目录中的音频文件
                    </div>
                </el-form-item>

                <el-form-item v-if="importForm.directory" label="文件格式">
                    <el-checkbox-group v-model="importForm.file_extensions">
                        <el-checkbox label=".mp3">MP3</el-checkbox>
                        <el-checkbox label=".m4a">M4A</el-checkbox>
                        <el-checkbox label=".flac">FLAC</el-checkbox>
                        <el-checkbox label=".wav">WAV</el-checkbox>
                        <el-checkbox label=".ogg">OGG</el-checkbox>
                        <el-checkbox label=".aac">AAC</el-checkbox>
                        <el-checkbox label=".wma">WMA</el-checkbox>
                    </el-checkbox-group>
                    <div style="font-size: 12px; color: #909399; margin-top: 4px">
                        选择要导入的音频文件格式
                    </div>
                </el-form-item>
                </template>

                <!-- 上传模式 -->
                <template v-else>
                    <el-form-item label="选择文件">
                        <el-upload
                            ref="uploadRef"
                            :auto-upload="false"
                            :file-list="uploadFileList"
                            :on-change="handleFileChange"
                            :on-remove="handleFileRemove"
                            multiple
                            accept=".mp3,.m4a,.flac,.wav,.ogg,.aac,.wma"
                            drag
                        >
                            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                            <div class="el-upload__text">
                                将文件拖到此处，或<em>点击选择文件</em>
                            </div>
                            <template #tip>
                                <div class="el-upload__tip">
                                    支持 MP3, M4A, FLAC, WAV, OGG, AAC, WMA 格式
                                </div>
                            </template>
                        </el-upload>
                    </el-form-item>

                    <el-form-item label="文件信息">
                        <div style="font-size: 12px; color: #606266">
                            已选择 <strong>{{ uploadFileList.length }}</strong> 个文件
                        </div>
                    </el-form-item>
                </template>
            </el-form>

            <!-- 导入结果 -->
            <el-alert 
                v-if="importResult"
                title="导入完成"
                type="success"
                style="margin-top: 20px"
                :closable="false"
            >
                <template #default>
                    <div style="line-height: 1.8">
                        <div>✅ 成功导入：<strong>{{ importResult.imported }}</strong> 个文件</div>
                        <div>⏭️ 跳过：<strong>{{ importResult.skipped }}</strong> 个文件</div>
                        <div>📁 扫描总数：<strong>{{ importResult.total_scanned }}</strong> 个文件</div>
                        <div>🎵 播单总数：<strong>{{ importResult.playlist_total_items }}</strong> 首</div>
                        <div v-if="importResult.skipped_files && importResult.skipped_files.length > 0" style="margin-top: 8px">
                            <el-divider style="margin: 8px 0" />
                            <div style="color: #e6a23c">部分文件被跳过：</div>
                            <ul style="margin: 4px 0; padding-left: 20px; font-size: 12px">
                                <li v-for="file in importResult.skipped_files" :key="file">{{ file }}</li>
                            </ul>
                        </div>
                    </div>
                </template>
            </el-alert>

            <template #footer>
                <el-button @click="showBatchImportDialog = false">关闭</el-button>
                <el-button 
                    v-if="importMode === 'path'"
                    type="primary" 
                    @click="handleBatchImport" 
                    :loading="importing"
                    :disabled="(!importForm.directory && (!importForm.files || importForm.files.length === 0)) || (importForm.directory && importForm.file_extensions.length === 0)"
                >
                    {{ importing ? '导入中...' : '开始导入' }}
                </el-button>
                <el-button 
                    v-else
                    type="primary" 
                    @click="handleUploadImport" 
                    :loading="importing"
                    :disabled="uploadFileList.length === 0"
                >
                    {{ importing ? '上传中...' : '上传并导入' }}
                </el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, List, Plus, VideoPlay, CaretRight, VideoPause, FolderOpened, UploadFilled } from '@element-plus/icons-vue'
import { api, type Device, type Playlist, type PlaylistIndex, type PlaylistItem, type DirectoryInfo, type ImportResult } from '@/api'
import PathSelector from '@/components/PathSelector.vue'

// 设备相关
const devices = ref<Device[]>([])
const deviceId = ref<string>('')
const devicesLoading = ref(false)

// 播单列表（索引信息）
const playlists = ref<PlaylistIndex[]>([])
const playlistsLoading = ref(false)

// 对话框状态
const showCreateDialog = ref(false)
const showItemsDialog = ref(false)
const showAddItemDialog = ref(false)
const showBatchImportDialog = ref(false)
const saving = ref(false)

// 编辑状态
const editingPlaylist = ref<PlaylistIndex | null>(null)
const currentPlaylist = ref<Playlist | null>(null)

// 表单数据
const playlistForm = ref({
    name: '',
    type: '',
    description: '',
    voice_keywords: [] as string[],
    interval: undefined as number | string | undefined,
    pic_url: '',
})

const itemForm = ref<PlaylistItem>({
    title: '',
    artist: '',
    album: '',
    audio_id: '',
    url: '',
    custom_params: {},
    interval: undefined,
    pic_url: '',
})

const customParamsText = ref('')

// 批量导入相关
const uploadRef = ref()
const importMode = ref<'path' | 'upload'>('path')
const isDockerEnv = ref(false)
const environmentMessage = ref('')
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const uploadFileList = ref<any[]>([])

const importForm = ref({
    directory: '',
    files: [] as string[],
    recursive: true,
    file_extensions: ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac'] as string[],
})

// 加载设备列表
async function loadDevices() {
    devicesLoading.value = true
    try {
        const data = await api.listDevices(true)
        devices.value = data.devices

        // 如果还没有设置设备且有默认设备，则设置默认设备
        if (!deviceId.value && data.devices.length > 0) {
            // 尝试从配置获取默认设备
            try {
                const config = await api.getConfig()
                if (config.MI_DID) {
                    // 查找匹配的设备
                    const defaultDevice = data.devices.find(d => d.deviceID === config.MI_DID)
                    if (defaultDevice) {
                        deviceId.value = config.MI_DID
                    }
                }
            } catch (error) {
                // 如果获取配置失败，忽略错误
            }
        }
    } catch (error: any) {
        ElMessage.error(`加载设备失败: ${error.message}`)
    } finally {
        devicesLoading.value = false
    }
}

// 加载播单列表
async function loadPlaylists() {
    playlistsLoading.value = true
    try {
        const data = await api.listPlaylists()
        playlists.value = data.playlists
    } catch (error: any) {
        ElMessage.error(`加载播单失败: ${error.message}`)
    } finally {
        playlistsLoading.value = false
    }
}

// 保存播单
async function handleSavePlaylist() {
    if (!playlistForm.value.name) {
        ElMessage.error('请输入播单名称')
        return
    }

    saving.value = true
    try {
        if (editingPlaylist.value) {
            // 更新播单
            await api.updatePlaylist(editingPlaylist.value.id, playlistForm.value)
            ElMessage.success('更新成功')
        } else {
            // 创建新播单
            await api.createPlaylist(playlistForm.value)
            ElMessage.success('创建成功')
        }
        showCreateDialog.value = false
        await loadPlaylists()
    } catch (error: any) {
        ElMessage.error(`保存失败: ${error.message}`)
    } finally {
        saving.value = false
    }
}

// 编辑播单基本信息
function handleEdit(playlist: PlaylistIndex) {
    editingPlaylist.value = playlist
    playlistForm.value = {
        name: playlist.name,
        type: playlist.type,
        description: playlist.description,
        voice_keywords: [...playlist.voice_keywords],
        interval: playlist.interval,
        pic_url: playlist.pic_url || '',
    }
    showCreateDialog.value = true
}

// 管理播单项
async function handleManageItems(playlist: PlaylistIndex) {
    try {
        // 加载完整的播单数据
        const fullPlaylist = await api.getPlaylistById(playlist.id)
        currentPlaylist.value = fullPlaylist
        showItemsDialog.value = true
    } catch (error: any) {
        ElMessage.error(`加载播单失败: ${error.message}`)
    }
}

// 删除播单
async function handleDelete(playlist: PlaylistIndex) {
    try {
        await ElMessageBox.confirm(`确定要删除播单"${playlist.name}"吗？`, '确认删除', {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        })

        await api.deletePlaylist(playlist.id)
        ElMessage.success('删除成功')
        await loadPlaylists()
    } catch (error: any) {
        if (error !== 'cancel') {
            ElMessage.error(`删除失败: ${error.message}`)
        }
    }
}

// 播放播单
async function handlePlay(playlist: PlaylistIndex) {
    try {
        await api.playPlaylist(playlist.id, {
            device_id: deviceId.value || undefined,
            start_index: 0,
            announce: true,
        })
        ElMessage.success(`正在播放：${playlist.name}`)
        await loadPlaylists()
    } catch (error: any) {
        ElMessage.error(`播放失败: ${error.message}`)
    }
}

// 继续播放播单
async function handleContinue(playlist: PlaylistIndex) {
    try {
        await api.continuePlaylist(playlist.id, deviceId.value || undefined, true)
        ElMessage.success(`继续播放：${playlist.name}`)
    } catch (error: any) {
        ElMessage.error(`继续播放失败: ${error.message}`)
    }
}

// 停止播放播单
async function handleStop(playlist: PlaylistIndex) {
    try {
        await api.stopPlaylist(playlist.id, deviceId.value || undefined)
        ElMessage.success(`已停止：${playlist.name}`)
    } catch (error: any) {
        ElMessage.error(`停止失败: ${error.message}`)
    }
}

// 修改播放模式
async function handlePlayModeChange(playlist: PlaylistIndex) {
    try {
        await api.setPlayMode(playlist.id, playlist.play_mode)
        ElMessage.success(`播放模式已更新为：${getPlayModeName(playlist.play_mode)}`)
    } catch (error: any) {
        ElMessage.error(`更新播放模式失败: ${error.message}`)
        await loadPlaylists()
    }
}

// 获取播放模式名称
function getPlayModeName(mode: string): string {
    const modeMap: Record<string, string> = {
        loop: '列表循环',
        single: '单曲循环',
        random: '随机播放',
    }
    return modeMap[mode] || mode
}

// 页面加载时
onMounted(() => {
    loadDevices()
    loadPlaylists()
})

// 监听对话框关闭
watch(showCreateDialog, (val) => {
    if (!val) {
        resetCreateForm()
    }
})
async function handleAddItem() {
    if (!itemForm.value.title) {
        ElMessage.error('请输入标题')
        return
    }

    // 解析自定义参数
    let customParams = {}
    if (customParamsText.value.trim()) {
        try {
            customParams = JSON.parse(customParamsText.value)
        } catch (error) {
            ElMessage.error('自定义参数 JSON 格式错误')
            return
        }
    }

    const newItem: PlaylistItem = {
        ...itemForm.value,
        custom_params: customParams,
    }

    saving.value = true
    try {
        await api.addPlaylistItems(currentPlaylist.value!.id, { items: [newItem] })
        ElMessage.success('添加成功')
        showAddItemDialog.value = false

        // 重置表单
        itemForm.value = {
            title: '',
            artist: '',
            album: '',
            audio_id: '',
            url: '',
            custom_params: {},
            interval: undefined,
            pic_url: '',
        }
        customParamsText.value = ''

        // 重新加载播单
        await loadPlaylists()

        // 更新当前播单（需要重新加载完整数据）
        const fullPlaylist = await api.getPlaylistById(currentPlaylist.value!.id)
        currentPlaylist.value = fullPlaylist
    } catch (error: any) {
        ElMessage.error(`添加失败: ${error.message}`)
    } finally {
        saving.value = false
    }
}

// 删除播单项
async function handleDeleteItem(index: number) {
    try {
        await ElMessageBox.confirm('确定要删除该项吗？', '确认删除', {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        })

        await api.deletePlaylistItem(currentPlaylist.value!.id, index)
        ElMessage.success('删除成功')

        // 重新加载播单
        await loadPlaylists()

        // 更新当前播单（需要重新加载完整数据）
        const fullPlaylist = await api.getPlaylistById(currentPlaylist.value!.id)
        currentPlaylist.value = fullPlaylist
    } catch (error: any) {
        if (error !== 'cancel') {
            ElMessage.error(`删除失败: ${error.message}`)
        }
    }
}

// 在创建对话框关闭时重置表单
function resetCreateForm() {
    editingPlaylist.value = null
    playlistForm.value = {
        name: '',
        type: '',
        description: '',
        voice_keywords: [],
        interval: undefined as number | string | undefined,
        pic_url: '',
    }
}

// 加载环境信息
async function loadEnvironmentInfo() {
    try {
        const data = await api.getAvailableDirectories()
        isDockerEnv.value = data.is_docker
        environmentMessage.value = data.message
    } catch (error: any) {
        ElMessage.error(`加载环境信息失败: ${error.message}`)
    }
}

// 批量导入
async function handleBatchImport() {
    // 验证输入
    const hasDirectory = !!importForm.value.directory
    const hasFiles = importForm.value.files && importForm.value.files.length > 0
    
    if (!hasDirectory && !hasFiles) {
        ElMessage.error('请选择目录或文件')
        return
    }
    
    if (hasDirectory && importForm.value.file_extensions.length === 0) {
        ElMessage.error('请至少选择一种文件格式')
        return
    }

    if (!currentPlaylist.value) {
        ElMessage.error('请先选择一个播单')
        return
    }

    importing.value = true
    importResult.value = null

    try {
        const requestData: any = {}
        
        if (hasDirectory) {
            requestData.directory = importForm.value.directory
            requestData.recursive = importForm.value.recursive
            requestData.file_extensions = importForm.value.file_extensions
        }
        
        if (hasFiles) {
            requestData.files = importForm.value.files
        }

        const result = await api.importFromDirectory(currentPlaylist.value.id, requestData)

        importResult.value = result

        if (result.imported > 0) {
            ElMessage.success(`成功导入 ${result.imported} 个文件`)
            
            // 重新加载播单列表
            await loadPlaylists()
            
            // 重新加载当前播单
            const fullPlaylist = await api.getPlaylistById(currentPlaylist.value.id)
            currentPlaylist.value = fullPlaylist
            
            // 关闭批量导入对话框
            showBatchImportDialog.value = false
            
            // 确保项目列表对话框保持打开状态
            // showItemsDialog 已经是 true，无需额外操作
        } else {
            ElMessage.warning('没有文件被导入，请检查路径和文件格式')
        }
    } catch (error: any) {
        ElMessage.error(`导入失败: ${error.response?.data?.detail || error.message}`)
    } finally {
        importing.value = false
    }
}

// 重置批量导入表单
function resetImportForm() {
    importMode.value = 'path'
    importForm.value = {
        directory: '',
        files: [],
        recursive: true,
        file_extensions: ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac'],
    }
    uploadFileList.value = []
    if (uploadRef.value) {
        uploadRef.value.clearFiles()
    }
    importResult.value = null
}

// 处理文件变化
function handleFileChange(_file: any, fileList: any[]) {
    uploadFileList.value = fileList
}

// 处理文件移除
function handleFileRemove(_file: any, fileList: any[]) {
    uploadFileList.value = fileList
}

// 处理上传导入
async function handleUploadImport() {
    if (uploadFileList.value.length === 0) {
        ElMessage.error('请选择要上传的文件')
        return
    }

    if (!currentPlaylist.value) {
        ElMessage.error('请先选择一个播单')
        return
    }

    importing.value = true
    importResult.value = null

    try {
        // 从上传的文件中提取信息并创建播单项
        const items: PlaylistItem[] = []
        
        for (const fileItem of uploadFileList.value) {
            const file = fileItem.raw as File
            
            // 从文件名提取信息
            const fileName = file.name
            const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.')) || fileName
            
            // 尝试从文件路径提取艺术家和专辑
            const webkitPath = (file as any).webkitRelativePath || fileName
            const pathParts = webkitPath.split('/')
            
            let artist = ''
            let album = ''
            
            if (pathParts.length >= 3) {
                artist = pathParts[pathParts.length - 3]
                album = pathParts[pathParts.length - 2]
            } else if (pathParts.length === 2) {
                album = pathParts[0]
            }
            
            // 读取文件内容并转换为base64或创建临时URL
            // 注意：这里我们创建一个临时的对象URL
            const fileUrl = URL.createObjectURL(file)
            
            items.push({
                title: nameWithoutExt,
                artist: artist,
                album: album,
                audio_id: '',
                url: fileUrl,
                custom_params: {
                    file_name: fileName,
                    file_size: file.size,
                    file_type: file.type,
                    uploaded: true,
                },
                interval: undefined,
                pic_url: undefined,
            })
        }

        // 添加到播单
        await api.addPlaylistItems(currentPlaylist.value.id, { items })
        
        // 设置结果
        importResult.value = {
            imported: items.length,
            skipped: 0,
            total_scanned: uploadFileList.value.length,
            playlist_total_items: currentPlaylist.value.items.length + items.length,
        }

        ElMessage.success(`成功上传 ${items.length} 个文件`)
        
        // 重新加载播单列表
        await loadPlaylists()
        
        // 重新加载当前播单
        const fullPlaylist = await api.getPlaylistById(currentPlaylist.value.id)
        currentPlaylist.value = fullPlaylist
        
        // 清空上传列表
        uploadFileList.value = []
        if (uploadRef.value) {
            uploadRef.value.clearFiles()
        }
    } catch (error: any) {
        ElMessage.error(`上传失败: ${error.response?.data?.detail || error.message}`)
    } finally {
        importing.value = false
    }
}

// 页面加载时
onMounted(() => {
    loadDevices()
    loadPlaylists()
})

// 监听对话框关闭
watch(showCreateDialog, (val) => {
    if (!val) {
        resetCreateForm()
    }
})

watch(showBatchImportDialog, (val) => {
    if (val) {
        // 打开对话框时加载环境信息
        loadEnvironmentInfo()
    } else {
        // 关闭对话框时重置表单
        resetImportForm()
    }
})
</script>

<style scoped>
.playlist-manager {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.device-selector :deep(.el-form--inline .el-form-item) {
    margin-bottom: 0;
}
</style>
