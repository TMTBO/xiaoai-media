# 播放控制器更新日志

## 2026-03-30 - 新增定时器模式

### 新增功能

1. **播放控制器（Playback Controller）**
   - 新增基于定时器的播放监控方案
   - 根据音频时长自动设置定时器，在歌曲结束前触发下一曲
   - 相比轮询模式，性能提升约 30 倍

2. **配置选项**
   - 新增 `PLAYBACK_MODE` 配置项，支持两种模式：
     - `monitor`（轮询模式）：定期检查播放状态，兼容性好
     - `controller`（定时器模式）：根据时长设置定时器，高效节能
   - 前端配置页面新增"监控模式"选择

3. **自动模式切换**
   - 修改配置后自动重启相应的监控/控制服务
   - 支持运行时动态切换模式

### 技术实现

1. **核心文件**
   - `backend/src/xiaoai_media/playback_controller.py` - 播放控制器实现
   - `backend/src/xiaoai_media/config.py` - 新增 PLAYBACK_MODE 配置
   - `backend/src/xiaoai_media/api/main.py` - 启动时根据配置选择模式
   - `backend/src/xiaoai_media/services/playlist_service.py` - 播放时设置定时器
   - `backend/src/xiaoai_media/api/routes/state.py` - SSE 支持两种模式

2. **前端更新**
   - `frontend/src/views/Settings.vue` - 新增监控模式选择
   - `frontend/src/api/index.ts` - 新增 PLAYBACK_MODE 类型定义

3. **测试文件**
   - `backend/tests/test_playback_controller.py` - 控制器单元测试

4. **文档**
   - `docs/PLAYBACK_CONTROLLER.md` - 详细使用说明
   - `user_config.example.py` - 配置示例

### 工作流程

#### 定时器模式

1. 播放开始时，获取音频时长和当前位置
2. 计算剩余播放时间：`remaining = (duration - position) / 1000 - buffer_time`
3. 设置定时器，在剩余时间后触发下一曲
4. 暂停时取消定时器，继续时重新设置定时器
5. 停止时取消定时器并清除状态

#### 轮询模式（原有）

1. 定期（如每 3 秒）调用 API 检查播放状态
2. 检测 position 回退（从接近结尾跳回开头）
3. 立即播放下一曲

### 性能对比

播放一首 3 分钟的歌曲：

- **轮询模式**（3 秒间隔）：需要调用 60 次 API
- **定时器模式**：只需要调用 2 次 API

性能提升：**约 30 倍**

### 兼容性

- 完全向后兼容，默认使用轮询模式
- 支持运行时切换模式，无需重启服务
- SSE 状态推送同时支持两种模式

### 使用建议

1. **推荐使用定时器模式**：
   - 音频文件有准确的时长信息
   - 追求高性能和低资源消耗
   - 播放列表较长

2. **推荐使用轮询模式**：
   - 音频时长信息不准确
   - 需要检测手动停止等异常情况
   - 追求兼容性和稳定性

### 已知限制

1. 定时器模式依赖准确的音频时长信息
2. 定时器模式无法检测手动停止等异常情况
3. 缓冲时间（默认 1 秒）可能需要根据实际情况调整

### 未来计划

1. 支持混合模式：定时器为主，定期轮询为辅
2. 自动检测音频时长准确性，动态切换模式
3. 支持更多的播放事件（如快进、快退等）
4. 优化缓冲时间的自适应调整

### 迁移指南

#### 从轮询模式迁移到定时器模式

1. 在 `user_config.py` 中添加：
   ```python
   PLAYBACK_MODE = "controller"
   ```

2. 或在前端配置页面：
   - 打开"配置管理"
   - 找到"播放监控"部分
   - 选择"定时器模式"
   - 点击"保存配置"

3. 配置会自动重新加载，无需重启服务

#### 回退到轮询模式

1. 修改配置：
   ```python
   PLAYBACK_MODE = "monitor"
   ```

2. 或在前端选择"轮询模式"并保存

### 测试

运行测试验证功能：

```bash
cd backend
pytest tests/test_playback_controller.py -v
```

### 贡献者

- 实现：AI Assistant
- 需求：用户反馈

### 相关链接

- [播放控制器文档](./PLAYBACK_CONTROLLER.md)
- [配置示例](../user_config.example.py)
- [测试文件](../backend/tests/test_playback_controller.py)
