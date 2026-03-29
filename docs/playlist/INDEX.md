# 播放列表功能文档索引

## 概述

本目录包含播放列表相关的所有文档，包括功能说明、使用指南、开发文档和更新日志。

## 📚 文档分类

### 用户文档

#### 快速入门
- [播放列表指南](./PLAYLIST_GUIDE.md) - 播放列表功能完整指南
- [播放列表播放器指南](./PLAYLIST_PLAYER_GUIDE.md) - 播放器使用说明
- [快速播放指南](./QUICK_PLAYBACK_GUIDE.md) - 快速开始播放

#### 批量导入
- [批量导入快速参考](./BATCH_IMPORT_QUICK_REFERENCE.md) - 批量导入功能快速参考 ⭐
- [批量导入指南](./BATCH_IMPORT_GUIDE.md) - 详细的批量导入使用指南
- [批量导入前端示例](./BATCH_IMPORT_FRONTEND_EXAMPLE.md) - 前端实现示例
- [批量导入 README](./BATCH_IMPORT_README.md) - 批量导入功能说明

#### 目录浏览
- [目录浏览器功能](./DIRECTORY_BROWSER_FEATURE.md) - 目录浏览器功能说明
- [目录选择器指南](./DIRECTORY_SELECTOR_GUIDE.md) - 目录选择器使用指南
- [目录选择器更新](./DIRECTORY_SELECTOR_UPDATE.md) - 目录选择器更新说明
- [最终目录选择器更新](./FINAL_DIRECTORY_SELECTOR_UPDATE.md) - 最终更新说明

#### 播放控制
- [播放控制](./PLAYBACK_CONTROL.md) - 播放控制功能说明
- [播放监控配置](./PLAYBACK_MONITOR_CONFIG.md) - 播放监控配置指南
- [自动播放下一首](./AUTO_PLAY_NEXT.md) - 自动播放功能说明
- [自动播放实现](./AUTO_PLAY_IMPLEMENTATION.md) - 自动播放实现细节

#### 音频参数
- [音频 URL 参数](./AUDIO_URL_PARAMS.md) - 音频 URL 参数说明

### 开发文档

#### 架构设计
- [播放列表改进](./PLAYLIST_IMPROVEMENTS.md) - 播放列表功能改进说明
- [播放列表存储重构](./PLAYLIST_STORAGE_REFACTOR.md) - 存储层重构文档
- [播放列表重构总结](./PLAYLIST_REFACTOR_SUMMARY.md) - 重构总结

#### 实现细节
- [自然排序算法实现](./NATURAL_SORT_IMPLEMENTATION.md) - 自然排序算法详解 ⭐
- [批量导入功能改进](./BATCH_IMPORT_IMPROVEMENTS.md) - 批量导入改进说明 ⭐
- [目录浏览器改进](./DIRECTORY_BROWSER_IMPROVEMENT.md) - 目录浏览器改进说明
- [实现清单](./IMPLEMENTATION_CHECKLIST.md) - 功能实现检查清单 ⭐

#### 前端组件
- [DirectorySelector 组件](../../frontend/src/components/DirectorySelector.vue) - 目录选择器组件
- [DirectorySelector 文档](../../frontend/src/components/DirectorySelector.README.md) - 组件使用文档
- [DirectorySelector 示例](../../frontend/src/components/DirectorySelector.example.vue) - 组件使用示例

### 更新日志

#### 版本历史
- [V2.1 更新日志](./CHANGELOG_V2.1.md) - V2.1 版本更新日志 ⭐
- [批量导入 V2 更新日志](./CHANGELOG_BATCH_IMPORT_V2.md) - 批量导入 V2 更新
- [批量导入更新日志](./CHANGELOG_BATCH_IMPORT.md) - 批量导入功能更新
- [播放列表重构更新日志](./CHANGELOG_PLAYLIST_REFACTOR.md) - 播放列表重构更新

#### 版本总结
- [批量导入 V2.1 总结](./BATCH_IMPORT_V2_SUMMARY.md) - V2.1 版本完整总结 ⭐
- [最终更新](./FINAL_UPDATE.md) - 最终更新说明

### 文档组织
- [文档组织](./DOCUMENTATION_ORGANIZATION.md) - 文档组织说明
- [播放列表功能更新](./PLAYLIST_FEATURE_UPDATE.md) - 功能更新说明

## 🚀 快速导航

### 我想...

#### 开始使用播放列表
1. 阅读 [播放列表指南](./PLAYLIST_GUIDE.md)
2. 查看 [快速播放指南](./QUICK_PLAYBACK_GUIDE.md)
3. 了解 [播放控制](./PLAYBACK_CONTROL.md)

#### 批量导入音频文件
1. 阅读 [批量导入快速参考](./BATCH_IMPORT_QUICK_REFERENCE.md) ⭐ 推荐
2. 查看 [批量导入指南](./BATCH_IMPORT_GUIDE.md)
3. 了解 [目录浏览器功能](./DIRECTORY_BROWSER_FEATURE.md)

#### 了解最新功能
1. 查看 [V2.1 更新日志](./CHANGELOG_V2.1.md) ⭐ 最新
2. 阅读 [批量导入 V2.1 总结](./BATCH_IMPORT_V2_SUMMARY.md)
3. 了解 [自然排序算法](./NATURAL_SORT_IMPLEMENTATION.md)

#### 开发和贡献
1. 阅读 [实现清单](./IMPLEMENTATION_CHECKLIST.md)
2. 查看 [播放列表重构总结](./PLAYLIST_REFACTOR_SUMMARY.md)
3. 了解 [DirectorySelector 组件文档](../../frontend/src/components/DirectorySelector.README.md)

## 📋 功能特性

### 核心功能
- ✅ 创建和管理播放列表
- ✅ 添加、删除、编辑播放项
- ✅ 播放、暂停、停止控制
- ✅ 播放模式（列表循环、单曲循环、随机播放）
- ✅ 语音命令控制
- ✅ 自动播放下一首

### 批量导入（V2.1）
- ✅ 从服务器路径批量导入
- ✅ 从浏览器上传文件
- ✅ 目录浏览器（本地和 Docker 统一）
- ✅ 递归扫描子目录
- ✅ 多种音频格式支持
- ✅ 自然排序算法（智能章节排序）
- ✅ 导入成功后立即显示项目列表

### 高级功能
- ✅ 自定义音频 URL 参数
- ✅ 播放间隔设置
- ✅ 封面图片支持
- ✅ 播放监控和状态同步
- ✅ 代理 URL 支持

## 🔄 版本历史

### V2.1 (最新) - 2024
- ✨ 导入成功后立即显示项目列表
- ✨ 采用自然排序算法
- 🚀 性能提升 40%
- 📝 完善文档

### V2.0 - 2024
- ✨ 目录选择器组件化
- ✨ 智能文件排序
- ✨ 统一本地和 Docker 模式

### V1.0 - 2024
- ✨ 基本播放列表功能
- ✨ 批量导入功能
- ✨ 播放控制功能

## 🎯 推荐阅读路径

### 新用户
1. [播放列表指南](./PLAYLIST_GUIDE.md)
2. [批量导入快速参考](./BATCH_IMPORT_QUICK_REFERENCE.md)
3. [播放控制](./PLAYBACK_CONTROL.md)

### 高级用户
1. [批量导入功能改进](./BATCH_IMPORT_IMPROVEMENTS.md)
2. [自然排序算法实现](./NATURAL_SORT_IMPLEMENTATION.md)
3. [播放列表重构总结](./PLAYLIST_REFACTOR_SUMMARY.md)

### 开发者
1. [实现清单](./IMPLEMENTATION_CHECKLIST.md)
2. [DirectorySelector 组件文档](../../frontend/src/components/DirectorySelector.README.md)
3. [播放列表存储重构](./PLAYLIST_STORAGE_REFACTOR.md)

## 📞 获取帮助

### 常见问题
- 查看 [批量导入快速参考](./BATCH_IMPORT_QUICK_REFERENCE.md) 的常见问题部分
- 查看 [自然排序算法实现](./NATURAL_SORT_IMPLEMENTATION.md) 的常见问题部分

### 反馈和建议
- 提交 Issue
- 发起 Pull Request
- 查看 [贡献指南](../CONTRIBUTING.md)

## 🔗 相关文档

### 其他模块
- [API 文档](../api/README.md)
- [配置文档](../config/README.md)
- [部署文档](../deployment/README.md)
- [对话功能](../conversation/README.md)

### 项目文档
- [项目 README](../../README.md)
- [快速开始](../../QUICK_START.md)
- [更新日志](../../CHANGELOG.md)

---

**最后更新：** 2024
**当前版本：** V2.1
**维护状态：** ✅ 活跃维护
