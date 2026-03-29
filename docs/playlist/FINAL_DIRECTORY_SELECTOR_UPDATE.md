# 目录选择器最终方案

## 📋 设计决策

经过评估，我们决定采用以下方案：

### 方案说明

由于浏览器安全限制，无法通过JavaScript获取用户文件系统的完整路径。因此，我们提供了两种互补的导入方式：

## ✅ 最终实现

### 1. 从服务器路径导入

**适用场景：** 大量文件，持久化存储

**Docker模式：**
- 从下拉列表选择已挂载的目录
- 简单直观，无需输入路径
- 推荐用于生产环境

**本地模式：**
- 手动输入完整路径
- 例如：`/Users/username/Music` 或 `C:\Users\username\Music`
- 适合本地开发环境

### 2. 从浏览器上传

**适用场景：** 少量文件，临时导入

**特点：**
- 支持拖拽上传
- 支持多文件选择
- 无需配置服务器路径
- 即传即用

**限制：**
- 建议 < 100个文件
- 文件存储在浏览器内存中
- 刷新页面后需要重新上传

## 🎯 为什么不使用系统文件浏览器？

### 浏览器安全限制

现代浏览器出于安全考虑，不允许网页应用：
1. 获取用户文件系统的完整路径
2. 直接访问用户的文件系统
3. 读取文件的绝对路径

### 可用的浏览器API

1. **`<input type="file" webkitdirectory>`**
   - ✅ 可以选择目录
   - ❌ 无法获取完整路径
   - ❌ 只能获取相对路径和文件内容

2. **File System Access API**
   - ✅ 可以选择目录
   - ❌ 无法获取完整路径
   - ❌ 只能获取目录句柄，不能获取路径字符串
   - ⚠️ 浏览器支持有限（仅Chrome/Edge）

3. **Electron API**
   - ✅ 可以获取完整路径
   - ❌ 需要Electron环境
   - ❌ 不适用于Web应用

## 💡 我们的解决方案

### 方案1：服务器路径导入（推荐）

**原理：**
- 文件存储在服务器端
- 前端只需要提供路径字符串
- 后端直接访问文件系统

**优势：**
- 支持大量文件
- 性能好
- 持久化存储
- 不占用浏览器内存

**使用方式：**

**Docker环境（最简单）：**
```yaml
# docker-compose.yml
volumes:
  - /path/to/music:/data/music
```
前端从下拉列表选择 `/data/music`

**本地环境：**
直接输入完整路径：`/Users/username/Music`

### 方案2：浏览器上传

**原理：**
- 用户选择文件
- 文件内容上传到浏览器
- 创建临时URL
- 添加到播单

**优势：**
- 无需配置服务器
- 即传即用
- 适合临时导入

**使用方式：**
拖拽文件到上传区域，或点击选择文件

## 📊 方案对比

| 特性 | 服务器路径导入 | 浏览器上传 |
|------|---------------|-----------|
| 文件数量 | 无限制 | < 100 建议 |
| 性能 | 优秀 | 一般 |
| 持久化 | ✅ | ❌ |
| 配置复杂度 | 中等 | 低 |
| 适用场景 | 生产环境 | 测试/临时 |

## 🎨 用户界面

### 导入模式选择

```
┌─────────────────────────────────────────┐
│ 导入模式:                                │
│ ◉ 从服务器路径导入  ○ 从浏览器上传      │
└─────────────────────────────────────────┘
```

### 服务器路径导入

**Docker模式：**
```
┌─────────────────────────────────────────┐
│ 选择目录: *                              │
│ ┌─────────────────────────────────┐     │
│ │ music                        ▼  │     │
│ └─────────────────────────────────┘     │
│ 从挂载的volume中选择目录                │
└─────────────────────────────────────────┘
```

**本地模式：**
```
┌─────────────────────────────────────────┐
│ 目录路径: *                              │
│ ┌─────────────────────────────────┐     │
│ │ /Users/username/Music           │     │
│ └─────────────────────────────────┘     │
│ 输入本地文件系统的完整路径              │
└─────────────────────────────────────────┘
```

### 浏览器上传

```
┌─────────────────────────────────────────┐
│ 选择文件:                                │
│ ┌─────────────────────────────────────┐ │
│ │         📁                           │ │
│ │  将文件拖到此处，或点击选择文件      │ │
│ └─────────────────────────────────────┘ │
│ 已选择 5 个文件                          │
└─────────────────────────────────────────┘
```

## 🚀 使用指南

### 场景1：Docker生产环境（推荐）

```bash
# 1. 配置 docker-compose.yml
volumes:
  - /mnt/nas/music:/data/music

# 2. 重启容器
docker-compose restart

# 3. 前端操作
# - 选择"从服务器路径导入"
# - 从下拉列表选择 "music"
# - 点击"开始导入"
```

### 场景2：本地开发环境

```bash
# 前端操作
# - 选择"从服务器路径导入"
# - 输入路径：/Users/username/Music
# - 点击"开始导入"
```

### 场景3：临时导入少量文件

```bash
# 前端操作
# - 选择"从浏览器上传"
# - 拖拽文件到上传区域
# - 点击"上传并导入"
```

## 📝 代码实现

### 服务器路径导入

```typescript
// Docker模式：从下拉列表选择
<el-select v-model="importForm.directory">
  <el-option 
    v-for="dir in availableDirectories" 
    :value="dir.path"
  />
</el-select>

// 本地模式：手动输入
<el-input 
  v-model="importForm.directory" 
  placeholder="输入目录路径，如：/Users/username/Music"
/>

// 调用后端API
await api.importFromDirectory(playlistId, {
  directory: importForm.value.directory,
  recursive: true,
  file_extensions: ['.mp3', '.flac']
})
```

### 浏览器上传

```typescript
// 文件上传组件
<el-upload
  :auto-upload="false"
  :on-change="handleFileChange"
  multiple
  drag
  accept=".mp3,.m4a,.flac,.wav,.ogg,.aac,.wma"
>
  <el-icon><upload-filled /></el-icon>
  <div>将文件拖到此处，或点击选择文件</div>
</el-upload>

// 处理上传
async function handleUploadImport() {
  const items: PlaylistItem[] = []
  
  for (const fileItem of uploadFileList.value) {
    const file = fileItem.raw as File
    const fileUrl = URL.createObjectURL(file)
    
    items.push({
      title: file.name,
      url: fileUrl,
      // ...
    })
  }
  
  await api.addPlaylistItems(playlistId, { items })
}
```

## ⚠️ 重要说明

### 关于路径输入

1. **为什么需要手动输入路径？**
   - 浏览器安全限制，无法获取完整路径
   - 这是所有Web应用的共同限制

2. **如何获取路径？**
   - Windows: 在文件资源管理器地址栏复制
   - macOS: 右键文件夹 → 按住Option → 复制路径
   - Linux: 在终端使用 `pwd` 命令

3. **路径格式：**
   - Windows: `C:\Users\username\Music` 或 `C:/Users/username/Music`
   - macOS/Linux: `/Users/username/Music`

### 关于浏览器上传

1. **文件持久化：**
   - 文件使用 Blob URL 存储
   - 刷新页面后 URL 失效
   - 建议用于临时导入

2. **性能考虑：**
   - 少量文件（< 50）：体验最佳
   - 中等数量（50-100）：可以接受
   - 大量文件（> 100）：建议使用服务器路径

## 🎯 最佳实践

### 生产环境

1. 使用Docker部署
2. 配置volume挂载
3. 使用"从服务器路径导入"
4. 从下拉列表选择目录

### 开发环境

1. 使用"从服务器路径导入"
2. 手动输入完整路径
3. 或使用"从浏览器上传"测试

### 临时使用

1. 使用"从浏览器上传"
2. 拖拽文件到上传区域
3. 快速导入少量文件

## 📚 相关文档

- [批量导入功能指南](./docs/playlist/BATCH_IMPORT_GUIDE.md)
- [目录选择器指南](./docs/playlist/DIRECTORY_SELECTOR_GUIDE.md)
- [前端功能说明](./docs/playlist/FRONTEND_BATCH_IMPORT.md)

## ✅ 总结

虽然无法使用系统文件浏览器获取完整路径，但我们提供了两种互补的解决方案：

1. **服务器路径导入** - 适合大量文件，生产环境
2. **浏览器上传** - 适合少量文件，临时导入

这两种方案覆盖了所有使用场景，为用户提供了灵活的选择。

**推荐使用：**
- 🐳 Docker环境 → 服务器路径（下拉选择）
- 💻 本地开发 → 服务器路径（手动输入）
- 🧪 临时测试 → 浏览器上传
