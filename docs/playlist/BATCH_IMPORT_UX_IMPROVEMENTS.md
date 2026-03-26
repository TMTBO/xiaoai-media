# 批量导入用户体验改进

## 更新日期
2026-03-26

## 改进内容

### 1. 导入完成后不自动关闭对话框

**问题**：之前批量导入完成后会自动关闭导入对话框，用户无法查看导入结果详情。

**改进**：
- 导入完成后保持对话框打开状态
- 显示详细的导入结果统计信息
- "开始导入"按钮在导入完成后自动禁用，防止重复导入
- 用户需要手动点击"关闭"按钮来关闭对话框

**实现细节**：
```typescript
// 前端代码 (PlaylistManager.vue)
// 1. 导入按钮禁用条件增加 importResult 检查
:disabled="... || importResult !== null"

// 2. 导入成功后不自动关闭对话框
// showBatchImportDialog.value = false  // 已注释

// 3. 关闭按钮点击时重置表单
function closeBatchImportDialog() {
    showBatchImportDialog.value = false
    resetImportForm()  // 重置表单和导入结果
}
```

### 2. 多目录导入时按章节信息排序

**问题**：之前多目录导入时只按文件名排序，导致不同章节的文件混在一起。

**改进**：
- 自动检测是否为多目录导入
- 多目录导入时，优先按目录名中的章节信息排序
- 支持多种章节命名格式：
  - 中文：`第01章`、`第 1 章`、`01章`
  - 英文：`Chapter 1`、`Chapter01`
  - Stage格式：`stage-02`、`stage_02`、`stage 02`、`stage02`
  - Episode格式：`episode-05`、`episode_05`、`ep-08`、`ep_08`
  - 纯数字：`01`、`1`
  - 前缀数字：`01-标题`、`01_标题`
- 同一章节内的文件按文件名自然排序
- 无章节信息的目录排在最后

**排序示例**：
```
多目录导入：
/data/第01章/001.mp3
/data/第01章/002.mp3
/data/第10章/001.mp3
/data/第10章/002.mp3
/data/第2章/001.mp3
/data/音乐/歌曲.mp3

排序结果：
1. 第01章/001.mp3  (章节1)
2. 第01章/002.mp3  (章节1)
3. 第2章/001.mp3   (章节2)
4. 第10章/001.mp3  (章节10)
5. 第10章/002.mp3  (章节10)
6. 音乐/歌曲.mp3   (无章节，排最后)
```

**实现细节**：
```python
# 后端代码 (playlist_service.py)

@staticmethod
def _extract_directory_sort_key(file_path: str) -> tuple:
    """从文件路径中提取目录排序键"""
    # 支持的章节格式正则表达式
    chapter_patterns = [
        r'第\s*(\d+)\s*章',      # 第01章、第 1 章
        r'chapter\s*(\d+)',      # Chapter 1、Chapter01
        r'stage[\-_\s]*(\d+)',   # stage-02、stage_02、stage 02、stage02
        r'episode[\-_\s]*(\d+)', # episode-02、episode_02、episode 02
        r'ep[\-_\s]*(\d+)',      # ep-02、ep_02、ep 02
        r'^(\d+)\s*章',          # 01章、1 章
        r'^(\d+)[_\-\s]',        # 01-、01_、01 开头
        r'^(\d+)$',              # 纯数字目录名
    ]
    # 返回 (章节号, 目录名, 文件名) 用于排序
    return (chapter_num, parent_dir, file_name)

# 多目录导入排序逻辑
if is_multi_directory:
    # 先按目录章节号排序，再按文件名排序
    imported_items.sort(key=lambda item: (
        PlaylistService._extract_directory_sort_key(
            item.custom_params.get("file_path", "")
        ),
        PlaylistService._natural_sort_key(
            item.custom_params.get("file_name", item.title)
        )
    ))
```

## 使用场景

### 场景1：有声书多章节导入
```
目录结构：
/data/有声书/
  ├── 第01章/
  │   ├── 001.mp3
  │   └── 002.mp3
  ├── 第02章/
  │   ├── 001.mp3
  │   └── 002.mp3
  └── 第10章/
      ├── 001.mp3
      └── 002.mp3

导入结果：
✅ 自动按章节顺序排列：第1章 → 第2章 → 第10章
✅ 每章内部按文件名排序：001 → 002
```

### 场景2：播客多期导入（支持多种格式）
```
目录结构：
/data/播客/
  ├── Episode 1/
  ├── Episode 2/
  ├── Episode 10/
  ├── stage-02/
  ├── stage-05/
  └── ep-03/

导入结果：
✅ 自动按期数排序：
   Episode 1 → stage-02 → ep-03 → stage-05 → Episode 10
✅ 支持混合格式，统一按数字排序
```

### 场景3：查看导入结果
```
导入完成后：
✅ 对话框保持打开
✅ 显示详细统计：
   - 成功导入：50 个文件
   - 跳过：2 个文件
   - 扫描总数：52 个文件
   - 播单总数：50 首
✅ "开始导入"按钮自动禁用
✅ 用户可以查看结果后手动关闭
```

## 技术细节

### 前端改动
- `frontend/src/views/PlaylistManager.vue`
  - 修改导入按钮禁用逻辑
  - 移除导入成功后自动关闭对话框
  - 添加 `closeBatchImportDialog` 函数处理关闭逻辑
  - 修改 `watch` 监听器，移除自动重置表单

### 后端改动
- `backend/src/xiaoai_media/services/playlist_service.py`
  - 添加 `_extract_directory_sort_key` 方法提取目录章节信息
  - 修改 `import_from_directory` 方法的排序逻辑
  - 支持多目录和单目录两种排序策略

### 测试
- `backend/tests/test_directory_sort.py`
  - 测试目录章节信息提取
  - 测试自然排序算法
  - 验证多种章节命名格式

## 兼容性

- ✅ 向后兼容：单目录导入行为不变
- ✅ 音乐类型播单不受影响（不排序）
- ✅ 有声书、播客等类型自动应用新排序逻辑

## 相关文档

- [批量导入功能指南](./BATCH_IMPORT_GUIDE.md)
- [播放列表排序说明](./PLAYLIST_SORTING.md)
- [自然排序算法](./NATURAL_SORT_ALGORITHM.md)
