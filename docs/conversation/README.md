# 对话监听功能说明

## 功能概述

对话监听功能会持续监听小爱音箱的对话记录，当检测到播放指令时，自动拦截并通过本服务获取音乐 URL 进行播放。

## 工作原理

参考 [xiaomusic](https://github.com/hanxi/xiaomusic) 的实现：

1. **对话轮询器 (ConversationPoller)**
   - 后台持续轮询所有音箱的对话记录
   - 检测新的对话（基于时间戳）
   - 将新对话传递给命令处理器

2. **命令处理器 (CommandHandler)**
   - 解析语音指令，识别播放命令
   - 支持的命令格式：
     - "播放周杰伦的晴天"
     - "播放晴天"
     - "播放歌曲晴天"
     - "打开周杰伦的歌"
   - 自动搜索音乐并获取播放 URL
   - 同步播放列表到服务端
   - 调用音箱播放音乐

3. **工作流程**
   ```
   用户对音箱说话 → 对话记录生成 → 轮询器检测到新对话 
   → 命令处理器解析指令 → 搜索音乐 → 获取 URL → 播放
   ```

## 配置选项

在 `.env` 文件中添加以下配置：

```bash
# 启用对话监听（默认: true）
ENABLE_CONVERSATION_POLLING=true

# 轮询间隔，单位秒（默认: 2.0）
CONVERSATION_POLL_INTERVAL=2.0
```

## 使用方式

1. 确保配置文件中启用了对话监听
2. 启动服务后，对话轮询器会自动在后台运行
3. 直接对音箱说："小爱同学，播放周杰伦的晴天"
4. 服务会自动：
   - 检测到播放指令
   - 搜索"周杰伦的晴天"
   - 获取音乐 URL
   - 在音箱上播放

## 技术细节

### 新增模块

- `backend/src/xiaoai_media/conversation.py` - 对话轮询器
- `backend/src/xiaoai_media/command_handler.py` - 命令处理器

### 修改的文件

- `backend/src/xiaoai_media/client.py` - 添加 `get_latest_ask()` 方法
- `backend/src/xiaoai_media/api/main.py` - 集成对话轮询器
- `backend/src/xiaoai_media/config.py` - 添加配置选项

### 命令识别逻辑

命令处理器会过滤掉非音乐播放的指令，例如：
- "播放音量" - 不会触发
- "播放暂停" - 不会触发
- "播放下一首" - 不会触发
- "播放周杰伦的晴天" - 会触发音乐搜索和播放

## 注意事项

1. 对话轮询需要持续运行，会定期调用小米 API
2. 轮询间隔不建议设置太短（建议 2 秒以上），避免频繁请求
3. 首次启动时会初始化时间戳，只处理启动后的新对话
4. 如果音乐搜索服务 (MUSIC_API_BASE_URL) 不可用，播放会失败

## 日志查看

启动服务后，可以在日志中看到：

```
INFO xiaoai_media.conversation — ConversationPoller started (interval: 2.0s)
INFO xiaoai_media.conversation — New conversation on device xxx: 播放周杰伦的晴天
INFO xiaoai_media.command_handler — Play command detected: 周杰伦的晴天
INFO xiaoai_media.command_handler — Found song: 周杰伦 - 晴天 (platform: tx)
```
