# 入门指南

快速了解 XiaoAI Media 并开始使用。

---

## 🎯 XiaoAI Media 是什么？

XiaoAI Media 是一个功能强大的小米/小爱音箱控制系统，提供：

- 🌐 **Web 管理界面** - 现代化的管理界面
- 🔌 **REST API** - 完整的编程接口
- 🎵 **音乐播放** - 多平台音乐搜索和播放
- 📋 **播放列表** - 自定义播放列表管理
- ⏰ **定时任务** - 定时播放和提醒
- 🎤 **语音命令** - 智能语音命令解析
- 🎧 **对话监听** - 自动拦截播放指令

---

## 🚀 5 分钟快速开始

### 步骤 1：部署服务

```bash
# 使用 Docker Compose（推荐）
mkdir -p ./data
cp user_config_template.py ./data/user_config.py
vim ./data/user_config.py  # 填入小米账号
docker-compose up -d
```

### 步骤 2：访问管理界面

浏览器打开：http://localhost:8000

### 步骤 3：查看设备

进入"设备列表"页面，查看你的小爱音箱设备。

### 步骤 4：开始使用

- 播放音乐：进入"音乐搜索"页面
- 创建播放列表：进入"播单管理"页面
- 设置定时任务：进入"定时任务"页面

---

## 📖 主要功能

### 1. 播放列表

创建自定义播放列表，通过语音命令快速播放：

```bash
# 创建播放列表
1. 进入"播单管理"页面
2. 点击"创建播单"
3. 填写播单信息和语音关键词

# 语音播放
对音箱说："小爱，播放音乐播单"
```

详见：[播放列表文档](playlist/README.md)

### 2. 批量导入

从目录批量导入音频文件：

```bash
1. 进入"播单管理"页面
2. 点击"批量导入"
3. 选择音频文件目录
4. 自动创建播放列表
```

支持自然排序（第1章、第2章、第10章）。

详见：[批量导入指南](playlist/README_BATCH_IMPORT.md)

### 3. 定时任务

设置定时播放和提醒：

```bash
# 定时播放音乐
1. 进入"定时任务"页面
2. 创建任务，选择"播放音乐"
3. 设置 Cron 表达式：0 7 * * *（每天早上7点）
4. 填写歌曲信息

# 延迟提醒
1. 创建任务，选择"提醒"
2. 设置延迟：30 分钟
3. 填写提醒内容
```

详见：[定时任务文档](scheduler/README.md)

### 4. 音乐搜索

搜索和播放音乐：

```bash
1. 进入"音乐搜索"页面
2. 输入歌曲名或歌手名
3. 选择音乐平台
4. 点击播放
```

支持 QQ 音乐、网易云音乐等多个平台。

### 5. 语音命令

执行自定义语音命令：

```bash
1. 进入"语音指令"页面
2. 输入命令（如："播放周杰伦的歌"）
3. 点击执行
```

系统会自动解析命令并执行相应操作。

---

## 🔧 配置说明

### 基础配置

```python
# user_config.py

# 小米账号（必填）
MI_USER = "your_account@example.com"
MI_PASS = "your_password"

# 本服务地址（必填，使用局域网 IP）
SERVER_BASE_URL = "http://192.168.1.100:8000"

# 默认设备（可选）
MI_DID = "123456789"
```

### 音乐服务配置

```python
# music_provider.py

# 音乐 API 地址
MUSIC_API_BASE_URL = "http://localhost:5050"
```

推荐使用 [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi) 作为音乐服务。

详见：[配置指南](config/README.md)

---

## 💡 使用技巧

### 技巧 1：语音关键词

为播放列表设置语音关键词，快速播放：

```
播单名称：我的音乐
语音关键词：音乐、歌曲

语音命令："小爱，播放音乐"
```

### 技巧 2：批量导入有声书

导入有声书章节，自动按章节排序：

```
目录结构：
├── 第1章.mp3
├── 第2章.mp3
├── 第10章.mp3
└── 第20章.mp3

导入后自动排序：第1章 → 第2章 → 第10章 → 第20章
```

### 技巧 3：定时播放

设置每天早上的起床音乐：

```
任务类型：播放播放列表
Cron 表达式：0 7 * * *
播放列表：我的音乐
```

### 技巧 4：自定义音频源

在 `user_config.py` 中实现 `get_audio_url()` 函数，集成自己的音乐服务：

```python
def get_audio_url(audio_id: str, custom_params: dict = None) -> str:
    """从你的音乐服务获取 URL"""
    return f"http://your-music-api.com/song/{audio_id}"
```

---

## 🆘 遇到问题？

### 常见问题

1. **无法连接设备**
   - 检查小米账号和密码
   - 确认设备在线

2. **播放失败**
   - 检查 `SERVER_BASE_URL` 是否为局域网 IP
   - 确认音乐 API 正常

3. **语音命令不响应**
   - 检查对话监听是否启用
   - 查看对话历史记录

### 获取帮助

- [用户使用指南](USER_GUIDE.md) - 完整使用指南
- [配置 FAQ](config/CONFIG_FAQ.md) - 配置常见问题
- [播放问题排查](playback/PLAYBACK_TROUBLESHOOTING.md) - 播放故障排查
- [GitHub Issues](https://github.com/tmtbo/xiaoai-media/issues) - 提交问题

---

## 📚 下一步

### 深入了解
- [功能特性详解](FEATURES.md) - 了解所有功能
- [用户使用指南](USER_GUIDE.md) - 完整使用指南
- [API 文档](api/README.md) - API 编程接口

### 高级功能
- [对话监听](conversation/README.md) - 自动拦截播放指令
- [自定义音频源](config/USER_CONFIG_GUIDE.md) - 集成自己的音乐服务
- [开发扩展](STRUCTURE.md) - 了解项目架构

---

**最后更新**：2026-03-28
