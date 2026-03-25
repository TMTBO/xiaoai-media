# 批量导入功能改进 - 更新日志

## 版本 2.0 - 2024

### 新增功能

#### 1. 目录选择器组件化 ✨

- 创建独立的 `DirectorySelector.vue` 组件
- 支持在任何地方复用
- 统一本地和 Docker 模式的用户界面
- 支持点击输入框或按钮打开浏览器

**影响的文件：**
- `frontend/src/components/DirectorySelector.vue` (新增)
- `frontend/src/views/PlaylistManager.vue` (重构)

#### 2. 智能文件排序 🎯

- 根据播单类型自动决定是否排序
- 音乐类型保持原始顺序
- 有声书、播客等按章节/集数排序
- 支持多种编号格式识别

**支持的格式：**
- 中文：第01章、第1集、1章
- 英文：Chapter 1、Episode 01
- 数字：001、01、1
- 分隔符：001-、1.、1_

**影响的文件：**
- `backend/src/xiaoai_media/services/playlist_service.py` (新增排序逻辑)

#### 3. 导入成功自动关闭 ⚡

- 导入成功后延迟 2 秒自动关闭对话框
- 给用户足够时间查看导入结果
- 提升用户体验

**影响的文件：**
- `frontend/src/views/PlaylistManager.vue` (修改)

### 改进点

#### 代码质量

- ✅ 组件化设计，提高代码复用性
- ✅ 删除重复代码，简化维护
- ✅ 统一本地和 Docker 模式的实现
- ✅ 添加详细的代码注释

#### 用户体验

- ✅ 统一的目录选择界面
- ✅ 更直观的交互方式
- ✅ 自动关闭减少操作步骤
- ✅ 智能排序提升播放体验

#### 性能优化

- ✅ 只对需要排序的类型进行排序
- ✅ 高效的排序算法
- ✅ 减少不必要的状态管理

### 技术细节

#### 前端改进

**新增组件：**
```vue
<DirectorySelector 
    v-model="importForm.directory"
    placeholder="点击选择目录"
    hint="点击输入框或浏览按钮选择目录"
/>
```

**删除的代码：**
- 目录浏览器对话框（移至组件）
- 目录浏览相关函数（移至组件）
- 重复的状态管理变量

**简化的逻辑：**
- `loadAvailableDirectories` → `loadEnvironmentInfo`
- 删除 `browseSubDirectory`、`browseParentDirectory`、`selectCurrentDirectory`

#### 后端改进

**新增函数：**
```python
@staticmethod
def _extract_sort_key(filename: str) -> tuple:
    """从文件名中提取排序关键字"""
    # 支持多种编号格式
    # 返回 (数字, 文件名) 用于排序

@staticmethod
def _should_sort_files(playlist_type: str) -> bool:
    """判断是否需要排序"""
    # 音乐类型不排序
    return playlist_type not in ['music', '']
```

**修改的逻辑：**
```python
# 添加排序键到 custom_params
item.custom_params["sort_key"] = PlaylistService._extract_sort_key(file_path.name)

# 根据类型决定是否排序
if imported_items and PlaylistService._should_sort_files(playlist.type):
    imported_items.sort(key=lambda item: item.custom_params.get("sort_key", (float('inf'), "")))
```

### 测试

**新增测试文件：**
- `backend/tests/test_playlist_sorting.py`

**测试覆盖：**
- ✅ 中文章节格式识别
- ✅ 英文章节格式识别
- ✅ 纯数字格式识别
- ✅ 带分隔符格式识别
- ✅ 无编号文件处理
- ✅ 混合格式排序
- ✅ 播单类型判断

### 文档

**新增文档：**
- `docs/playlist/BATCH_IMPORT_IMPROVEMENTS.md` - 详细改进说明
- `docs/playlist/CHANGELOG_BATCH_IMPORT_V2.md` - 本更新日志

**更新文档：**
- `docs/playlist/DIRECTORY_BROWSER_IMPROVEMENT.md` - 目录浏览器改进

### 迁移指南

#### 对于开发者

如果你在其他地方需要目录选择功能：

```vue
<script setup>
import DirectorySelector from '@/components/DirectorySelector.vue'
import { ref } from 'vue'

const selectedPath = ref('')
</script>

<template>
  <DirectorySelector v-model="selectedPath" />
</template>
```

#### 对于用户

无需任何操作，所有改进自动生效：

1. 打开批量导入对话框
2. 点击输入框或"浏览"按钮选择目录
3. 选择文件格式和扫描选项
4. 点击"开始导入"
5. 导入成功后对话框自动关闭

### 兼容性

- ✅ 完全向后兼容
- ✅ 不影响现有播单
- ✅ API 接口保持不变
- ✅ 支持本地和 Docker 环境

### 已知问题

无

### 下一步计划

1. 添加导入预览功能
2. 支持更多排序选项
3. 支持批量编辑导入的项目
4. 添加导入进度显示

### 贡献者

- 实现目录选择器组件化
- 实现智能文件排序
- 实现自动关闭功能
- 编写测试和文档

### 反馈

如有问题或建议，请提交 Issue 或 Pull Request。
