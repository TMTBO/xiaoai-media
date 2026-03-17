import { createRouter, createWebHistory } from 'vue-router'
import DeviceList from '@/views/DeviceList.vue'
import TTSControl from '@/views/TTSControl.vue'
import VolumeControl from '@/views/VolumeControl.vue'
import CommandPanel from '@/views/CommandPanel.vue'
import Settings from '@/views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/devices' },
    { path: '/devices', component: DeviceList },
    { path: '/tts', component: TTSControl },
    { path: '/volume', component: VolumeControl },
    { path: '/command', component: CommandPanel },
    { path: '/settings', component: Settings },
  ],
})

export default router
