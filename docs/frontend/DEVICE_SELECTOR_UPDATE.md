# 全局设备选择器更新说明

## 更新内容

### 1. 新增全局设备选择器组件
- 位置：`frontend/src/components/GlobalDeviceSelector.vue`
- 功能：
  - 固定显示在页面顶部（main区域）
  - 设备选择器靠右显示
  - 选中设备后，左侧显示设备信息：
    - 在线状态（绿色标签：在线 / 灰色标签：离线）
    - 播放状态（绿色：播放中 / 橙色：已暂停 / 灰色：未播放）
    - 硬件型号
    - IP地址
    - 停止按钮（发送停止播放指令）
      - 仅在设备正在播放或暂停时启用
      - 未播放时按钮禁用

### 2. 播放状态监控
- 自动轮询播放状态（每3秒更新一次）
- 切换设备时自动更新状态
- 点击停止按钮后立即刷新状态
- 组件卸载时自动停止轮询

### 3. 修改的页面
以下页面的设备选择器已移除，统一使用顶部全局选择器：
- `frontend/src/views/TTSControl.vue` - TTS朗读
- `frontend/src/views/VolumeControl.vue` - 音量控制
- `frontend/src/views/CommandPanel.vue` - 语音指令
- `frontend/src/views/MusicPanel.vue` - 音乐搜索
- `frontend/src/views/PlaylistManager.vue` - 播单管理
- `frontend/src/views/ConversationHistory.vue` - 对话记录

### 4. 保留设备选择器的页面
- `frontend/src/views/SchedulerManager.vue` - 定时任务
  - 原因：定时任务创建时需要为每个任务单独指定设备

### 5. 布局调整
- `frontend/src/App.vue`
  - 在 `el-main` 顶部添加 `GlobalDeviceSelector` 组件
  - 调整样式，使设备选择器固定在顶部
  - 内容区域可滚动

## 技术实现

### 全局状态管理
使用 `useDevices` composable 实现设备状态的全局共享：
- 设备列表 (`devices`)
- 当前选中设备ID (`deviceId`)
- 加载状态 (`devicesLoading`)
- 错误信息 (`devicesError`)

所有页面通过 `useDevices()` 访问同一个设备状态，确保选择的设备在所有页面保持一致。

### 播放状态获取
- API端点：`GET /api/music/status?device_id={deviceId}`
- 返回数据结构：
  ```json
  {
    "device": "设备名称(设备ID)",
    "status": {
      "data": {
        "info": "{\"status\": 0|1|2, ...}"
      }
    }
  }
  ```
- 状态码：
  - `0`: 停止/未播放
  - `1`: 播放中
  - `2`: 暂停

### 组件特性
- 自动加载设备列表
- 默认选中配置文件中的默认设备
- 支持刷新设备列表
- 实时显示选中设备的详细信息
- 实时监控播放状态（每3秒轮询）
- 智能停止按钮（根据播放状态自动启用/禁用）

## 用户体验改进
1. 统一的设备选择入口，避免在每个页面重复选择
2. 实时显示设备状态，方便用户了解设备情况
3. 实时显示播放状态，一目了然
4. 智能停止按钮，仅在需要时启用，避免误操作
5. 设备信息一目了然，包括在线状态、播放状态、型号、IP地址
