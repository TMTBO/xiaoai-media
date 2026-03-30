# 对话监听功能指南

自动监听音箱对话，拦截播放指令，通过本服务获取音乐 URL 并播放。

---

## 📚 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [支持的指令](#支持的指令)
- [技术实现](#技术实现)
- [故障排查](#故障排查)

---

## 功能概述

### 问题描述

当用户直接对音箱说话时（例如："小爱同学，播放周杰伦的晴天"），这个指令是由小爱音箱自己处理的，不会经过你的服务。

### 解决方案

参考 [xiaomusic](https://github.com/hanxi/xiaomusic) 项目的实现，通过**持续监听对话记录**来拦截播放指令。

### 核心机制

1. **后台轮询** - 每 2 秒轮询一次所有音箱的对话记录
2. **指令识别** - 检测到新的播放指令（如"播放周杰伦的晴天"）
3. **自动搜索** - 调用音乐搜索服务查找歌曲
4. **获取 URL** - 通过 `play_music` 接口获取音乐 URL
5. **播放音乐** - 在音箱上播放获取到的 URL

---

## 快速开始

### 1. 配置

在 `user_config.py` 文件中添加（默认已启用）：

```python
# 启用对话监听
ENABLE_CONVERSATION_POLLING = True

# 轮询间隔（秒）
CONVERSATION_POLL_INTERVAL = 2.0

# 音乐服务地址（必须配置）
MUSIC_API_BASE_URL = "http://localhost:5050"

# 默认音乐平台
MUSIC_DEFAULT_PLATFORM = "tx"
```

### 2. 启动服务

```bash
cd backend
python run.py
```

启动后会看到日志：

```
INFO xiaoai_media.api.main — 对话监听已启用
INFO xiaoai_media.conversation — 对话轮询器已启动 (轮询间隔: 2.0秒)
```

### 3. 测试

对音箱说：

```
小爱同学，播放周杰伦的晴天
```

服务日志会显示：

```
INFO xiaoai_media.conversation — 检测到新对话 (设备 xxx): 播放周杰伦的晴天
INFO xiaoai_media.command_handler — 检测到播放指令: 周杰伦的晴天
INFO xiaoai_media.command_handler — 搜索音乐: query=周杰伦的晴天 platform=tx
INFO xiaoai_media.command_handler — 找到歌曲: 周杰伦 - 晴天 (平台: tx, ID: xxx)
INFO xiaoai_media.command_handler — 已同步播放列表到设备 xxx: 20 首歌曲
INFO xiaoai_media.command_handler — 正在获取歌曲 URL: 周杰伦 - 晴天
INFO xiaoai_media.command_handler — 获取到播放 URL (音质=320k): http://...
INFO xiaoai_media.command_handler — 正在播放 (设备 xxx): 第 1/20 首 - 晴天
INFO xiaoai_media.command_handler — 播放成功: 周杰伦 - 晴天
```

---

## 配置说明

### 基础配置

```python
# user_config.py

# 启用对话监听
ENABLE_CONVERSATION_POLLING = True

# 轮询间隔（秒）
CONVERSATION_POLL_INTERVAL = 2.0

# 音乐服务地址
MUSIC_API_BASE_URL = "http://localhost:5050"

# 默认音乐平台
MUSIC_DEFAULT_PLATFORM = "tx"
```

### 高级配置

#### 调整轮询间隔

如果觉得响应太慢，可以缩短轮询间隔：

```python
CONVERSATION_POLL_INTERVAL = 1.0  # 1秒轮询一次（更快但更耗资源）
```

#### 禁用对话监听

如果只想通过 Web 界面控制，可以禁用：

```python
ENABLE_CONVERSATION_POLLING = False
```

---

## 支持的指令

### ✅ 会被拦截的指令

- "播放周杰伦的晴天"
- "播放晴天"
- "播放歌曲晴天"
- "打开周杰伦的歌"
- "播放稻香"

### ❌ 不会被拦截的指令

这些指令包含控制关键词，会被过滤掉：

- "播放音量" (包含"音量")
- "播放暂停" (包含"暂停")
- "播放继续" (包含"继续")
- "播放停止" (包含"停止")
- "播放下一首" (包含"下一首")
- "播放上一首" (包含"上一首")

---

## 技术实现

### 核心文件

1. **`backend/src/xiaoai_media/conversation.py`**
   - `ConversationPoller` 类 - 对话轮询器
   - 持续监听所有设备的对话记录
   - 检测新对话并触发回调

2. **`backend/src/xiaoai_media/command_handler.py`**
   - `CommandHandler` 类 - 命令处理器
   - 解析播放指令
   - 搜索音乐并获取 URL
   - 调用播放接口

3. **`backend/src/xiaoai_media/client.py`**
   - 添加 `get_latest_ask()` 方法
   - 从音箱获取对话记录

4. **`backend/src/xiaoai_media/api/main.py`**
   - 集成对话轮询器
   - 在应用启动时自动启动轮询

### 工作流程

```
1. 用户对音箱说话
   ↓
2. 小爱音箱记录对话
   ↓
3. ConversationPoller 轮询检测到新对话
   ↓
4. CommandHandler 解析指令
   ↓
5. 如果是播放指令：
   a. 调用音乐搜索 API
   b. 获取搜索结果（20首歌）
   c. 同步播放列表到服务端
   d. 调用 play_music 获取第一首歌的 URL
   e. 在音箱上播放
```

### 与 xiaomusic 的对比

| 功能 | xiaomusic | 本项目 |
|------|-----------|--------|
| 对话监听 | ✅ | ✅ |
| 自动搜索播放 | ✅ | ✅ |
| 播放列表管理 | ✅ | ✅ |
| 音质选择 | ✅ | ✅ |
| 多设备支持 | ✅ | ✅ |

---

## 故障排查

### Q: 没有检测到对话？

A: 检查以下几点：
1. 配置是否启用 (`ENABLE_CONVERSATION_POLLING = True`)
2. 小米账号是否正确配置
3. 查看启动日志是否有错误
4. 确认音箱在线并可以正常使用

### Q: 检测到对话但没有播放？

A: 检查以下几点：
1. 音乐服务是否运行 (`MUSIC_API_BASE_URL` 可访问)
2. 搜索是否有结果（查看日志）
3. 查看错误日志了解具体原因
4. 确认音箱可以正常播放音乐

### Q: 播放了错误的歌曲？

A: 建议：
- 说话时包含歌手名，如"播放周杰伦的晴天"
- 检查搜索结果是否正确（查看日志）
- 调整音乐平台设置

### Q: 响应延迟太大？

A: 可能原因：
- 轮询间隔设置太长
- 网络延迟
- 音乐服务响应慢

解决方法：
- 缩短轮询间隔（如 1.0 秒）
- 检查网络连接
- 优化音乐服务性能

---

## 注意事项

1. **音乐服务必须运行** - 确保 `MUSIC_API_BASE_URL` 指向的服务可用
2. **轮询间隔** - 不建议设置太短（< 1秒），避免频繁请求小米 API
3. **首次启动** - 只会处理启动后的新对话，不会处理历史对话
4. **网络延迟** - 从检测到播放可能有 2-5 秒延迟（取决于轮询间隔和网络速度）

---

## 相关文档

- [对话监听快速开始](QUICK_START.md) - 英文快速开始指南
- [对话监听 README](README.md) - 功能总览
- [API 文档](../api/README.md) - API 参考

---

**最后更新**: 2026-03-30
