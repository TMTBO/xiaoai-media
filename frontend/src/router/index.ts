import { createRouter, createWebHistory } from 'vue-router'
import DeviceList from '@/views/DeviceList.vue'
import TTSControl from '@/views/TTSControl.vue'
import VolumeControl from '@/views/VolumeControl.vue'
import CommandPanel from '@/views/CommandPanel.vue'
import ConversationHistory from '@/views/ConversationHistory.vue'
import Settings from '@/views/Settings.vue'
import MusicPanel from '@/views/MusicPanel.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/devices' },
    { path: '/devices', component: DeviceList },
    { path: '/tts', component: TTSControl },
    { path: '/volume', component: VolumeControl },
    { path: '/command', component: CommandPanel },
    { path: '/conversation', component: ConversationHistory },
    { path: '/music', component: MusicPanel },
    { path: '/settings', component: Settings },
  ],
})

export default router
