# 文档结构

本目录包含 XiaoAI Media 项目的完整文档。

## 📂 目录结构

```
docs/
├── README.md                    # 文档入口
├── STRUCTURE.md                 # 本文档 - 文档结构说明
├── INDEX.md                     # 文档索引
├── NAVIGATION.md                # 导航指南
│
├── api/                         # API 文档
│   ├── API_REFERENCE.md         # API 接口参考
│   └── API实现说明.md            # API 实现说明
│
├── config/                      # 配置文档
│   ├── CONFIG_API.md            # 配置管理 API
│   ├── QUICK_CONFIG.md          # 快速配置指南
│   ├── CONFIG_FAQ.md            # 配置常见问题
│   ├── CONFIG_CHEATSHEET.md     # 配置速查表
│   ├── CONFIG_ANSWERS.md        # 配置问答
│   ├── USER_CONFIG_GUIDE.md     # 用户配置指南
│   ├── USER_CONFIG_IMPLEMENTATION.md  # 配置实现说明
│   └── USER_CONFIG_SUMMARY.md   # 配置摘要
│
├── playlist/                    # 播放列表文档
│   ├── PLAYLIST_GUIDE.md        # 播放列表使用指南
│   ├── PLAYLIST_FEATURE_UPDATE.md  # 功能更新说明
│   └── PLAYLIST_IMPROVEMENTS.md # 功能改进记录
│
├── playback/                    # 播放功能文档
│   ├── README.md                # 播放功能概览
│   ├── QUICK_PLAYBACK_GUIDE.md  # 快速播放指南
│   ├── PLAYBACK_FIX.md          # 播放问题修复
│   ├── PLAYBACK_TROUBLESHOOTING.md  # 播放故障排查
│   ├── PROXY_URL_SUMMARY.md     # 代理 URL 摘要
│   ├── 播放错误修复说明.md        # 播放错误修复详解
│   ├── 播放错误快速修复.md        # 播放错误快速修复
│   ├── 代理URL使用指南.md         # 代理 URL 使用指南
│   └── 代理URL封装说明.md         # 代理 URL 封装说明
│
├── tts/                         # TTS 文档
│   ├── README.md                # TTS 功能概览
│   ├── README_TTS.md            # TTS 详细说明
│   ├── QUICK_TEST.md            # 快速测试指南
│   ├── TTS修复说明.md            # TTS 修复说明
│   ├── TTS_完整解决方案.md       # TTS 完整解决方案
│   └── 功能验证报告.md           # 功能验证报告
│
├── conversation/                # 对话监听文档
│   ├── README.md                # 对话监听概览
│   ├── QUICK_START.md           # 快速开始
│   ├── QUICK_REFERENCE.md       # 快速参考
│   ├── USER_GUIDE.md            # 用户指南
│   ├── FEATURE_SPEC.md          # 功能规格
│   ├── SUMMARY.md               # 功能摘要
│   ├── 使用说明.md               # 使用说明
│   ├── 修复总结.md               # 修复总结
│   ├── 修复说明.md               # 修复详解
│   ├── 功能说明.md               # 功能说明
│   ├── 完整修复报告.md           # 完整修复报告
│   ├── 完整指南.md               # 完整指南
│   ├── 快速参考.md               # 快速参考（中文）
│   ├── 播放拦截问题分析.md       # 播放拦截分析
│   ├── 管理后台修复.md           # 管理后台修复
│   ├── 管理后台验证.md           # 管理后台验证
│   └── 验证报告.md               # 验证报告
│
├── migration/                   # 迁移文档
│   ├── README.md                # 迁移概览
│   ├── MISERVICE_MIGRATION.md   # MiService 迁移指南
│   ├── MIGRATION_TO_USER_CONFIG.md  # 迁移到 user_config
│   ├── MIGRATION_COMPLETE.md    # 迁移完成说明
│   ├── MIGRATION_SUMMARY.md     # 迁移摘要
│   ├── IMPLEMENTATION_COMPLETE.md  # 实现完成说明
│   ├── FINAL_SUMMARY.md         # 最终摘要
│   └── CLEANUP_SUMMARY.md       # 清理摘要
│
├── BEFORE_AFTER.md              # 改进前后对比
├── ORGANIZATION_REPORT.md       # 代码组织报告
├── ORGANIZATION_SUMMARY.md      # 组织摘要
└── UPGRADE_GUIDE.md             # 升级指南
```

## 📖 快速导航

### 新手入门
1. [README.md](README.md) - 项目概览
2. [config/QUICK_CONFIG.md](config/QUICK_CONFIG.md) - 快速配置
3. [playback/QUICK_PLAYBACK_GUIDE.md](playback/QUICK_PLAYBACK_GUIDE.md) - 快速播放测试

### 配置相关
- [配置 API](config/CONFIG_API.md) - 通过管理后台管理配置
- [配置指南](config/USER_CONFIG_GUIDE.md) - 详细配置说明
- [配置常见问题](config/CONFIG_FAQ.md) - 配置问题排查

### 功能使用
- [播放列表](playlist/PLAYLIST_GUIDE.md) - 播放列表功能
- [TTS 语音播报](tts/README.md) - 文字转语音
- [对话监听](conversation/README.md) - 语音指令监听

### 问题排查
- [播放故障排查](playback/PLAYBACK_TROUBLESHOOTING.md)
- [配置常见问题](config/CONFIG_FAQ.md)
- [TTS 修复说明](tts/TTS修复说明.md)

### API 开发
- [API 参考](api/API_REFERENCE.md) - 完整 API 文档
- [API 实现说明](api/API实现说明.md) - API 实现细节

## 📝 文档维护原则

1. **功能分类**：按功能模块组织文档，每个功能一个目录
2. **语言统一**：新文档优先使用中文，重要文档提供中英双语
3. **文件命名**：
   - 英文文档：`UPPERCASE_WITH_UNDERSCORE.md`
   - 中文文档：`中文名称.md`
4. **README 优先**：每个目录都应有 `README.md` 作为入口
5. **定期清理**：删除过时文档，合并重复内容

## 🔄 更新记录

- 2026-03-20: 创建文档结构，整理配置、播放列表、API 文档
- 2026-03-20: 添加配置管理 API 文档
