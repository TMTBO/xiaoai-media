<template>
  <!-- 登录页面：全屏显示 -->
  <div v-if="isLoginPage" class="login-layout">
    <router-view />
  </div>

  <!-- 主应用：带侧边栏布局 -->
  <el-container v-else class="app-layout">
    <el-aside width="200px" class="aside">
      <div class="logo">
        <img src="/logo.svg" alt="XiaoAI Media Logo" />
        <span>XiaoAI Media</span>
        <ThemeToggle />
      </div>
      <el-menu :default-active="$route.path" router>
        <el-menu-item index="/devices">
          <el-icon>
            <Monitor />
          </el-icon>
          <span>设备列表</span>
        </el-menu-item>
        <el-menu-item index="/tts">
          <el-icon>
            <ChatDotRound />
          </el-icon>
          <span>TTS 朗读</span>
        </el-menu-item>
        <el-menu-item index="/volume">
          <el-icon>
            <Headset />
          </el-icon>
          <span>音量控制</span>
        </el-menu-item>
        <el-menu-item index="/command">
          <el-icon>
            <Mic />
          </el-icon>
          <span>语音指令</span>
        </el-menu-item>
        <el-menu-item index="/conversation">
          <el-icon>
            <ChatLineRound />
          </el-icon>
          <span>对话记录</span>
        </el-menu-item>
        <el-menu-item index="/music">
          <el-icon>
            <VideoPlay />
          </el-icon>
          <span>音乐搜索</span>
        </el-menu-item>
        <el-menu-item index="/playlists">
          <el-icon>
            <List />
          </el-icon>
          <span>播单管理</span>
        </el-menu-item>
        <el-menu-item index="/scheduler">
          <el-icon>
            <Clock />
          </el-icon>
          <span>定时任务</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon>
            <Setting />
          </el-icon>
          <span>配置管理</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/users">
          <el-icon>
            <UserFilled />
          </el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
      <UserInfo />
    </el-aside>

    <el-main class="main">
      <GlobalDeviceSelector />
      <GlobalPlayerBar />
      <div class="main-content">
        <router-view />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  Monitor, 
  ChatDotRound, 
  Headset, 
  Mic, 
  ChatLineRound, 
  VideoPlay, 
  List, 
  Clock, 
  Setting,
  UserFilled
} from '@element-plus/icons-vue'
import GlobalDeviceSelector from '@/components/GlobalDeviceSelector.vue'
import GlobalPlayerBar from '@/components/GlobalPlayerBar.vue'
import UserInfo from '@/components/UserInfo.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const { isAdmin } = useAuth()

const isLoginPage = computed(() => route.path === '/login')
</script>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>

<style scoped>
.login-layout {
  width: 100%;
  height: 100vh;
}

.app-layout {
  height: 100vh;
}

.aside {
  background: var(--color-sidebar-bg);
  display: flex;
  flex-direction: column;
}

.aside .logo {
  padding: 20px 16px;
  font-size: 16px;
  font-weight: bold;
  color: var(--color-sidebar-active);
  border-bottom: 1px solid var(--color-sidebar-border);
  display: flex;
  align-items: center;
  gap: 10px;
}

.aside .logo img {
  width: 32px;
  height: 32px;
}

.aside .el-menu {
  border-right: none;
  background: var(--color-sidebar-bg);
  --el-menu-text-color: var(--color-sidebar-text);
  --el-menu-hover-bg-color: var(--color-sidebar-hover);
  --el-menu-active-color: var(--color-sidebar-active);
  flex: 1;
}

.main {
  background: var(--color-bg-secondary);
  padding: 0;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--color-bg-primary);
}
</style>
