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
                <el-table-column label="操作" width="300" fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" type="success" :disabled="!row.item_count" @click="handlePlay(row)">
                            <el-icon style="margin-right: 4px">
                                <VideoPlay />
                            </el-icon>播放
                        </el-button>
                        <el-button size="small" @click="handleEdit(row)">编辑</el-button>
                        <el-button size="small" @click="handleManageItems(row)">项目</el-button>
                        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
                    <el-input v-model="playlistForm.type" placeholder="例如：music, audiobook, podcast" />
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
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, List, Plus, VideoPlay } from '@element-plus/icons-vue'
import { api, type Device, type Playlist, type PlaylistIndex, type PlaylistItem } from '@/api'

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
    } catch (error: any) {
        ElMessage.error(`播放失败: ${error.message}`)
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
