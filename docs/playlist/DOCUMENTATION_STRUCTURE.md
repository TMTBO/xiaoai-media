# 播放列表文档结构说明

## 文档组织

本文档说明播放列表相关文档的组织结构和文件位置。

## 📁 目录结构

```
xiaoai-media/
├── docs/
│   └── playlist/                           # 播放列表文档目录
│       ├── INDEX.md                        # 📚 文档索引（入口）
│       │
│       ├── BATCH_IMPORT_V2_SUMMARY.md      # V2.1 版本总结
│       ├── CHANGELOG_V2.1.md               # V2.1 更新日志
│       ├── IMPLEMENTATION_CHECKLIST.md     # 实现检查清单
│       │
│       ├── BATCH_IMPORT_QUICK_REFERENCE.md # 批量导入快速参考
│       ├── BATCH_IMPORT_IMPROVEMENTS.md    # 批量导入功能改进
│       ├── NATURAL_SORT_IMPLEMENTATION.md  # 自然排序算法实现
│       │
│       ├── DIRECTORY_BROWSER_IMPROVEMENT.md # 目录浏览器改进
│       ├── DIRECTORY_BROWSER_FEATURE.md    # 目录浏览器功能
│       ├── DIRECTORY_SELECTOR_GUIDE.md     # 目录选择器指南
│       │
│       ├── PLAYLIST_GUIDE.md               # 播放列表指南
│       ├── PLAYLIST_PLAYER_GUIDE.md        # 播放器指南
│       ├── PLAYBACK_CONTROL.md             # 播放控制
│       │
│       └── ... (其他文档)
│
├── frontend/
│   └── src/
│       └── components/
│           ├── DirectorySelector.vue           # 目录选择器组件
│           ├── DirectorySelector.README.md     # 组件文档
│           └── DirectorySelector.example.vue   # 组件示例
│
└── backend/
    ├── src/xiaoai_media/services/
    │   └── playlist_service.py             # 播放列表服务（含排序算法）
    └── tests/
        └── test_playlist_sorting.py        # 排序功能测试
```

## 📄 文档分类

### 1. 入口文档

| 文件 | 说明 | 位置 |
|------|------|------|
| INDEX.md | 文档索引，所有文档的入口 | `docs/playlist/` |

### 2. 版本文档

| 文件 | 说明 | 位置 |
|------|------|------|
| BATCH_IMPORT_V2_SUMMARY.md | V2.1 版本完整总结 | `docs/playlist/` |
| CHANGELOG_V2.1.md | V2.1 版本更新日志 | `docs/playlist/` |
| CHANGELOG_BATCH_IMPORT_V2.md | 批量导入 V2 更新日志 | `docs/playlist/` |
| IMPLEMENTATION_CHECKLIST.md | 实现检查清单 | `docs/playlist/` |

### 3. 用户文档

| 文件 | 说明 | 位置 |
|------|------|------|
| BATCH_IMPORT_QUICK_REFERENCE.md | 批量导入快速参考 ⭐ | `docs/playlist/` |
| BATCH_IMPORT_GUIDE.md | 批量导入详细指南 | `docs/playlist/` |
| PLAYLIST_GUIDE.md | 播放列表使用指南 | `docs/playlist/` |
| PLAYLIST_PLAYER_GUIDE.md | 播放器使用指南 | `docs/playlist/` |
| QUICK_PLAYBACK_GUIDE.md | 快速播放指南 | `docs/playlist/` |

### 4. 开发文档

| 文件 | 说明 | 位置 |
|------|------|------|
| BATCH_IMPORT_IMPROVEMENTS.md | 批量导入功能改进 | `docs/playlist/` |
| NATURAL_SORT_IMPLEMENTATION.md | 自然排序算法实现 ⭐ | `docs/playlist/` |
| DIRECTORY_BROWSER_IMPROVEMENT.md | 目录浏览器改进 | `docs/playlist/` |
| PLAYLIST_STORAGE_REFACTOR.md | 存储层重构 | `docs/playlist/` |
| PLAYLIST_REFACTOR_SUMMARY.md | 重构总结 | `docs/playlist/` |

### 5. 组件文档

| 文件 | 说明 | 位置 |
|------|------|------|
| DirectorySelector.README.md | 组件使用文档 | `frontend/src/components/` |
| DirectorySelector.example.vue | 组件使用示例 | `frontend/src/components/` |

### 6. 功能文档

| 文件 | 说明 | 位置 |
|------|------|------|
| DIRECTORY_BROWSER_FEATURE.md | 目录浏览器功能 | `docs/playlist/` |
| DIRECTORY_SELECTOR_GUIDE.md | 目录选择器指南 | `docs/playlist/` |
| PLAYBACK_CONTROL.md | 播放控制功能 | `docs/playlist/` |
| AUTO_PLAY_NEXT.md | 自动播放功能 | `docs/playlist/` |
| AUDIO_URL_PARAMS.md | 音频 URL 参数 | `docs/playlist/` |

## 🔍 文档查找指南

### 按用户类型

#### 新用户
1. 从 [INDEX.md](./INDEX.md) 开始
2. 阅读 [PLAYLIST_GUIDE.md](./PLAYLIST_GUIDE.md)
3. 查看 [BATCH_IMPORT_QUICK_REFERENCE.md](./BATCH_IMPORT_QUICK_REFERENCE.md)

#### 高级用户
1. 查看 [BATCH_IMPORT_IMPROVEMENTS.md](./BATCH_IMPORT_IMPROVEMENTS.md)
2. 了解 [NATURAL_SORT_IMPLEMENTATION.md](./NATURAL_SORT_IMPLEMENTATION.md)
3. 阅读 [CHANGELOG_V2.1.md](./CHANGELOG_V2.1.md)

#### 开发者
1. 查看 [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)
2. 阅读 [DirectorySelector.README.md](../../frontend/src/components/DirectorySelector.README.md)
3. 了解 [PLAYLIST_STORAGE_REFACTOR.md](./PLAYLIST_STORAGE_REFACTOR.md)

### 按功能模块

#### 批量导入
- 快速参考：[BATCH_IMPORT_QUICK_REFERENCE.md](./BATCH_IMPORT_QUICK_REFERENCE.md)
- 功能改进：[BATCH_IMPORT_IMPROVEMENTS.md](./BATCH_IMPORT_IMPROVEMENTS.md)
- 更新日志：[CHANGELOG_V2.1.md](./CHANGELOG_V2.1.md)

#### 目录浏览
- 功能说明：[DIRECTORY_BROWSER_FEATURE.md](./DIRECTORY_BROWSER_FEATURE.md)
- 使用指南：[DIRECTORY_SELECTOR_GUIDE.md](./DIRECTORY_SELECTOR_GUIDE.md)
- 改进说明：[DIRECTORY_BROWSER_IMPROVEMENT.md](./DIRECTORY_BROWSER_IMPROVEMENT.md)
- 组件文档：[DirectorySelector.README.md](../../frontend/src/components/DirectorySelector.README.md)

#### 文件排序
- 算法实现：[NATURAL_SORT_IMPLEMENTATION.md](./NATURAL_SORT_IMPLEMENTATION.md)
- 功能改进：[BATCH_IMPORT_IMPROVEMENTS.md](./BATCH_IMPORT_IMPROVEMENTS.md)

#### 播放控制
- 播放控制：[PLAYBACK_CONTROL.md](./PLAYBACK_CONTROL.md)
- 自动播放：[AUTO_PLAY_NEXT.md](./AUTO_PLAY_NEXT.md)
- 播放器指南：[PLAYLIST_PLAYER_GUIDE.md](./PLAYLIST_PLAYER_GUIDE.md)

### 按版本

#### V2.1 (最新)
- 版本总结：[BATCH_IMPORT_V2_SUMMARY.md](./BATCH_IMPORT_V2_SUMMARY.md)
- 更新日志：[CHANGELOG_V2.1.md](./CHANGELOG_V2.1.md)
- 实现清单：[IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)

#### V2.0
- 更新日志：[CHANGELOG_BATCH_IMPORT_V2.md](./CHANGELOG_BATCH_IMPORT_V2.md)
- 功能改进：[BATCH_IMPORT_IMPROVEMENTS.md](./BATCH_IMPORT_IMPROVEMENTS.md)

#### V1.0
- 重构说明：[PLAYLIST_STORAGE_REFACTOR.md](./PLAYLIST_STORAGE_REFACTOR.md)
- 重构总结：[PLAYLIST_REFACTOR_SUMMARY.md](./PLAYLIST_REFACTOR_SUMMARY.md)

## 📝 文档命名规范

### 文件命名
- 使用大写字母和下划线：`BATCH_IMPORT_GUIDE.md`
- 版本号放在文件名中：`CHANGELOG_V2.1.md`
- 功能描述清晰：`NATURAL_SORT_IMPLEMENTATION.md`

### 文档类型
- `README.md` - 模块总览
- `INDEX.md` - 文档索引
- `GUIDE.md` - 使用指南
- `REFERENCE.md` - 快速参考
- `IMPLEMENTATION.md` - 实现细节
- `CHANGELOG.md` - 更新日志
- `SUMMARY.md` - 总结文档

## 🔄 文档维护

### 更新频率
- 版本文档：每次版本发布
- 用户文档：功能变更时
- 开发文档：重大重构时
- 索引文档：新增文档时

### 维护责任
- 版本文档：版本发布者
- 用户文档：功能开发者
- 开发文档：架构负责人
- 索引文档：文档维护者

## 📊 文档统计

### 文档数量
- 总文档数：50+ 个
- 用户文档：20+ 个
- 开发文档：15+ 个
- 版本文档：10+ 个
- 组件文档：5+ 个

### 文档大小
- 总大小：约 500 KB
- 平均大小：约 10 KB/文档
- 最大文档：约 50 KB

### 文档语言
- 中文：90%
- 英文：10%
- 代码示例：Python, JavaScript, Vue

## 🎯 文档质量标准

### 必须包含
- ✅ 清晰的标题和目录
- ✅ 简洁的概述
- ✅ 详细的说明
- ✅ 代码示例
- ✅ 常见问题
- ✅ 相关链接

### 推荐包含
- 📝 图表和截图
- 📝 使用场景
- 📝 最佳实践
- 📝 性能数据
- 📝 版本历史

### 避免
- ❌ 过时的信息
- ❌ 错误的代码
- ❌ 模糊的描述
- ❌ 缺少示例
- ❌ 死链接

## 🔗 相关资源

### 项目文档
- [项目 README](../../README.md)
- [快速开始](../../QUICK_START.md)
- [更新日志](../../CHANGELOG.md)

### 其他模块
- [API 文档](../api/README.md)
- [配置文档](../config/README.md)
- [部署文档](../deployment/README.md)

### 外部资源
- [GitHub 仓库](https://github.com/tmtbo/xiaoai-media)
- [问题追踪](https://github.com/tmtbo/xiaoai-media/issues)

---

**最后更新：** 2024
**维护者：** 项目团队
**状态：** ✅ 活跃维护
