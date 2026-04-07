<template>
  <el-tooltip
    :content="tooltipText"
    placement="bottom"
  >
    <el-button
      circle
      class="theme-toggle"
      @click="toggleTheme"
    >
      <el-icon>
        <Sunny v-if="themeMode === 'light'" />
        <Moon v-else-if="themeMode === 'dark'" />
        <Monitor v-else />
      </el-icon>
    </el-button>
  </el-tooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sunny, Moon, Monitor } from '@element-plus/icons-vue'
import { useTheme } from '@/composables/useTheme'

const { themeMode, toggleTheme } = useTheme()

const tooltipText = computed(() => {
  switch (themeMode.value) {
    case 'light':
      return '浅色模式（点击切换到深色）'
    case 'dark':
      return '深色模式（点击切换到跟随系统）'
    case 'auto':
      return '跟随系统（点击切换到浅色）'
    default:
      return '切换主题'
  }
})
</script>

<style scoped>
.theme-toggle {
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  transform: rotate(180deg);
}
</style>
