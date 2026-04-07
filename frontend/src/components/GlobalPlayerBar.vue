<template>
  <transition name="slide-down">
    <div
      v-if="shouldShow"
      class="global-player-bar"
    >
      <div class="player-content">
        <!-- 封面 -->
        <div class="cover">
          <img 
            v-if="displaySong?.cover" 
            :src="displaySong.cover" 
            :alt="displaySong.name"
            @error="onCoverError"
          >
          <el-icon
            v-else
            class="default-cover"
          >
            <Headset />
          </el-icon>
        </div>
        
        <!-- 歌曲信息 -->
        <div class="song-info">
          <div class="song-name">
            {{ displaySong?.name || '未知歌曲' }}
          </div>
          <div class="song-meta">
            <span class="artist">{{ displaySong?.singer || '未知歌手' }}</span>
            <span
              v-if="displaySong?.album"
              class="separator"
            >·</span>
            <span
              v-if="displaySong?.album"
              class="album"
            >{{ displaySong.album }}</span>
          </div>
        </div>
        
        <!-- 播放控制 -->
        <div class="controls">
          <el-button 
            circle
            :icon="CaretLeft" 
            :disabled="!playlist || playlist.total <= 1"
            title="上一曲"
            class="control-btn prev-btn"
            @click="playPrev"
          />
          <el-button 
            circle
            class="control-btn play-btn"
            :title="isPlaying ? '暂停' : '播放'"
            :disabled="!state || state.play_status === 'unknown'"
            @click="togglePlay"
          >
            <el-icon :size="24">
              <VideoPause v-if="isPlaying" />
              <VideoPlay v-else />
            </el-icon>
          </el-button>
          <el-button 
            circle
            :icon="CaretRight" 
            :disabled="!playlist || playlist.total <= 1"
            title="下一曲"
            class="control-btn next-btn"
            @click="playNext"
          />
        </div>
        
        <!-- 播放进度 -->
        <div class="progress-section">
          <span class="time">{{ formatTime(state?.position || 0) }}</span>
          <el-slider 
            v-model="progressValue" 
            :show-tooltip="false"
            class="progress-slider"
            disabled
          />
          <span class="time">{{ formatTime(state?.duration || 0) }}</span>
        </div>
        
        <!-- 播放列表信息 -->
        <div class="playlist-info">
          <el-icon><List /></el-icon>
          <span v-if="playlist">{{ playlist.current + 1 }} / {{ playlist.total }}</span>
          <span v-else>-</span>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  VideoPlay, 
  VideoPause, 
  CaretLeft, 
  CaretRight, 
  List,
  Headset
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalState } from '@/composables/useGlobalState'
import { useDevices } from '@/composables/useDevices'
import { api } from '@/api'

const { deviceId } = useDevices()
const { state, isPlaying, currentSong, playlist, progress } = useGlobalState(deviceId)

// 播放器栏始终显示
const shouldShow = computed(() => true)

// 显示的歌曲信息（如果没有完整信息，显示未播放状态）
const displaySong = computed(() => {
  if (currentSong.value && currentSong.value.name) {
    return currentSong.value
  }
  // 如果没有歌曲信息但正在播放，显示基本信息
  if (state.value && state.value.media_type === 3 && state.value.duration > 0) {
    return {
      name: '正在播放',
      singer: state.value.audio_id ? `ID: ${state.value.audio_id.slice(0, 12)}...` : '未知',
      album: '',
      cover: '',
      audio_id: state.value.audio_id
    }
  }
  // 没有播放时显示未播放状态
  return {
    name: '未播放',
    singer: '选择音乐开始播放',
    album: '',
    cover: '',
    audio_id: ''
  }
})

const progressValue = computed(() => progress.value)

function formatTime(ms: number): string {
  if (!ms) return '0:00'
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

function onCoverError(e: Event): void {
  // 封面加载失败时隐藏图片
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

async function togglePlay(): Promise<void> {
  try {
    if (isPlaying.value) {
      // 暂停播放
      await api.pauseMusic(deviceId.value || undefined)
    } else {
      // 恢复播放
      // 直接使用 resumeMusic，不需要重新加载播放列表
      await api.resumeMusic(deviceId.value || undefined)
    }
  } catch (e: unknown) {
    ElMessage.error(e instanceof Error ? e.message : '操作失败')
  }
}

async function playNext(): Promise<void> {
  try {
    // 如果有播放列表，使用播放列表的下一曲（支持循环模式）
    if (playlist.value && playlist.value.id) {
      await api.playNextInPlaylist(playlist.value.id, deviceId.value || undefined)
      ElMessage.success('正在播放下一曲')
    } else {
      // 没有播放列表，使用旧的播放器逻辑
      await api.nextMusic(deviceId.value || undefined)
      ElMessage.success('正在播放下一曲')
    }
  } catch (e: unknown) {
    ElMessage.error(e instanceof Error ? e.message : '播放失败')
  }
}

async function playPrev(): Promise<void> {
  try {
    // 上一曲功能暂时只支持旧的播放器逻辑
    await api.prevMusic(deviceId.value || undefined)
    ElMessage.success('正在播放上一曲')
  } catch (e: unknown) {
    ElMessage.error(e instanceof Error ? e.message : '播放失败')
  }
}
</script>

<style scoped>
.global-player-bar {
  background: var(--color-player-bg);
  color: var(--color-text-primary);
  padding: 12px 20px;
  border-bottom: 1px solid var(--color-border-light);
  box-shadow: var(--color-shadow-sm);
}

.player-content {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 1400px;
  margin: 0 auto;
}

.cover {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--color-player-control-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-cover {
  font-size: 24px;
  color: var(--color-text-secondary);
}

.song-info {
  flex: 1;
  min-width: 0;
  margin-right: 16px;
}

.song-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text-primary);
}

.song-meta {
  font-size: 13px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.separator {
  margin: 0 6px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.control-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  background: var(--color-player-control-bg);
  color: var(--color-text-regular);
  font-size: 18px;
  transition: all 0.2s;
}

.control-btn:hover:not(.is-disabled) {
  background: var(--color-player-control-hover-bg);
  color: var(--color-primary);
  transform: scale(1.05);
}

.control-btn.is-disabled {
  background: var(--color-button-disabled-bg);
  color: var(--color-button-disabled-text);
  cursor: not-allowed;
}

.play-btn {
  width: 42px;
  height: 42px;
  background: var(--color-primary);
  color: var(--color-text-white);
  font-size: 20px;
}

.play-btn:hover {
  background: var(--color-primary-light);
  transform: scale(1.08);
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  max-width: 400px;
}

.time {
  font-size: 12px;
  color: var(--color-text-secondary);
  min-width: 40px;
  text-align: center;
}

.progress-slider {
  flex: 1;
}

.progress-slider :deep(.el-slider__runway) {
  background: var(--color-player-progress-bg);
}

.progress-slider :deep(.el-slider__bar) {
  background: var(--color-player-progress-bar);
}

.progress-slider :deep(.el-slider__button) {
  border-color: var(--color-player-progress-bar);
}

.playlist-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
  padding: 6px 12px;
  background: var(--color-player-control-bg);
  border-radius: 16px;
}

.close-btn {
  color: var(--color-text-secondary);
  font-size: 16px;
  flex-shrink: 0;
  margin-left: 8px;
}

.close-btn:hover {
  color: var(--color-text-regular);
}

/* 动画效果 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
