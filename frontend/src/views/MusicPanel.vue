<template>
    <div class="music-panel">
        <!-- Smart voice command -->
        <el-card>
            <template #header>
                <span>
                    <el-icon style="vertical-align: middle; margin-right: 6px">
                        <Mic />
                    </el-icon>智能语音指令
                </span>
            </template>
            <el-form inline @submit.prevent="handleVoiceCommand">
                <el-form-item>
                    <el-input v-model="voiceCommandText" placeholder="例如：播放腾讯热歌榜 · 打开网易云飙升榜" clearable
                        style="width: 400px" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" native-type="submit" :loading="voiceCommandLoading">执行指令</el-button>
                </el-form-item>
            </el-form>
            <el-alert v-if="voiceCommandResult" :title="voiceCommandResultMsg" type="success" show-icon closable
                style="margin-top: 8px" @close="voiceCommandResult = null" />
        </el-card>

        <!-- Search / Charts tabs -->
        <el-card style="margin-top: 16px">
            <el-tabs v-model="activeTab" @tab-change="onTabChange">
                <!-- Search Tab -->
                <el-tab-pane label="搜索音乐" name="search">
                    <el-form inline @submit.prevent="doSearch">
                        <el-form-item label="平台">
                            <el-select v-model="searchPlatform" style="width: 130px">
                                <el-option v-for="p in platformOptions" :key="p.value" :label="p.label"
                                    :value="p.value" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="关键词">
                            <el-input v-model="searchQuery" placeholder="搜索歌曲、歌手..." clearable style="width: 260px" />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" native-type="submit" :loading="searchLoading">
                                <el-icon style="margin-right: 4px">
                                    <Search />
                                </el-icon>搜索
                            </el-button>
                        </el-form-item>
                    </el-form>

                    <div v-if="searchResults.length"
                        style="margin: 8px 0; display: flex; align-items: center; gap: 8px">
                        <span :style="{ fontSize: '13px', color: 'var(--color-text-regular)' }">共 {{ searchResults.length }} 首歌曲</span>
                        <el-button size="small" :loading="askPlayLoading" @click="handleAskPlay">
                            <el-icon style="margin-right: 4px">
                                <Bell />
                            </el-icon>询问音箱并播放全部
                        </el-button>
                        <el-button size="small" type="primary" @click="handleCreatePlaylist('search')">
                            <el-icon style="margin-right: 4px">
                                <Plus />
                            </el-icon>创建播单
                        </el-button>
                    </div>

                    <el-table :data="searchResults" v-loading="searchLoading" style="width: 100%; margin-top: 8px"
                        empty-text="暂无结果，请输入关键词搜索" :row-class-name="getSearchRowClassName"
                        @row-click="handleSearchRowClick">
                        <el-table-column prop="name" label="歌名" min-width="160" show-overflow-tooltip />
                        <el-table-column prop="singer" label="歌手" min-width="120" show-overflow-tooltip />
                        <el-table-column prop="meta.albumName" label="专辑" min-width="140" show-overflow-tooltip />
                    </el-table>
                </el-tab-pane>

                <!-- Charts Tab -->
                <el-tab-pane label="排行榜" name="charts">
                    <el-form inline>
                        <el-form-item label="平台">
                            <el-select v-model="chartPlatform" style="width: 130px" @change="onChartPlatformChange">
                                <el-option v-for="p in platformOptions" :key="p.value" :label="p.label"
                                    :value="p.value" />
                            </el-select>
                        </el-form-item>
                        <el-form-item>
                            <el-button :loading="chartsLoading" @click="loadCharts">
                                <el-icon>
                                    <Refresh />
                                </el-icon>
                            </el-button>
                        </el-form-item>
                    </el-form>

                    <div v-if="chartsLoading" v-loading="true" style="height: 80px" />
                    <div v-else-if="charts.length" class="charts-layout">
                        <!-- Left: Charts List -->
                        <div class="charts-list">
                            <div v-for="chart in charts" :key="chart.id" class="chart-item"
                                :class="{ 'chart-item--active': selectedChart?.id === chart.id }"
                                @click="loadChartSongs(chart)">
                                <el-image :src="chart.picUrl" class="chart-image" fit="cover" loading="lazy">
                                    <template #error>
                                        <div class="chart-image-error">
                                            <el-icon size="24">
                                                <VideoPlay />
                                            </el-icon>
                                        </div>
                                    </template>
                                </el-image>
                                <div class="chart-name">{{ chart.name }}</div>
                            </div>
                        </div>

                        <!-- Right: Chart Details -->
                        <div class="chart-details">
                            <template v-if="selectedChart">
                                <div
                                    style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 4px">
                                    <div style="font-size: 16px; font-weight: 600">
                                        {{ selectedChart.name }}
                                    </div>
                                    <el-button v-if="chartSongs.length" size="small" type="primary"
                                        @click="handleCreatePlaylist('chart')">
                                        <el-icon style="margin-right: 4px">
                                            <Plus />
                                        </el-icon>创建播单
                                    </el-button>
                                </div>
                                <el-table :data="chartSongs" v-loading="chartSongsLoading" style="width: 100%"
                                    empty-text="暂无歌曲" max-height="600" :row-class-name="getRowClassName"
                                    @row-click="handleRowClick">
                                    <el-table-column type="index" label="#" width="50" />
                                    <el-table-column prop="name" label="歌名" min-width="160" show-overflow-tooltip />
                                    <el-table-column prop="singer" label="歌手" min-width="120" show-overflow-tooltip />
                                    <el-table-column prop="meta.albumName" label="专辑" min-width="140"
                                        show-overflow-tooltip />
                                </el-table>
                            </template>
                            <el-empty v-else description="请点击左侧排行榜查看详情" />
                        </div>
                    </div>
                    <el-empty v-else description="点击刷新按钮加载排行榜" />
                </el-tab-pane>
            </el-tabs>
        </el-card>

        <!-- Player Control Bar -->
        <el-card v-if="currentSong" class="player-bar" style="margin-top: 16px">
            <div class="player-content">
                <div class="song-info">
                    <span class="song-name">{{ currentSong.name }}</span>
                    <span class="song-singer">{{ currentSong.singer }}</span>
                    <el-tag size="small" style="margin-left: 8px">
                        {{ playlistIndex + 1 }} / {{ playlist.length }}
                    </el-tag>
                </div>
                <div class="player-controls">
                    <el-button :loading="controlLoading" circle title="上一首" @click="handlePrev">
                        <el-icon>
                            <CaretLeft />
                        </el-icon>
                    </el-button>
                    <el-button type="primary" :loading="controlLoading" circle :title="isPaused ? '继续' : '暂停'"
                        @click="handlePlayPause">
                        <el-icon>
                            <VideoPlay v-if="isPaused" />
                            <VideoPause v-else />
                        </el-icon>
                    </el-button>
                    <el-button :loading="controlLoading" circle title="下一首" @click="handleNext">
                        <el-icon>
                            <CaretRight />
                        </el-icon>
                    </el-button>
                </div>
            </div>
        </el-card>

        <el-alert v-if="error" :title="error" type="error" show-icon closable style="margin-top: 16px"
            @close="error = ''" />

        <!-- 创建播单对话框 -->
        <el-dialog v-model="showCreatePlaylistDialog" title="创建播单" width="500px">
            <el-form :model="createPlaylistForm" label-width="80px">
                <el-form-item label="播单名称" required>
                    <el-input v-model="createPlaylistForm.name" placeholder="请输入播单名称" />
                </el-form-item>
                <el-form-item label="类型">
                    <el-select v-model="createPlaylistForm.type" style="width: 100%">
                        <el-option label="音乐" value="music" />
                        <el-option label="有声书" value="audiobook" />
                        <el-option label="播客" value="podcast" />
                        <el-option label="其他" value="other" />
                    </el-select>
                </el-form-item>
                <el-form-item label="描述">
                    <el-input v-model="createPlaylistForm.description" type="textarea" :rows="3"
                        placeholder="播单描述（可选）" />
                </el-form-item>
                <el-form-item>
                    <el-alert type="info" :closable="false" show-icon>
                        <template #title>
                            将从{{ createPlaylistSource === 'search' ? '搜索结果' : '排行榜' }}中添加
                            {{ createPlaylistSource === 'search' ? searchResults.length : chartSongs.length }} 首歌曲
                        </template>
                    </el-alert>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showCreatePlaylistDialog = false">取消</el-button>
                <el-button type="primary" :loading="createPlaylistLoading" @click="confirmCreatePlaylist">
                    创建
                </el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
    Search,
    CaretLeft,
    CaretRight,
    VideoPlay,
    VideoPause,
    Mic,
    Bell,
    Plus,
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { api, type Song, type SongQuality, type Chart, type PlaylistItem } from '@/api'
import { useDevices } from '@/composables/useDevices'

const { deviceId } = useDevices()
const activeTab = ref('search')
const error = ref('')

const platformOptions = [
    { value: 'tx', label: '腾讯音乐' },
    { value: 'kw', label: '酷我音乐' },
    { value: 'kg', label: '酷狗音乐' },
    { value: 'wy', label: '网易云音乐' },
    { value: 'mg', label: '咪咕音乐' },
]

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------
const searchPlatform = ref('tx')
const searchQuery = ref('')
const searchLoading = ref(false)
const searchResults = ref<Song[]>([])
const playingIdx = ref(-999) // negative idx means chart row, positive means search row

function normalizeSong(raw: Record<string, unknown>, platform: string): Song {
    const qualities: SongQuality[] = Array.isArray(raw.qualities)
        ? (raw.qualities as Record<string, unknown>[]).map((q) => ({
            type: String(q.type ?? '128k'),
            format: String(q.format ?? 'mp3'),
            size: (q.size as number | string) ?? 0,
        }))
        : []
    const meta = (raw.meta as Record<string, unknown>) ?? {}
    
    // interval 可能是数字或字符串（如 "04:32"）
    let interval: number | string = 0
    if (typeof raw.interval === 'number') {
        interval = raw.interval
    } else if (typeof raw.interval === 'string') {
        interval = raw.interval
    }
    
    return {
        id: String(raw.id ?? raw.songId ?? ''),
        name: String(raw.name ?? ''),
        singer: String(raw.singer ?? ''),
        platform,
        qualities,
        interval,
        meta: {
            albumName: String(meta.albumName ?? raw.albumName ?? ''),
            picUrl: String(meta.picUrl ?? raw.picUrl ?? ''),
            songId: (meta.songId ?? raw.songId ?? 0) as number | string,
        },
    }
}

async function doSearch() {
    if (!searchQuery.value.trim()) return
    searchLoading.value = true
    error.value = ''
    try {
        const data = await api.searchMusic(searchQuery.value, searchPlatform.value)
        const list: unknown[] = (data as { data?: { list?: unknown[] } }).data?.list ?? []
        searchResults.value = list.map((s) => normalizeSong(s as Record<string, unknown>, searchPlatform.value))
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '搜索失败'
    } finally {
        searchLoading.value = false
    }
}

async function playFromSearch(index: number) {
    playingIdx.value = index
    error.value = ''
    try {
        await api.syncPlaylist(searchResults.value, deviceId.value || undefined)
        await api.playMusic(index, deviceId.value || undefined)
        playlist.value = [...searchResults.value]
        playlistIndex.value = index
        isPaused.value = false
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '播放失败'
    } finally {
        playingIdx.value = -999
    }
}

function handleSearchRowClick(row: Song, column: unknown, event: Event) {
    const index = searchResults.value.findIndex(s => s.id === row.id)
    if (index >= 0) {
        playFromSearch(index)
    }
}

function getSearchRowClassName({ rowIndex }: { rowIndex: number }) {
    return playingIdx.value === rowIndex ? 'playing-row' : 'clickable-row'
}

// ---------------------------------------------------------------------------
// Charts
// ---------------------------------------------------------------------------
const chartPlatform = ref('tx')
const chartsLoading = ref(false)
const charts = ref<Chart[]>([])
const selectedChart = ref<Chart | null>(null)
const chartSongsLoading = ref(false)
const chartSongs = ref<Song[]>([])

function onChartPlatformChange() {
    selectedChart.value = null
    chartSongs.value = []
    charts.value = []
    loadCharts()
}

function onTabChange(name: string) {
    if (name === 'charts' && charts.value.length === 0) {
        loadCharts()
    }
}

async function loadCharts() {
    chartsLoading.value = true
    error.value = ''
    selectedChart.value = null
    chartSongs.value = []
    try {
        const data = await api.getRanks(chartPlatform.value)
        const list: unknown[] = (data as { data?: { list?: unknown[] } }).data?.list ?? []
        charts.value = list.map((c) => {
            const raw = c as Record<string, unknown>
            return {
                id: String(raw.id ?? ''),
                name: String(raw.name ?? ''),
                picUrl: raw.picUrl ? String(raw.picUrl) : undefined,
                updateTime: raw.updateTime ? String(raw.updateTime) : undefined,
                totalNum: typeof raw.totalNum === 'number' ? raw.totalNum : undefined,
            }
        })
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '加载排行榜失败'
    } finally {
        chartsLoading.value = false
    }
}

async function loadChartSongs(chart: Chart) {
    selectedChart.value = chart
    chartSongsLoading.value = true
    error.value = ''
    try {
        const data = await api.getRankSongs(chart.id, chartPlatform.value)
        const list: unknown[] = (data as { data?: { list?: unknown[] } }).data?.list ?? []
        chartSongs.value = list.map((s) => normalizeSong(s as Record<string, unknown>, chartPlatform.value))
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '加载歌曲失败'
    } finally {
        chartSongsLoading.value = false
    }
}

async function playFromChart(index: number) {
    playingIdx.value = -(index + 1)
    error.value = ''
    try {
        await api.syncPlaylist(chartSongs.value, deviceId.value || undefined)
        await api.playMusic(index, deviceId.value || undefined)
        playlist.value = [...chartSongs.value]
        playlistIndex.value = index
        isPaused.value = false
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '播放失败'
    } finally {
        playingIdx.value = -999
    }
}

function handleRowClick(row: Song, column: unknown, event: Event) {
    const index = chartSongs.value.findIndex(s => s.id === row.id)
    if (index >= 0) {
        playFromChart(index)
    }
}

function getRowClassName({ rowIndex }: { rowIndex: number }) {
    return playingIdx.value === -(rowIndex + 1) ? 'playing-row' : 'clickable-row'
}

// ---------------------------------------------------------------------------
// Smart voice command
// ---------------------------------------------------------------------------
const voiceCommandText = ref('')
const voiceCommandLoading = ref(false)
const voiceCommandResult = ref<Record<string, unknown> | null>(null)

const voiceCommandResultMsg = computed(() => {
    if (!voiceCommandResult.value) return ''
    const r = voiceCommandResult.value
    if (r.action === 'play_chart') return `正在播放「${r.chart}」(${r.platform})，共 ${r.total} 首歌曲`
    return `指令已发送：${r.command}`
})

async function handleVoiceCommand() {
    if (!voiceCommandText.value.trim()) return
    voiceCommandLoading.value = true
    voiceCommandResult.value = null
    error.value = ''
    try {
        const data = await api.voiceCommand(voiceCommandText.value, deviceId.value || undefined)
        voiceCommandResult.value = data as Record<string, unknown>
        if ((data as { action?: string }).action === 'play_chart') {
            await syncPlaylist()
        }
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '指令执行失败'
    } finally {
        voiceCommandLoading.value = false
    }
}

// ---------------------------------------------------------------------------
// Ask & play: TTS announces results to speaker, UI confirm triggers play
// ---------------------------------------------------------------------------
const askPlayLoading = ref(false)

async function handleAskPlay() {
    if (!searchResults.value.length) return
    askPlayLoading.value = true
    error.value = ''
    try {
        await api.announceSearch(searchQuery.value, searchResults.value.length, deviceId.value || undefined)
        askPlayLoading.value = false
        await ElMessageBox.confirm(
            `音箱已播报：共找到 ${searchResults.value.length} 首「${searchQuery.value}」相关歌曲，确认播放全部？`,
            '确认播放',
            { confirmButtonText: '播放全部', cancelButtonText: '取消', type: 'info' },
        )
        await api.syncPlaylist(searchResults.value, deviceId.value || undefined)
        await api.playMusic(0, deviceId.value || undefined)
        playlist.value = [...searchResults.value]
        playlistIndex.value = 0
        isPaused.value = false
    } catch (e: unknown) {
        // ElMessageBox cancel rejects with string 'cancel', not an Error — ignore it
        if (e instanceof Error) error.value = e.message
    } finally {
        askPlayLoading.value = false
    }
}

// ---------------------------------------------------------------------------
// Sync frontend playlist from server (used after voice-command plays a chart)
// ---------------------------------------------------------------------------
async function syncPlaylist() {
    try {
        const data = await api.getPlaylist(deviceId.value || undefined)
        if (data.total > 0) {
            playlist.value = data.songs
            playlistIndex.value = data.current
            isPaused.value = false
        }
    } catch {
        // best-effort
    }
}

// ---------------------------------------------------------------------------
// Playback controls
// ---------------------------------------------------------------------------
const playlist = ref<Song[]>([])
const playlistIndex = ref(-1)
const isPaused = ref(false)
const controlLoading = ref(false)

const currentSong = computed(() =>
    playlistIndex.value >= 0 && playlistIndex.value < playlist.value.length
        ? playlist.value[playlistIndex.value]
        : null,
)

async function handlePrev() {
    if (!playlist.value.length) return
    controlLoading.value = true
    error.value = ''
    try {
        const data = await api.prevMusic(deviceId.value || undefined)
        if (typeof (data as { index?: number }).index === 'number') {
            playlistIndex.value = (data as { index: number }).index
        }
        isPaused.value = false
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '上一首失败'
    } finally {
        controlLoading.value = false
    }
}

async function handleNext() {
    if (!playlist.value.length) return
    controlLoading.value = true
    error.value = ''
    try {
        const data = await api.nextMusic(deviceId.value || undefined)
        if (typeof (data as { index?: number }).index === 'number') {
            playlistIndex.value = (data as { index: number }).index
        }
        isPaused.value = false
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '下一首失败'
    } finally {
        controlLoading.value = false
    }
}

async function handlePlayPause() {
    controlLoading.value = true
    error.value = ''
    try {
        if (isPaused.value) {
            await api.resumeMusic(deviceId.value || undefined)
        } else {
            await api.pauseMusic(deviceId.value || undefined)
        }
        isPaused.value = !isPaused.value
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '操作失败'
    } finally {
        controlLoading.value = false
    }
}

// ---------------------------------------------------------------------------
// Create Playlist from search/chart results
// ---------------------------------------------------------------------------
const showCreatePlaylistDialog = ref(false)
const createPlaylistLoading = ref(false)
const createPlaylistForm = ref({
    name: '',
    type: 'music',
    description: '',
})
const createPlaylistSource = ref<'search' | 'chart'>('search')

function handleCreatePlaylist(source: 'search' | 'chart') {
    createPlaylistSource.value = source

    // 预填播单名称
    if (source === 'search' && searchQuery.value) {
        createPlaylistForm.value.name = `${searchQuery.value} 的搜索结果`
        createPlaylistForm.value.description = `从搜索"${searchQuery.value}"创建的播单`
    } else if (source === 'chart' && selectedChart.value) {
        createPlaylistForm.value.name = selectedChart.value.name
        createPlaylistForm.value.description = `从排行榜"${selectedChart.value.name}"创建的播单`
    }

    showCreatePlaylistDialog.value = true
}

async function confirmCreatePlaylist() {
    if (!createPlaylistForm.value.name.trim()) {
        ElMessage.error('请输入播单名称')
        return
    }

    const songs = createPlaylistSource.value === 'search' ? searchResults.value : chartSongs.value

    if (!songs.length) {
        ElMessage.error('没有歌曲可添加')
        return
    }

    createPlaylistLoading.value = true
    try {
        // 创建播单
        const playlist = await api.createPlaylist({
            name: createPlaylistForm.value.name,
            type: createPlaylistForm.value.type,
            description: createPlaylistForm.value.description,
        })

        // 将歌曲转换为播单项
        const items: PlaylistItem[] = songs.map(song => ({
            title: song.name,
            artist: song.singer,
            album: song.meta.albumName,
            audio_id: String(song.id),
            url: '', // 留空，由动态获取
            custom_params: {
                type: 'music',
                platform: song.platform,
                song_id: song.id,
                qualities: song.qualities,
            },
            interval: song.interval,
            pic_url: song.meta.picUrl,
        }))

        // 添加歌曲到播单
        await api.addPlaylistItems(playlist.id, { items })

        ElMessage.success(`播单"${playlist.name}"创建成功，已添加 ${items.length} 首歌曲`)
        showCreatePlaylistDialog.value = false

        // 重置表单
        createPlaylistForm.value = {
            name: '',
            type: 'music',
            description: '',
        }
    } catch (error: any) {
        ElMessage.error(`创建播单失败: ${error.message}`)
    } finally {
        createPlaylistLoading.value = false
    }
}

watch(activeTab, (name) => {
    if (name === 'charts' && charts.value.length === 0) {
        loadCharts()
    }
})
</script>

<style scoped>
.charts-layout {
    display: flex;
    gap: 16px;
    margin-top: 12px;
}

.charts-list {
    flex: 0 0 280px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 600px;
    overflow-y: auto;
    padding-right: 8px;
}

.charts-list::-webkit-scrollbar {
    width: 6px;
}

.charts-list::-webkit-scrollbar-thumb {
    background: var(--color-scrollbar-thumb);
    border-radius: 3px;
}

.charts-list::-webkit-scrollbar-thumb:hover {
    background: var(--color-scrollbar-thumb-hover);
}

.chart-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: var(--color-chart-item-bg);
    border: 1px solid var(--color-chart-item-border);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.chart-item:hover {
    border-color: var(--el-color-primary);
    box-shadow: var(--color-shadow-md);
}

.chart-item--active {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
}

.chart-image {
    width: 60px;
    height: 60px;
    border-radius: 4px;
    flex-shrink: 0;
}

.chart-image-error {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-chart-image-error-bg);
    color: var(--color-chart-image-error-text);
    border-radius: 4px;
}

.chart-name {
    flex: 1;
    font-size: 13px;
    line-height: 1.5;
    color: var(--color-text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.chart-details {
    flex: 1;
    min-width: 0;
}

.image-placeholder {
    width: 100%;
    height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-chart-image-error-bg);
    color: var(--color-chart-image-error-text);
}

.player-bar {
    position: sticky;
    bottom: 16px;
}

.player-content {
    display: flex;
    align-items: center;
    gap: 24px;
}

.song-info {
    flex: 1;
    min-width: 0;
}

.song-name {
    font-size: 15px;
    font-weight: 600;
    margin-right: 8px;
}

.song-singer {
    font-size: 13px;
    color: var(--color-text-regular);
}

.player-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.clickable-row {
    cursor: pointer;
}

.clickable-row:hover {
    background-color: var(--el-fill-color-light) !important;
}

.playing-row {
    background-color: var(--el-color-primary-light-9) !important;
    cursor: pointer;
}
</style>
