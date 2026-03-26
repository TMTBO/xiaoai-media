# 批量导入UI更新说明

## 更新日期
2026-03-26

## 更新内容

### 1. 简化导入模式
- **移除**：导入模式选择（"从服务器路径导入" vs "从浏览器上传"）
- **保留**：仅保留PathSelector路径选择方式
- **原因**：简化用户操作流程，统一导入方式

### 2. 音频格式选择优化
- **位置调整**：将音频格式选择从PathSelector内部移到对话框顶部
- **显示方式**：使用复选框组，支持多选
- **默认值**：默认全选所有支持的音频格式（MP3, M4A, FLAC, WAV, OGG, AAC, WMA）
- **功能**：PathSelector中只显示用户选中格式的音频文件

### 3. 多目录支持
- **改进**：支持同时选择多个目录进行批量导入
- **实现**：使用`directories`（数组）替代`directory`（字符串）
- **处理**：多个目录会依次导入，汇总结果

### 4. 用户体验改进
- 用户首先选择要导入的音频格式
- PathSelector根据选中的格式过滤显示文件
- 支持选择多个目录或多个文件
- 减少不必要的文件显示，提高选择效率

## 修改的文件

### 前端文件
1. `frontend/src/views/PlaylistManager.vue`
   - 移除导入模式选择（importMode）
   - 移除上传相关代码（uploadRef, uploadFileList, handleFileChange, handleFileRemove, handleUploadImport）
   - 将音频格式选择移到PathSelector之前
   - 更新默认音频格式列表，添加.wma支持
   - 简化对话框footer，只保留一个导入按钮
   - **修复**：使用`directories`（数组）替代`directory`（字符串）
   - **增强**：支持多目录批量导入，循环处理每个目录

2. `frontend/src/components/PathSelector.vue`
   - 添加audioExtensions prop，支持从父组件传入音频格式列表
   - 使用computed属性处理audioExtensions
   - 根据传入的格式列表过滤显示的音频文件

## 使用方式

### 批量导入流程
1. 点击"批量导入"按钮
2. 选择要导入的音频格式（默认全选）
3. 使用PathSelector选择目录或文件
   - 只会显示选中格式的音频文件
   - 可以选择一个或多个目录（批量导入）
   - 可以选择一个或多个文件（精确导入）
4. 如果选择了目录，可以选择是否递归扫描子目录
5. 点击"开始导入"按钮

### 按钮禁用条件
- 未选择任何音频格式
- 未选择目录或文件

## 技术细节

### PathSelector Props
```typescript
interface Props {
    directory?: string          // 已废弃，保留用于向后兼容
    directories?: string[]      // 新增：多目录支持
    files?: string[]
    placeholder?: string
    hint?: string
    audioExtensions?: string[]  // 新增：音频格式列表
}
```

### ImportForm 结构
```typescript
{
    directories: string[]       // 选中的目录列表
    files: string[]            // 选中的文件列表
    recursive: boolean         // 是否递归扫描
    file_extensions: string[]  // 音频格式列表
}
```

### 默认音频格式
```typescript
['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma']
```

### 多目录导入逻辑
```typescript
// 如果选择了多个目录，依次导入每个目录
for (const directory of importForm.value.directories) {
    const result = await api.importFromDirectory(playlistId, {
        directory: directory,
        recursive: importForm.value.recursive,
        file_extensions: importForm.value.file_extensions
    })
    // 汇总结果
}
```

## 问题修复

### 问题：选择目录后点确定没有带回选中的目录
**原因**：
- PlaylistManager使用`v-model:directory`（单数）
- PathSelector的`confirmSelection`只更新`directories`（复数）
- 导致数据绑定不匹配

**解决方案**：
- 修改PlaylistManager使用`v-model:directories`（复数）
- 更新importForm结构使用`directories: []`
- 修改handleBatchImport支持多目录循环导入
- 更新所有相关的条件判断和验证逻辑

## 向后兼容性
- PathSelector的audioExtensions prop有默认值，不影响其他使用该组件的地方
- PathSelector仍然支持`directory` prop（单数），但推荐使用`directories`（复数）
- 保持了原有的API接口，只是移除了上传模式

## 未来改进建议
1. 可以考虑添加"全选/取消全选"按钮
2. 可以保存用户的格式选择偏好
3. 可以根据目录内容自动检测并推荐格式
4. 可以显示每个目录的导入进度
5. 可以支持拖拽排序导入顺序
