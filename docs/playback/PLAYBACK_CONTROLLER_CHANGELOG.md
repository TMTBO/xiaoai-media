# 播放控制器更新日志

## 2026-04-01 - 完全移除轮询模式和配置判断

### 变更内容

1. **移除 playback_monitor 模块**
   - 删除 `backend/src/xiaoai_media/playback_monitor.py`
   - 移除所有轮询模式相关代码

2. **完全移除配置项**
   - 移除 `ENABLE_PLAYBACK_MONITOR` 配置项
   - 移除 `PLAYBACK_MONITOR_INTERVAL` 配置项
   - 移除 `PLAYBACK_MODE` 配置项
   - 移除所有 `hasattr(app_config, 'PLAYBACK_MODE')` 判断逻辑

3. **简化代码**
   - 所有播放控制逻辑直接使用 playback_controller
   - 移除条件判断，代码更简洁
   - 减少配置复杂度

4. **前端更新**
   - 移除播放监控配置界面
   - 移除播放模式选择

5. **文档更新**
   - 更新 `PLAYBACK_CONTROLLER.md`
   - 删除 `PLAYBACK_MONITOR_CONFIG.md`
   - 更新相关配置文档

### 迁移指南

播放控制器现在默认启用，无需任何配置。

1. 移除 `user_config.py` 中的以下配置（如果存在）：
   ```python
   ENABLE_PLAYBACK_MONITOR = True
   PLAYBACK_MONITOR_INTERVAL = 3.0
   PLAYBACK_MODE = "controller"
   ```

2. 重启服务

就这么简单！

---

## 2024-03-28 - 新增定时器模式

### 新功能

1. **定时器模式（Playback Controller）**
   - 新增基于定时器的播放控制方案
   - 根据音频时长自动设置定时器，在歌曲结束前触发下一曲
   - 相比轮询模式，性能提升约 30 倍

2. **SSE 状态推送**
   - 定时器模式完全支持 SSE 实时状态推送
   - 前端无需修改，透明切换

### 实现细节

#### 定时器模式

1. 播放开始时获取音频时长和当前位置
2. 计算剩余播放时间：`remaining = (duration - position) / 1000 - buffer_time`
3. 设置定时器，在剩余时间后触发下一曲
4. 暂停时取消定时器，继续时重新设置
5. 停止时取消定时器并清除状态

### 性能对比

播放一首 3 分钟的歌曲：

- **定时器模式**：只需要调用 2 次 API

### 兼容性

- 默认启用定时器模式
- 支持运行时配置更新
- SSE 状态推送完全支持

### 测试

新增测试文件：
- `backend/tests/test_playback_controller.py` - 定时器模式测试

运行测试：
```bash
cd backend
pytest tests/test_playback_controller.py -v
```

### 相关文件

#### 后端
- `backend/src/xiaoai_media/playback_controller.py` - 定时器模式实现
- `backend/src/xiaoai_media/services/playlist_service.py` - 播放服务集成
- `backend/src/xiaoai_media/api/routes/state.py` - SSE 状态推送
- `backend/src/xiaoai_media/config.py` - 配置管理

#### 前端
- `frontend/src/views/Settings.vue` - 配置页面
- `frontend/src/api/index.ts` - API 类型定义

#### 文档
- `docs/PLAYBACK_CONTROLLER.md` - 播放控制器文档
- `docs/PLAYBACK_CONTROLLER_CHANGELOG.md` - 更新日志（本文件）
