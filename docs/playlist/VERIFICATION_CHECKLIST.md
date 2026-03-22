# 自动播放下一曲功能验证清单

## 后端验证

### 1. 配置文件
- [x] `backend/src/xiaoai_media/config.py` - 添加配置项定义
- [x] `backend/src/xiaoai_media/services/config_service.py` - 添加到允许列表和返回值
- [x] `backend/src/xiaoai_media/api/routes/config.py` - 添加到 API 模型

### 2. 核心功能
- [x] `backend/src/xiaoai_media/playback_monitor.py` - 播放监控器实现
- [x] `backend/src/xiaoai_media/services/playlist_service.py` - 添加 random 导入
- [x] `backend/src/xiaoai_media/api/main.py` - 集成监控器启动/停止

### 3. 用户配置
- [x] `user_config.py` - 添加配置项
- [x] `user_config_template.py` - 添加配置项和说明
- [x] `user_config.example.py` - 添加配置项

## 前端验证

### 1. 类型定义
- [x] `frontend/src/api/index.ts` - Config 接口添加字段

### 2. 配置页面
- [x] `frontend/src/views/Settings.vue` - 添加配置表单项
  - [x] 启用监控开关
  - [x] 轮询间隔输入框
  - [x] 表单默认值

## 文档验证

- [x] `docs/playlist/AUTO_PLAY_NEXT.md` - 功能说明
- [x] `docs/playlist/PLAYBACK_MONITOR_CONFIG.md` - 配置说明
- [x] `docs/playlist/AUTO_PLAY_IMPLEMENTATION.md` - 实现总结

## 功能测试清单

### 测试前准备
1. [ ] 确保后端服务正常运行
2. [ ] 确保前端服务正常运行
3. [ ] 确保有可用的小爱音箱设备
4. [ ] 确保已创建测试播单（至少包含 3 首歌）

### 配置测试
1. [ ] 访问管理后台配置页面
2. [ ] 验证"播放监控"配置区域显示正常
3. [ ] 修改配置并保存
4. [ ] 验证配置保存成功
5. [ ] 刷新页面，验证配置已持久化

### 功能测试

#### 测试 1：列表循环模式
1. [ ] 设置播单播放模式为 "loop"
2. [ ] 启用播放监控
3. [ ] 播放播单第一首
4. [ ] 等待第一首播放完成
5. [ ] 验证自动播放第二首
6. [ ] 等待播放到最后一首
7. [ ] 验证自动回到第一首

#### 测试 2：单曲循环模式
1. [ ] 设置播单播放模式为 "single"
2. [ ] 播放播单第一首
3. [ ] 等待第一首播放完成
4. [ ] 验证重复播放第一首

#### 测试 3：随机播放模式
1. [ ] 设置播单播放模式为 "random"
2. [ ] 播放播单
3. [ ] 等待当前歌曲播放完成
4. [ ] 验证随机播放另一首（可能重复）

#### 测试 4：禁用播放监控
1. [ ] 禁用播放监控
2. [ ] 播放播单
3. [ ] 等待当前歌曲播放完成
4. [ ] 验证不会自动播放下一首

#### 测试 5：轮询间隔
1. [ ] 设置轮询间隔为 5 秒
2. [ ] 播放播单
3. [ ] 观察切歌延迟（应该在 5 秒内）

### 日志验证
1. [ ] 查看后端日志，验证监控器启动消息
2. [ ] 查看播放状态检查日志
3. [ ] 查看自动播放触发日志
4. [ ] 验证无异常错误

## 已知问题

1. 用户主动暂停可能触发自动播放（需要进一步优化）
2. 播放状态检测依赖于小爱音箱的状态 API

## 验证结果

- 后端配置：✅ 完成
- 前端配置：✅ 完成
- 文档：✅ 完成
- 功能测试：⏳ 待测试

## 下一步

1. 进行完整的功能测试
2. 根据测试结果优化实现
3. 收集用户反馈
4. 持续改进
