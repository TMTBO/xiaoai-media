# 管理员登录后立即显示"用户管理"菜单 - 修复说明

## 问题描述
管理员在登录成功后，"用户管理"菜单项不会立即显示，需要刷新页面才能看到。

## 根本原因
在 `App.vue` 中，`isAdmin` 是一个 computed 属性，它通过调用 `checkIsAdmin()` 函数来检查用户角色。该函数直接读取 `localStorage.getItem('role')`。

Vue 的响应式系统无法追踪 localStorage 的变化。当用户登录后，虽然 localStorage 被更新了，但 computed 属性不会重新计算，因为 localStorage 的变化不会触发 Vue 的响应式更新。

## 解决方案
创建一个响应式的用户状态管理 composable (`useAuth`)，使用 Vue 的 ref 来存储用户信息，而不是直接依赖 localStorage。

## 修改的文件

### 1. 新建 `frontend/src/composables/useAuth.ts`
创建响应式的用户状态管理：
- 使用 Vue ref 存储 token、username 和 role
- 提供 `setAuth()` 方法在登录时更新状态
- 提供 `clearAuth()` 方法在登出时清除状态
- 导出 computed 属性 `isAuthenticated` 和 `isAdmin` 供组件使用
- 导出普通函数供路由守卫使用

### 2. 更新 `frontend/src/views/Login.vue`
- 导入 `useAuth` composable
- 登录成功后调用 `setAuth()` 更新响应式状态，而不是直接操作 localStorage

### 3. 更新 `frontend/src/App.vue`
- 导入 `useAuth` composable
- 使用 `useAuth()` 返回的响应式 `isAdmin` 属性，而不是调用 `checkIsAdmin()` 函数

### 4. 更新 `frontend/src/components/UserInfo.vue`
- 导入 `useAuth` composable
- 使用响应式的 `username` 和 `isAdmin` 属性

### 5. 更新 `frontend/src/router/index.ts`
- 从 `@/composables/useAuth` 导入 `isAuthenticated` 和 `isAdmin` 函数
- 路由守卫现在使用响应式状态

## 工作原理

1. 应用启动时，`useAuth.ts` 中的 ref 从 localStorage 初始化
2. 用户登录时，`setAuth()` 同时更新 ref 和 localStorage
3. ref 的变化会触发所有依赖它的 computed 属性重新计算
4. `App.vue` 中的 `isAdmin` computed 属性会立即更新
5. "用户管理"菜单项会立即显示，无需刷新页面

## 测试步骤

1. 清除浏览器的 localStorage 和 cookies
2. 使用管理员账号登录（admin / admin123）
3. 验证登录成功后，"用户管理"菜单项立即显示
4. 无需刷新页面

## 技术要点

- 使用 Vue 3 的 Composition API 和响应式系统
- 模块级别的 ref 在整个应用中共享状态
- localStorage 仍然用于持久化，但不再是唯一的数据源
- 响应式状态是真实的数据源，localStorage 只是备份
