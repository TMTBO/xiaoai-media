# 配置系统文档

XiaoAI Media 配置系统的完整文档。

## 📚 文档列表

### 快速开始
- **[QUICK_CONFIG.md](QUICK_CONFIG.md)** - 5 分钟快速配置指南

### 配置管理
- **[CONFIG_API.md](CONFIG_API.md)** - 配置管理 API 文档
  - 通过管理后台动态修改配置
  - 支持所有配置项
  - 无需重启服务

### 用户指南
- **[USER_CONFIG_GUIDE.md](USER_CONFIG_GUIDE.md)** - 用户配置详细指南
  - 所有配置项的详细说明
  - 配置示例和最佳实践
  - 高级配置技巧

### 参考文档
- **[CONFIG_CHEATSHEET.md](CONFIG_CHEATSHEET.md)** - 配置项速查表
  - 快速查找配置项
  - 默认值和示例
  - 常用配置组合

### 问题排查
- **[CONFIG_FAQ.md](CONFIG_FAQ.md)** - 配置常见问题
  - 常见配置错误
  - 问题诊断步骤
  - 解决方案

### 技术文档
- **[USER_CONFIG_IMPLEMENTATION.md](USER_CONFIG_IMPLEMENTATION.md)** - 配置系统实现说明
- **[USER_CONFIG_SUMMARY.md](USER_CONFIG_SUMMARY.md)** - 配置系统摘要
- **[CONFIG_ANSWERS.md](CONFIG_ANSWERS.md)** - 配置问答集

## 🎯 配置项总览

### 必填配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `MI_USER` | 小米账号 | `"your_account"` |
| `MI_PASS` | 小米密码 | `"password"` |
| `MI_PASS_TOKEN` | 小米令牌 | `"V1:..."` |

### 服务配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MUSIC_API_BASE_URL` | 音乐搜索服务地址 | `"http://localhost:5050"` |
| `MUSIC_DEFAULT_PLATFORM` | 默认音乐平台 | `"tx"` |
| `SERVER_BASE_URL` | 本服务地址 | `"http://localhost:8000"` |

### 功能配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ENABLE_CONVERSATION_POLLING` | 启用对话监听 | `true` |
| `CONVERSATION_POLL_INTERVAL` | 轮询间隔（秒） | `2.0` |
| `ENABLE_WAKE_WORD_FILTER` | 启用唤醒词过滤 | `true` |

### 日志配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LOG_LEVEL` | 日志级别 | `"INFO"` |
| `VERBOSE_PLAYBACK_LOG` | 详细播放日志 | `false` |

### 存储配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PLAYLIST_STORAGE_DIR` | 播单存储目录 | `"~/.xiaoai-media"` |

## 🚀 快速配置流程

### 1. 复制配置模板
```bash
cp user_config_template.py user_config.py
```

### 2. 修改配置
编辑 `user_config.py`，填入必填配置：
```python
MI_USER = "your_xiaomi_account"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"  # 使用局域网 IP
SERVER_BASE_URL = "http://192.168.1.100:8000"     # 使用局域网 IP
```

### 3. 启动服务
```bash
make dev
```

### 4. 管理后台配置
访问 `http://localhost:8000`，在设置页面可以动态修改配置。

## ⚠️ 重要提示

### 网络配置
- `MUSIC_API_BASE_URL` 和 `SERVER_BASE_URL` **必须使用局域网 IP**
- 不能使用 `localhost` 或 `127.0.0.1`
- 小爱音箱需要通过网络访问这些服务

### 敏感信息
- 不要将 `user_config.py` 提交到版本控制
- 密码和令牌会在管理后台中被掩码显示
- 支持使用 `MI_PASS_TOKEN` 代替 `MI_PASS`

## 🔗 相关文档

- [API 参考](../api/API_REFERENCE.md) - 查看配置 API 接口
- [快速开始](../README.md) - 项目快速开始
- [问题排查](CONFIG_FAQ.md) - 配置问题解决
