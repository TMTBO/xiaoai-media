<template>
  <el-container class="app-layout">
    <el-aside width="200px" class="aside">
      <div class="logo">🎵 XiaoAI Media</div>
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
      </el-menu>
    </el-aside>

    <el-main class="main">
      <GlobalDeviceSelector />
      <div class="main-content">
        <router-view />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import GlobalDeviceSelector from '@/components/GlobalDeviceSelector.vue'
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
.app-layout {
  height: 100vh;
}

.aside {
  background: #1d2d44;
}

.aside .logo {
  padding: 20px 16px;
  font-size: 16px;
  font-weight: bold;
  color: #ffffff;
  border-bottom: 1px solid #2e4060;
}

.aside .el-menu {
  border-right: none;
  background: #1d2d44;
  --el-menu-text-color: #c0cfe0;
  --el-menu-hover-bg-color: #2e4060;
  --el-menu-active-color: #ffffff;
}

.main {
  background: #f5f7fa;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
</style>
