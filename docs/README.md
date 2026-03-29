# XiaoAI Media 文档中心

<div align="center">
  <img src="logo.svg" alt="XiaoAI Media Logo" width="120" />
</div>

欢迎使用 XiaoAI Media！这里是完整的文档索引。

---

## 📚 快速导航

### 🚀 新手入门
- [项目概览](OVERVIEW.md) - 项目整体介绍和架构
- [入门指南](GETTING_STARTED.md) - 快速了解和开始使用
- [快速开始](../QUICK_START.md) - 5 分钟快速上手
- [完整 README](../README.md) - 项目完整介绍
- [用户使用指南](USER_GUIDE.md) - 完整使用指南
- [功能特性详解](FEATURES.md) - 所有功能的详细说明
- [Docker 部署](deployment/DOCKER_GUIDE.md) - Docker 完整指南

### 📖 核心功能
- [播放列表](playlist/README.md) - 播放列表管理
- [批量导入](playlist/README_BATCH_IMPORT.md) - 批量导入音频文件
- [定时任务](scheduler/README.md) - 定时播放和提醒
- [对话监听](conversation/README.md) - 自动拦截播放指令
- [TTS 语音](tts/README.md) - 文字转语音播报
- [音乐播放](playback/README.md) - 音乐搜索和播放

### ⚙️ 配置和部署
- [配置指南](config/README.md) - 配置文件详解
- [用户配置](config/USER_CONFIG_GUIDE.md) - 用户配置详细说明
- [数据存储](config/DATA_STORAGE.md) - 数据目录说明
- [开发环境](config/DEV_ENVIRONMENT.md) - 本地开发配置

### 💻 开发文档
- [API 参考](api/README.md) - REST API 完整文档
- [项目结构](STRUCTURE.md) - 代码结构说明
- [服务层架构](../backend/src/xiaoai_media/services/README.md) - 服务层设计
- [前端开发](frontend/README.md) - 前端开发文档
- [重构文档](refactor/README.md) - 架构重构说明

### 🔄 升级和迁移
- [迁移指南](migration/README.md) - 版本升级说明
- [更新日志](../CHANGELOG.md) - 版本更新记录

---

## 📖 文档分类

### 配置相关 (config/)
- **README.md** - 配置总览
- **USER_CONFIG_GUIDE.md** - 用户配置详细指南
- **DEV_ENVIRONMENT.md** - 开发环境配置
- **DATA_STORAGE.md** - 数据存储说明
- **CONFIG_FAQ.md** - 配置常见问题
- **GET_PASSTOKEN_GUIDE.md** - Token 获取指南

### 部署相关 (deployment/)
- **DOCKER_GUIDE.md** - Docker 部署完整指南
- **DOCKER_QUICK_START.md** - Docker 快速开始
- **DOCKER_HUB_CI.md** - Docker Hub CI/CD
- **DOCKER_VOLUMES_GUIDE.md** - Docker 数据卷指南

### 功能相关
- **playlist/** - 播放列表功能文档
  - 播放列表管理、批量导入、存储优化
- **scheduler/** - 定时任务功能文档
  - 定时播放、定时提醒、定时命令
- **conversation/** - 对话监听功能文档
  - 自动拦截、指令识别、智能响应
- **playback/** - 音乐播放功能文档
  - 音乐搜索、播放控制、故障排查
- **tts/** - TTS 语音功能文档
  - 文字转语音、语音播报

### 开发相关
- **api/** - API 接口文档
  - REST API 参考、SSE 实时推送
- **frontend/** - 前端开发文档
  - 组件开发、布局规范、UI/UX 改进
- **refactor/** - 代码重构文档
  - 架构重构、服务层设计、最佳实践
- **migration/** - 迁移和升级指南
  - 版本升级、数据迁移、配置迁移

### 元文档 (meta/)
- 文档组织、清理记录、维护说明

---

## 🔍 按场景查找

### 我想开始使用
1. [快速开始](../QUICK_START.md) - 5 分钟上手
2. [Docker 部署](deployment/DOCKER_GUIDE.md) - 生产环境部署
3. [配置指南](config/README.md) - 配置说明

### 我想开发调试
1. [开发环境配置](config/DEV_ENVIRONMENT.md) - 本地开发环境
2. [项目结构](STRUCTURE.md) - 代码结构
3. [API 文档](api/README.md) - API 接口
4. [服务层架构](../backend/src/xiaoai_media/services/README.md) - 服务层设计
5. [前端开发](frontend/README.md) - 前端开发规范

### 我遇到了问题
1. [配置 FAQ](config/CONFIG_FAQ.md) - 配置常见问题
2. [播放问题排查](playback/PLAYBACK_TROUBLESHOOTING.md) - 播放故障排查
3. [对话监听问题](conversation/README.md) - 对话监听问题
4. [GitHub Issues](https://github.com/tmtbo/xiaoai-media/issues) - 提交问题

### 我想了解功能
1. [播放列表管理](playlist/README.md) - 播放列表功能
2. [批量导入](playlist/README_BATCH_IMPORT.md) - 批量导入音频
3. [定时任务](scheduler/README.md) - 定时播放和提醒
4. [对话监听](conversation/README.md) - 自动拦截功能
5. [TTS 语音](tts/README.md) - 语音播报

### 我想升级版本
1. [迁移指南](migration/README.md) - 版本升级说明
2. [更新日志](../CHANGELOG.md) - 版本更新记录
3. [播单存储迁移](playlist/PLAYLIST_STORAGE_REFACTOR.md) - v1.0 存储优化

---

## 📝 文档维护

### 文档原则
- 保持简洁，避免重复
- 用户文档和开发文档分离
- 及时更新过时内容
- 中英文文档并存

### 文档结构
```
docs/
├── README.md              # 文档中心（本文件）
├── INDEX.md               # 文档索引表格
├── STRUCTURE.md           # 项目结构说明
├── CONTRIBUTING.md        # 贡献指南
├── api/                   # API 文档
├── config/                # 配置文档
├── deployment/            # 部署文档
├── frontend/              # 前端开发文档
├── playlist/              # 播放列表文档
├── scheduler/             # 定时任务文档
├── conversation/          # 对话监听文档
├── playback/              # 音乐播放文档
├── tts/                   # TTS 文档
├── migration/             # 迁移指南
├── refactor/              # 重构文档
├── bugfix/                # Bug 修复记录
└── meta/                  # 元文档（文档维护记录）
```

### 贡献文档
如果你想为文档做贡献，请查看：[贡献指南](CONTRIBUTING.md)

---

## 🔗 外部资源

- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
- [问题反馈](https://github.com/tmtbo/xiaoai-media/issues)
- [更新日志](../CHANGELOG.md)
- [MiService Fork](https://github.com/yihong0618/MiService)

---

**最后更新**：2026-03-28
