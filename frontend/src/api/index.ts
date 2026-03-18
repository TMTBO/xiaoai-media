import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

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
  MI_PASS_TOKEN: string
  MI_DID: string
  MI_REGION: string
  MUSIC_API_BASE_URL: string
  MUSIC_DEFAULT_PLATFORM: string
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
  interval: number
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

export const api = {
  // Devices
  listDevices: (refresh = false) =>
    http.get<{ devices: Device[] }>('/devices', { params: refresh ? { refresh: true } : undefined }).then(r => r.data),

  // TTS
  textToSpeech: (text: string, deviceId?: string) =>
    http.post('/tts', { text, device_id: deviceId }).then(r => r.data),

  // Volume
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

  // Music: Smart voice command & announce
  voiceCommand: (text: string, deviceId?: string) =>
    http.post('/music/voice-command', { text, device_id: deviceId }).then(r => r.data),
  announceSearch: (query: string, count: number, deviceId?: string) =>
    http.post('/music/announce-search', { query, count, device_id: deviceId }).then(r => r.data),

  // Conversation
  getConversation: (deviceId?: string) =>
    http.get('/command/conversation', { params: { device_id: deviceId } }).then(r => r.data),
}
