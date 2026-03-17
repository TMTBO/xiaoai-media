<template>
    <div class="music-panel">
        <!-- Device selector -->
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

        <!-- Smart voice command -->
        <el-card style="margin-top: 16px">
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
                        <span style="font-size: 13px; color: #606266">共 {{ searchResults.length }} 首歌曲</span>
                        <el-button size="small" :loading="askPlayLoading" @click="handleAskPlay">
                            <el-icon style="margin-right: 4px">
                                <Bell />
                            </el-icon>询问音箱并播放全部
                        </el-button>
                    </div>

                    <el-table :data="searchResults" v-loading="searchLoading" style="width: 100%; margin-top: 8px"
                        empty-text="暂无结果，请输入关键词搜索">
                        <el-table-column prop="name" label="歌名" min-width="160" show-overflow-tooltip />
                        <el-table-column prop="singer" label="歌手" min-width="120" show-overflow-tooltip />
                        <el-table-column prop="albumName" label="专辑" min-width="140" show-overflow-tooltip />
                        <el-table-column label="操作" width="90" fixed="right">
                            <template #default="scope">
                                <el-button type="primary" size="small" :loading="playingIdx === scope.$index"
                                    @click="playFromSearch(scope.$index)">
                                    播放
                                </el-button>
                            </template>
                        </el-table-column>
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
                    <div v-else-if="charts.length" class="charts-grid">
                        <el-card v-for="chart in charts" :key="chart.id" class="chart-card"
                            :class="{ 'chart-card--active': selectedChart?.id === chart.id }" shadow="hover"
                            @click="loadChartSongs(chart)">
                            <el-image :src="chart.picUrl" style="width: 100%; height: 110px" fit="cover" loading="lazy">
                                <template #error>
                                    <div class="image-placeholder">
                                        <el-icon size="36">
                                            <VideoPlay />
                                        </el-icon>
                                    </div>
                                </template>
                            </el-image>
                            <div class="chart-name">{{ chart.name }}</div>
                        </el-card>
                    </div>
                    <el-empty v-else description="点击刷新按钮加载排行榜" />

                    <template v-if="selectedChart">
                        <el-divider content-position="left">{{ selectedChart.name }}</el-divider>
                        <el-table :data="chartSongs" v-loading="chartSongsLoading" style="width: 100%"
                            empty-text="暂无歌曲">
                            <el-table-column type="index" label="#" width="50" />
                            <el-table-column prop="name" label="歌名" min-width="160" show-overflow-tooltip />
                            <el-table-column prop="singer" label="歌手" min-width="120" show-overflow-tooltip />
                            <el-table-column label="操作" width="90" fixed="right">
                                <template #default="scope">
                                    <el-button type="primary" size="small" :loading="playingIdx === -(scope.$index + 1)"
                                        @click="playFromChart(scope.$index)">
                                        播放
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </template>
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
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
    Refresh,
    Search,
    CaretLeft,
    CaretRight,
    VideoPlay,
    VideoPause,
    Mic,
    Bell,
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { api, type Song, type Chart } from '@/api'
import { useDevices } from '@/composables/useDevices'

const { devices, devicesLoading, loadDevices, deviceId } = useDevices()
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
    return {
        id: String(raw.id ?? raw.songId ?? ''),
        name: String(raw.name ?? ''),
        singer: String(raw.singer ?? ''),
        platform,
        albumName: raw.albumName ? String(raw.albumName) : undefined,
        picUrl: raw.picUrl ? String(raw.picUrl) : undefined,
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
        await api.playMusic(searchResults.value, index, deviceId.value || undefined)
        playlist.value = [...searchResults.value]
        playlistIndex.value = index
        isPaused.value = false
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '播放失败'
    } finally {
        playingIdx.value = -999
    }
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
    // Toggle: click same chart again to collapse
    if (selectedChart.value?.id === chart.id) {
        selectedChart.value = null
        chartSongs.value = []
        return
    }
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
        await api.playMusic(chartSongs.value, index, deviceId.value || undefined)
        playlist.value = [...chartSongs.value]
        playlistIndex.value = index
        isPaused.value = false
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '播放失败'
    } finally {
        playingIdx.value = -999
    }
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
        await api.playMusic(searchResults.value, 0, deviceId.value || undefined)
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

watch(activeTab, (name) => {
    if (name === 'charts' && charts.value.length === 0) {
        loadCharts()
    }
})
</script>

<style scoped>
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
    margin-top: 12px;
}

.chart-card {
    cursor: pointer;
    transition: transform 0.15s;
}

.chart-card:hover {
    transform: translateY(-2px);
}

.chart-card--active {
    box-shadow: 0 0 0 2px var(--el-color-primary);
}

.chart-name {
    font-size: 13px;
    text-align: center;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 4px;
}

.image-placeholder {
    width: 100%;
    height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f7fa;
    color: #c0c4cc;
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
    color: #606266;
}

.player-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
