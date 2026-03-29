<template>
  <div class="user-info">
    <div class="user-avatar">
      <el-icon :size="24"><User /></el-icon>
    </div>
    <div class="user-details">
      <div class="username">{{ username }}</div>
      <div class="role">
        <el-tag :type="isAdmin ? 'danger' : 'info'" size="small">
          {{ isAdmin ? '管理员' : '普通用户' }}
        </el-tag>
      </div>
    </div>
    <el-dropdown @command="handleCommand">
      <el-icon class="more-icon"><MoreFilled /></el-icon>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="logout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { User, MoreFilled, SwitchButton } from '@element-plus/icons-vue'
import { logout } from '@/api/auth'
import { useAuth } from '@/composables/useAuth'

const { username, isAdmin } = useAuth()

const handleCommand = (command: string) => {
  if (command === 'logout') {
    logout()
  }
}
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--color-sidebar-hover);
  border-top: 1px solid var(--color-sidebar-border);
  color: var(--color-sidebar-text);
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-sidebar-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-sidebar-active);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-sidebar-active);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role {
  font-size: 12px;
}

.more-icon {
  cursor: pointer;
  font-size: 18px;
  color: var(--color-sidebar-text);
}

.more-icon:hover {
  color: var(--color-sidebar-active);
}
</style>
