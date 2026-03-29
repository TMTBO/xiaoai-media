# 前端开发文档

XiaoAI Media 前端相关的开发文档。

## 📚 文档列表

### UI/UX 改进
- **[DEVICE_SELECTOR_UPDATE.md](DEVICE_SELECTOR_UPDATE.md)** - 全局设备选择器更新
  - 全局设备选择器组件
  - 播放状态监控
  - 设备信息展示
  - 停止按钮功能

- **[LAYOUT_FIX.md](LAYOUT_FIX.md)** - 页面布局一致性修复
  - 布局问题分析
  - 修复方案
  - 页面布局规范

## 🎨 前端技术栈

- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型安全
- Vite - 快速构建工具
- Element Plus - UI 组件库
- Vue Router - 路由管理

## 📱 功能页面

### 核心功能
- **设备列表** (`DeviceList.vue`) - 查看和管理小爱音箱设备
- **播单管理** (`PlaylistManager.vue`) - 创建和管理播放列表
- **音乐搜索** (`MusicPanel.vue`) - 搜索和播放音乐
- **定时任务** (`SchedulerManager.vue`) - 创建和管理定时任务

### 控制功能
- **TTS 朗读** (`TTSControl.vue`) - 文字转语音播报
- **音量控制** (`VolumeControl.vue`) - 调节设备音量
- **语音指令** (`CommandPanel.vue`) - 执行自定义语音命令

### 监控功能
- **对话记录** (`ConversationHistory.vue`) - 查看对话历史
- **全局设备选择器** (`GlobalDeviceSelector.vue`) - 统一设备选择和状态监控

### 配置功能
- **设置** (`Settings.vue`) - 系统配置管理

## 🏗️ 项目结构

```
frontend/
├── src/
│   ├── App.vue              # 主应用组件
│   ├── main.ts              # 应用入口
│   ├── api/                 # API 客户端
│   │   └── client.ts        # HTTP 客户端封装
│   ├── components/          # 可复用组件
│   │   └── GlobalDeviceSelector.vue
│   ├── composables/         # 组合式函数
│   │   └── useDevices.ts    # 设备状态管理
│   ├── router/              # 路由配置
│   │   └── index.ts
│   └── views/               # 页面组件
│       ├── DeviceList.vue
│       ├── PlaylistManager.vue
│       ├── MusicPanel.vue
│       ├── SchedulerManager.vue
│       ├── TTSControl.vue
│       ├── VolumeControl.vue
│       ├── CommandPanel.vue
│       ├── ConversationHistory.vue
│       └── Settings.vue
├── public/                  # 静态资源
├── index.html               # HTML 模板
├── package.json             # 依赖配置
├── tsconfig.json            # TypeScript 配置
└── vite.config.ts           # Vite 配置
```

## 🎯 开发规范

### 页面布局规范

为保持页面布局一致性，请遵循以下规范：

1. **不要在页面容器上设置 padding**
   - `App.vue` 的 `.main-content` 已提供统一的 padding

2. **第一个元素不要设置 margin-top**
   - 避免额外的顶部留白

3. **元素之间的间距使用 margin-top 或 margin-bottom**
   - 推荐使用 `margin-top: 16px` 或 `margin-bottom: 16px`

4. **可以使用 max-width 和 margin: 0 auto 实现居中布局**
   - 适用于需要限制最大宽度的页面

详见：[页面布局规范](LAYOUT_FIX.md)

### 组件开发规范

1. **使用 Composition API**
   - 优先使用 `<script setup>` 语法
   - 使用 composables 共享逻辑

2. **类型安全**
   - 为 props 和 emits 定义类型
   - 使用 TypeScript 接口定义数据结构

3. **组件命名**
   - 使用 PascalCase 命名组件文件
   - 组件名称应清晰表达功能

4. **样式管理**
   - 使用 scoped 样式避免污染
   - 遵循 Element Plus 的设计规范

## 🔧 开发命令

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🌐 API 集成

前端通过 `src/api/client.ts` 与后端 API 通信：

```typescript
import { api } from '@/api/client'

// 获取设备列表
const devices = await api.get('/api/devices')

// 播放音乐
await api.post('/api/music/play', {
  song_name: '告白气球',
  device_id: 'xxx'
})
```

## 🔗 相关文档

- [API 参考](../api/README.md) - 后端 API 文档
- [项目结构](../STRUCTURE.md) - 整体项目结构
- [开发环境](../config/DEV_ENVIRONMENT.md) - 开发环境配置

---

**最后更新**：2026-03-28
