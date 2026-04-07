import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, isAdmin } from '@/composables/useAuth'
import DeviceList from '@/views/DeviceList.vue'
import TTSControl from '@/views/TTSControl.vue'
import VolumeControl from '@/views/VolumeControl.vue'
import CommandPanel from '@/views/CommandPanel.vue'
import ConversationHistory from '@/views/ConversationHistory.vue'
import Settings from '@/views/SettingsPage.vue'
import MusicPanel from '@/views/MusicPanel.vue'
import PlaylistManager from '@/views/PlaylistManager.vue'
import SchedulerManager from '@/views/SchedulerManager.vue'
import Login from '@/views/LoginPage.vue'
import UserManagement from '@/views/UserManagement.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login, meta: { public: true } },
    { path: '/', redirect: '/devices' },
    { path: '/devices', component: DeviceList },
    { path: '/tts', component: TTSControl },
    { path: '/volume', component: VolumeControl },
    { path: '/command', component: CommandPanel },
    { path: '/conversation', component: ConversationHistory },
    { path: '/music', component: MusicPanel },
    { path: '/playlists', component: PlaylistManager },
    { path: '/scheduler', component: SchedulerManager },
    { path: '/settings', component: Settings },
    { path: '/users', component: UserManagement, meta: { requiresAdmin: true } },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authenticated = isAuthenticated()
  const admin = isAdmin()

  // 公开页面直接放行
  if (to.meta.public) {
    if (authenticated && to.path === '/login') {
      // 已登录用户访问登录页，重定向到首页
      next('/devices')
    } else {
      next()
    }
    return
  }

  // 需要登录的页面
  if (!authenticated) {
    next('/login')
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && !admin) {
    next('/devices')
    return
  }

  next()
})

export default router

