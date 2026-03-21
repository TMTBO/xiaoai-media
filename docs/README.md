# XiaoAI Media 文档中心

欢迎使用 XiaoAI Media！这里是完整的文档索引。

---

## 📚 快速导航

### 新手入门
- [快速开始](../QUICK_START.md) - 5 分钟快速上手
- [完整 README](../README.md) - 项目完整介绍

### 核心功能
- [配置指南](config/README.md) - 配置文件详解
- [播放列表](playlist/README.md) - 播放列表管理
- [对话监听](conversation/README.md) - 对话监听功能
- [TTS 语音](tts/README.md) - 文字转语音
- [音乐播放](playback/README.md) - 音乐播放功能

### 部署运维
- [Docker 部署](deployment/DOCKER_GUIDE.md) - Docker 完整指南
- [开发环境](config/DEV_ENVIRONMENT.md) - 本地开发配置

### 开发文档
- [API 参考](api/README.md) - REST API 文档
- [迁移指南](migration/README.md) - 版本升级说明
- [重构文档](refactor/README.md) - 代码重构文档 ✨
- [重构总结](../REFACTOR_SUMMARY.md) - 架构重构总览 ✨

---

## 📖 文档分类

### 配置相关 (config/)
- **README.md** - 配置总览
- **DEV_ENVIRONMENT.md** - 开发环境配置
- **DATA_STORAGE.md** - 数据存储说明
- **USER_CONFIG_GUIDE.md** - 用户配置指南

### 部署相关 (deployment/)
- **DOCKER_GUIDE.md** - Docker 部署完整指南
- **DOCKER_QUICK_START.md** - Docker 快速开始
- **DOCKER_HUB_CI.md** - Docker Hub CI/CD

### 功能相关
- **playlist/** - 播放列表功能文档
- **conversation/** - 对话监听功能文档
- **playback/** - 音乐播放功能文档
- **tts/** - TTS 语音功能文档

### 开发相关
- **api/** - API 接口文档
- **migration/** - 迁移和升级指南
- **refactor/** - 代码重构文档 ✨

---

## 🔍 按场景查找

### 我想开始使用
1. [快速开始](../QUICK_START.md)
2. [配置指南](config/README.md)
3. [Docker 部署](deployment/DOCKER_GUIDE.md)

### 我想开发调试
1. [开发环境配置](config/DEV_ENVIRONMENT.md)
2. [API 文档](api/README.md)
3. [项目结构](STRUCTURE.md)
4. [代码重构文档](refactor/README.md) ✨
5. [服务层架构](../backend/src/xiaoai_media/services/README.md) ✨

### 我遇到了问题
1. [配置 FAQ](config/CONFIG_FAQ.md)
2. [播放问题排查](playback/PLAYBACK_TROUBLESHOOTING.md)
3. [对话监听问题](conversation/README.md)

### 我想了解功能
1. [播放列表管理](playlist/README.md)
2. [播单存储重构](playlist/PLAYLIST_STORAGE_REFACTOR.md) - v1.0 新特性
3. [对话监听](conversation/README.md)
4. [TTS 语音](tts/README.md)

---

## 📝 文档维护

### 文档原则
- 保持简洁，避免重复
- 用户文档和开发文档分离
- 及时更新过时内容

### 文档结构
```
docs/
├── README.md              # 文档中心（本文件）
├── STRUCTURE.md           # 项目结构说明
├── api/                   # API 文档
├── config/                # 配置文档
├── deployment/            # 部署文档
├── playlist/              # 播放列表文档
├── conversation/          # 对话监听文档
├── playback/              # 音乐播放文档
├── tts/                   # TTS 文档
├── migration/             # 迁移指南
└── refactor/              # 重构文档 ✨
```

---

## 🔗 外部资源

- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
- [问题反馈](https://github.com/tmtbo/xiaoai-media/issues)
- [更新日志](../CHANGELOG.md)
