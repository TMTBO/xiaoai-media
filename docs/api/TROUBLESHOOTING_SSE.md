# SSE 功能故障排查

## 问题：页面空白

### 原因
App.vue 中使用了 Element Plus 图标但未导入。

### 解决方案
已在 App.vue 的 `<script setup>` 中添加图标导入：

```typescript
import { 
  Monitor, 
  ChatDotRound, 
  Headset, 
  Mic, 
  ChatLineRound, 
  VideoPlay, 
  List, 
  Clock, 
  Setting 
} from '@element-plus/icons-vue'
```

### 验证步骤

1. **清除浏览器缓存**
   - Chrome/Edge: Ctrl+Shift+Delete 或 Cmd+Shift+Delete
   - 或使用无痕模式

2. **硬刷新页面**
   - Chrome/Edge: Ctrl+Shift+R 或 Cmd+Shift+R
   - Firefox: Ctrl+F5 或 Cmd+Shift+R

3. **检查浏览器控制台**
   - 按 F12 打开开发者工具
   - 查看 Console 标签是否有错误
   - 查看 Network 标签确认资源加载

4. **重启前端服务**
   ```bash
   cd frontend
   # 停止当前服务 (Ctrl+C)
   npm run dev
   ```

## 常见问题

### 1. 页面空白，控制台无错误

**可能原因**: 浏览器缓存

**解决方案**:
- 硬刷新页面 (Ctrl+Shift+R)
- 清除浏览器缓存
- 使用无痕模式测试

### 2. SSE 连接失败

**检查步骤**:

1. 确认后端服务运行中
   ```bash
   curl http://localhost:8000/api/devices
   ```

2. 检查 SSE 端点
   ```bash
   curl -N http://localhost:8000/api/state/stream?device_id=xxx
   ```

3. 查看后端日志
   ```bash
   tail -f backend/logs/app.log | grep SSE
   ```

### 3. 播放器栏不显示

**检查清单**:
- [ ] 已选择设备
- [ ] 设备正在播放音乐
- [ ] SSE 连接成功（查看 Console）
- [ ] `currentSong` 有值（查看 Vue DevTools）

**调试方法**:
```javascript
// 在浏览器控制台执行
console.log(window.__VUE_DEVTOOLS_GLOBAL_HOOK__)
```

### 4. 状态不更新

**检查步骤**:

1. 查看 Network 标签中的 EventStream
2. 确认有 `state` 事件推送
3. 检查后端日志中的状态变化通知

### 5. TypeScript 编译错误

**当前已知警告**（不影响运行）:
- `MusicPanel.vue`: 未使用的参数 `column`, `event`
- `PlaylistManager.vue`: 未使用的类型导入

**解决方案**: 这些是代码质量警告，不影响功能运行。

## 验证功能正常

### 快速测试

1. 打开 `http://localhost:5173`
2. 应该看到左侧菜单和顶部设备选择器
3. 选择一个设备
4. 进入"音乐搜索"页面
5. 搜索并播放音乐
6. 播放器栏应该出现在设备选择器下方

### 详细测试

访问测试页面：
```
http://localhost:5173/test-global-state.html
```

查看：
- SSE 连接状态
- 实时状态更新
- 事件日志

## 开发者工具使用

### Chrome DevTools

1. **Console 标签**
   - 查看 JavaScript 错误
   - 查看 SSE 连接日志

2. **Network 标签**
   - 筛选 `state/stream`
   - 查看 EventStream 类型
   - 观察实时事件

3. **Vue DevTools**
   - 安装 Vue DevTools 扩展
   - 查看组件状态
   - 检查 `useGlobalState` 的返回值

## 回滚方案

如果新功能有问题，可以临时禁用播放器栏：

```vue
<!-- App.vue -->
<el-main class="main">
  <GlobalDeviceSelector />
  <!-- <GlobalPlayerBar /> --> <!-- 注释掉 -->
  <div class="main-content">
    <router-view />
  </div>
</el-main>
```

GlobalDeviceSelector 仍然会使用 SSE，但不会显示播放器栏。

## 获取帮助

如果问题仍未解决：

1. 提供浏览器控制台的完整错误信息
2. 提供后端日志中的相关错误
3. 说明复现步骤
4. 提供浏览器和操作系统版本
