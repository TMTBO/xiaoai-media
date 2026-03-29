import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

// 标记是否正在跳转登录页
let isRedirecting = false

// 请求拦截器 - 添加token
http.interceptors.request.use(
  (config) => {
    // 如果正在跳转登录页，取消所有新请求
    if (isRedirecting) {
      return Promise.reject(new axios.Cancel('正在跳转登录页，取消请求'))
    }

    // 如果在登录页面且不是登录请求，取消请求
    if (window.location.pathname === '/login' && !config.url?.includes('/auth/login')) {
      return Promise.reject(new axios.Cancel('登录页面不允许发起非登录请求'))
    }

    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理401错误
http.interceptors.response.use(
  (response) => {
    // 成功响应时重置跳转标志
    isRedirecting = false
    return response
  },
  (error) => {
    // 如果是取消的请求，直接返回
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401) {
      // 避免重复跳转
      if (!isRedirecting && window.location.pathname !== '/login') {
        isRedirecting = true

        // 清除token和用户信息
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('role')

        // 跳转到登录页
        window.location.href = '/login'

        // 延迟重置标志，确保跳转完成
        setTimeout(() => {
          isRedirecting = false
        }, 1000)
      }
    }
    return Promise.reject(error)
  }
)

export interface Device {
  deviceID: string   // MiNA UUID — used for ubus commands (TTS, volume, etc.)
  did?: string       // MiIO numeric device ID — used for miot_action
  miotDID?: string   // same as did, from MiNA response
  name: string
  model: string      // e.g. "xiaomi.wifispeaker.oh2p" (from MiIO)
  hardware: string   // e.g. "OH2P" (from MiNA)
  isOnline?: boolean
  localip?: string
  [key: string]: unknown
}

export interface Config {
  MI_USER: string
  MI_PASS: string
  MI_DID: string
  MI_REGION: string
  MUSIC_API_BASE_URL: string
  MUSIC_DEFAULT_PLATFORM: string
  SERVER_BASE_URL: string
  ENABLE_CONVERSATION_POLLING: boolean
  CONVERSATION_POLL_INTERVAL: number
  ENABLE_PLAYBACK_MONITOR: boolean
  PLAYBACK_MONITOR_INTERVAL: number
  ENABLE_WAKE_WORD_FILTER: boolean
  WAKE_WORDS: string[]
  LOG_LEVEL: string
  VERBOSE_PLAYBACK_LOG: boolean
}

export interface SongQuality {
  type: string     // e.g. '128k', '320k', 'flac'
  format: string   // e.g. 'mp3', 'flac'
  size: number | string
}

export interface SongMeta {
  albumName: string
  picUrl: string
  songId: number | string
}

export interface Song {
  id: string
  name: string
  singer: string
  platform: string
  qualities: SongQuality[]
  interval: number | string  // 可能是秒数或时长字符串 "04:32"
  meta: SongMeta
}

export interface Chart {
  id: string
  name: string
  picUrl?: string
  updateTime?: string
  totalNum?: number
}

export interface PlaylistState {
  device_id: string | null
  songs: Song[]
  current: number
  total: number
}

export interface PlaylistItem {
  title: string          // 歌曲名
  artist: string         // 艺术家
  album: string          // 专辑名
  audio_id: string       // 音频ID
  url?: string           // 音频URL
  custom_params: Record<string, any>
}

export interface PlaylistIndex {
  id: string
  name: string
  type: string
  description: string
  voice_keywords: string[]
  item_count: number
  created_at: string
  updated_at: string
  play_mode: string      // 播放模式：loop, single, random
  current_index: number  // 当前播放索引
}

export interface Playlist {
  id: string
  name: string
  type: string
  description: string
  items: PlaylistItem[]
  voice_keywords: string[]
  created_at: string
  updated_at: string
  play_mode: string      // 播放模式：loop, single, random
  current_index: number  // 当前播放索引
}

export interface CreatePlaylistRequest {
  name: string
  type?: string
  description?: string
  voice_keywords?: string[]
}

export interface UpdatePlaylistRequest {
  name?: string
  type?: string
  description?: string
  voice_keywords?: string[]
  play_mode?: string
  current_index?: number
}

export interface AddItemRequest {
  items: PlaylistItem[]
}

export interface PlayPlaylistRequest {
  device_id?: string
  start_index?: number
  announce?: boolean
}

export interface ImportFromDirectoryRequest {
  directory?: string
  files?: string[]
  recursive?: boolean
  file_extensions?: string[]
}

export interface ImportResult {
  imported: number
  skipped: number
  total_scanned: number
  skipped_files?: string[]
  playlist_total_items: number
}

export interface DirectoryInfo {
  path: string
  name: string
  is_accessible?: boolean
}

export interface FileInfo {
  path: string
  name: string
  size: number
}

export interface DirectoriesResponse {
  directories: DirectoryInfo[]
  is_docker: boolean
  message: string
}

export interface BrowseDirectoryResponse {
  current_path: string
  parent_path: string | null
  directories: DirectoryInfo[]
  files?: FileInfo[]
  total: number
}

export const api = {
  // Devices
  listDevices: (refresh = false) =>
    http.get<{ devices: Device[] }>('/devices', { params: refresh ? { refresh: true } : undefined }).then(r => r.data),

  // TTS
  textToSpeech: (text: string, deviceId?: string) =>
    http.post('/tts', { text, device_id: deviceId }).then(r => r.data),

  // Volume
  getVolume: (deviceId?: string) =>
    http.get('/volume', { params: { device_id: deviceId } }).then(r => r.data),
  setVolume: (volume: number, deviceId?: string) =>
    http.post('/volume', { volume, device_id: deviceId }).then(r => r.data),

  // Command
  sendCommand: (text: string, deviceId?: string) =>
    http.post('/command', { text, device_id: deviceId }).then(r => r.data),

  // Config
  getConfig: () => http.get<Config>('/config').then(r => r.data),
  updateConfig: (data: Partial<Config>) => http.put('/config', data).then(r => r.data),

  // Music: Search & Charts
  searchMusic: (query: string, platform?: string, page?: number, limit?: number) =>
    http.get('/music/search', { params: { query, platform, page, limit } }).then(r => r.data),
  getRanks: (platform?: string) =>
    http.get('/music/ranks', { params: { platform } }).then(r => r.data),
  getRankSongs: (rankId: string, platform?: string, page?: number, limit?: number) =>
    http.get(`/music/rank/${encodeURIComponent(rankId)}`, { params: { platform, page, limit } }).then(r => r.data),

  // Music: Playback control
  syncPlaylist: (songs: Song[], deviceId?: string) =>
    http.post('/music/playlist', { songs, device_id: deviceId }).then(r => r.data),
  playMusic: (index: number, deviceId?: string) =>
    http.post('/music/play', { index, device_id: deviceId }).then(r => r.data),
  nextMusic: (deviceId?: string) =>
    http.post('/music/next', { device_id: deviceId }).then(r => r.data),
  prevMusic: (deviceId?: string) =>
    http.post('/music/prev', { device_id: deviceId }).then(r => r.data),
  pauseMusic: (deviceId?: string) =>
    http.post('/music/pause', { device_id: deviceId }).then(r => r.data),
  resumeMusic: (deviceId?: string) =>
    http.post('/music/resume', { device_id: deviceId }).then(r => r.data),
  getPlaylist: (deviceId?: string) =>
    http.get<PlaylistState>('/music/playlist', { params: { device_id: deviceId } }).then(r => r.data),
  getPlayerStatus: (deviceId?: string) =>
    http.get('/music/status', { params: { device_id: deviceId } }).then(r => r.data),

  // Music: Smart voice command & announce
  voiceCommand: (text: string, deviceId?: string) =>
    http.post('/music/voice-command', { text, device_id: deviceId }).then(r => r.data),
  announceSearch: (query: string, count: number, deviceId?: string) =>
    http.post('/music/announce-search', { query, count, device_id: deviceId }).then(r => r.data),

  // Conversation
  getConversation: (deviceId?: string) =>
    http.get('/command/conversation', { params: { device_id: deviceId } }).then(r => r.data),

  // Playlists
  listPlaylists: () =>
    http.get<{ playlists: PlaylistIndex[], total: number }>('/playlists').then(r => r.data),
  createPlaylist: (data: CreatePlaylistRequest) =>
    http.post<Playlist>('/playlists', data).then(r => r.data),
  getPlaylistById: (playlistId: string) =>
    http.get<Playlist>(`/playlists/${playlistId}`).then(r => r.data),
  updatePlaylist: (playlistId: string, data: UpdatePlaylistRequest) =>
    http.put<Playlist>(`/playlists/${playlistId}`, data).then(r => r.data),
  deletePlaylist: (playlistId: string) =>
    http.delete(`/playlists/${playlistId}`).then(r => r.data),
  addPlaylistItems: (playlistId: string, data: AddItemRequest) =>
    http.post(`/playlists/${playlistId}/items`, data).then(r => r.data),
  deletePlaylistItem: (playlistId: string, itemIndex: number) =>
    http.delete(`/playlists/${playlistId}/items/${itemIndex}`).then(r => r.data),
  playPlaylist: (playlistId: string, data: PlayPlaylistRequest) =>
    http.post(`/playlists/${playlistId}/play`, data).then(r => r.data),
  continuePlaylist: (playlistId: string, deviceId?: string, announce?: boolean) =>
    http.post(`/playlists/${playlistId}/continue`, { device_id: deviceId, announce }).then(r => r.data),
  stopPlaylist: (playlistId: string, deviceId?: string) =>
    http.post(`/playlists/${playlistId}/stop`, null, { params: { device_id: deviceId } }).then(r => r.data),
  setPlayMode: (playlistId: string, playMode: string) =>
    http.post(`/playlists/${playlistId}/play-mode`, { play_mode: playMode }).then(r => r.data),
  playNextInPlaylist: (playlistId: string, deviceId?: string) =>
    http.post(`/playlists/${playlistId}/next`, null, { params: { device_id: deviceId } }).then(r => r.data),

  // Playlist: Batch import
  getAvailableDirectories: () =>
    http.get<DirectoriesResponse>('/playlists/directories').then(r => r.data),
  browseDirectory: (path?: string) =>
    http.get<BrowseDirectoryResponse>('/playlists/directories/browse', { params: path ? { path } : undefined }).then(r => r.data),
  importFromDirectory: (playlistId: string, data: ImportFromDirectoryRequest) =>
    http.post<ImportResult>(`/playlists/${playlistId}/import`, data).then(r => r.data),
}
