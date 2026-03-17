import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export interface Device {
  deviceID: string
  name: string
  model: string
  [key: string]: unknown
}

export interface Config {
  MI_USER: string
  MI_PASS: string
  MI_PASS_TOKEN: string
  MI_DID: string
  MI_REGION: string
}

export const api = {
  // Devices
  listDevices: () => http.get<{ devices: Device[] }>('/devices').then(r => r.data),

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
}
