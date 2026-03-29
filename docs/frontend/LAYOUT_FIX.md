# 页面布局一致性修复

## 问题描述
定时任务、播单管理、音乐搜索页面的顶部留白与其他页面不一致，导致视觉效果不统一。

## 问题原因
1. `App.vue` 的 `.main-content` 已经设置了 `padding: 20px`
2. 部分页面（定时任务、播单管理、音乐搜索）有自己的容器 div，并额外设置了 `padding: 20px`
3. 部分页面的第一个元素设置了 `margin-top: 16px`
4. 这导致了双重 padding 和额外的顶部留白

## 修复内容

### 1. 移除容器的 padding
- `frontend/src/views/SchedulerManager.vue`
  - 移除 `.scheduler-manager` 的 `padding: 20px`
  - 保留 `max-width` 和 `margin: 0 auto` 用于居中布局

- `frontend/src/views/PlaylistManager.vue`
  - 移除 `.playlist-manager` 的 `padding: 20px`
  - 保留 `max-width` 和 `margin: 0 auto` 用于居中布局

### 2. 移除第一个元素的 margin-top
- `frontend/src/views/MusicPanel.vue`
  - 移除第一个 `el-card` 的 `style="margin-top: 16px"`

- `frontend/src/views/PlaylistManager.vue`
  - 移除第一个 `el-card` 的 `style="margin-top: 16px"`

## 修复后的效果
所有页面的顶部留白现在保持一致，都由 `App.vue` 的 `.main-content` 统一控制（`padding: 20px`）。

## 页面布局规范
为了保持一致性，所有页面应遵循以下规范：

1. **不要在页面容器上设置 padding**
   - `App.vue` 的 `.main-content` 已经提供了统一的 padding

2. **第一个元素不要设置 margin-top**
   - 避免额外的顶部留白

3. **元素之间的间距使用 margin-top 或 margin-bottom**
   - 推荐使用 `margin-top: 16px` 或 `margin-bottom: 16px`

4. **可以使用 max-width 和 margin: 0 auto 实现居中布局**
   - 适用于需要限制最大宽度的页面

## 示例

### 正确的页面结构
```vue
<template>
  <div class="page-container">
    <el-card>
      <!-- 第一个元素，无 margin-top -->
    </el-card>
    
    <el-card style="margin-top: 16px">
      <!-- 后续元素，使用 margin-top 分隔 -->
    </el-card>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  /* 不要设置 padding */
}
</style>
```

### 错误的页面结构
```vue
<template>
  <div class="page-container">
    <el-card style="margin-top: 16px">
      <!-- ❌ 第一个元素不应该有 margin-top -->
    </el-card>
  </div>
</template>

<style scoped>
.page-container {
  padding: 20px; /* ❌ 不要设置 padding，会与 App.vue 的 padding 重复 */
  max-width: 1400px;
  margin: 0 auto;
}
</style>
```
