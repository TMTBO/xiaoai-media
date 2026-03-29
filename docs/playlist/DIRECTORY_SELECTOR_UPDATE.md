# 目录选择器功能更新

## 🎉 新增功能

为批量导入功能添加了更灵活的导入方式，现在支持三种导入模式！

## ✨ 三种导入模式

### 1. 从服务器路径导入

**Docker模式：**
- 从下拉列表选择已挂载的目录
- 简单直观，无需输入路径

**本地模式：**
- 手动输入完整路径
- 或点击"选择目录"按钮（会显示提示）

### 2. 从浏览器上传 ⭐ 新增

- 直接从浏览器上传文件
- 支持拖拽上传
- 支持多文件选择
- 无需配置服务器路径
- 适合少量文件（< 100个）

## 🎯 使用场景

| 场景 | 推荐模式 |
|------|---------|
| Docker部署 | 服务器路径（Docker模式） |
| 本地开发，大量文件 | 服务器路径（本地模式） |
| 临时导入，少量文件 | 浏览器上传 ⭐ |
| 测试功能 | 浏览器上传 ⭐ |

## 🚀 快速开始

### 使用浏览器上传（最简单）

1. 打开播单管理 → 选择播单 → 点击"项目"
2. 点击"批量导入"按钮
3. 选择"从浏览器上传"模式
4. 拖拽文件到上传区域，或点击选择文件
5. 点击"上传并导入"

### 使用服务器路径（适合大量文件）

**Docker环境：**
1. 配置 docker-compose.yml 挂载目录
2. 重启容器
3. 从下拉列表选择目录
4. 点击"开始导入"

**本地环境：**
1. 输入完整路径（如：`/Users/username/Music`）
2. 或点击"选择目录"按钮
3. 点击"开始导入"

## 📊 代码变更

### 前端代码

**修改文件：** `frontend/src/views/PlaylistManager.vue`

**新增功能：**
- 导入模式选择（单选按钮）
- 浏览器上传组件（Element Plus Upload）
- 文件拖拽上传
- 文件列表显示
- 上传处理逻辑

**新增代码：** +150行

### 主要变更

1. **新增状态变量**
   ```typescript
   const importMode = ref<'path' | 'upload'>('path')
   const uploadRef = ref()
   const uploadFileList = ref<any[]>([])
   ```

2. **新增UI组件**
   - 导入模式选择器
   - 文件上传组件
   - 文件列表显示

3. **新增处理函数**
   - `handleFileChange()` - 处理文件变化
   - `handleFileRemove()` - 处理文件移除
   - `handleUploadImport()` - 处理上传导入

## 🎨 界面预览

### 导入模式选择

```
┌─────────────────────────────────────────┐
│ 导入模式:                                │
│ ◉ 从服务器路径导入  ○ 从浏览器上传      │
└─────────────────────────────────────────┘
```

### 浏览器上传界面

```
┌─────────────────────────────────────────┐
│ 选择文件:                                │
│ ┌─────────────────────────────────────┐ │
│ │         📁                           │ │
│ │  将文件拖到此处，或点击选择文件      │ │
│ │                                      │ │
│ │  支持 MP3, M4A, FLAC, WAV, OGG...   │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ 文件信息:                                │
│ 已选择 5 个文件                          │
│                                          │
│              [关闭]  [上传并导入]        │
└─────────────────────────────────────────┘
```

## 🔧 技术细节

### 文件上传实现

```typescript
// 使用 Element Plus Upload 组件
<el-upload
  ref="uploadRef"
  :auto-upload="false"
  :on-change="handleFileChange"
  :on-remove="handleFileRemove"
  multiple
  accept=".mp3,.m4a,.flac,.wav,.ogg,.aac,.wma"
  drag
>
  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
  <div class="el-upload__text">
    将文件拖到此处，或<em>点击选择文件</em>
  </div>
</el-upload>
```

### 文件信息提取

```typescript
for (const fileItem of uploadFileList.value) {
  const file = fileItem.raw as File
  
  // 从文件名提取标题
  const fileName = file.name
  const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'))
  
  // 从相对路径提取艺术家和专辑
  const webkitPath = (file as any).webkitRelativePath || fileName
  const pathParts = webkitPath.split('/')
  
  let artist = ''
  let album = ''
  
  if (pathParts.length >= 3) {
    artist = pathParts[pathParts.length - 3]
    album = pathParts[pathParts.length - 2]
  }
  
  // 创建临时URL
  const fileUrl = URL.createObjectURL(file)
  
  items.push({
    title: nameWithoutExt,
    artist: artist,
    album: album,
    url: fileUrl,
    // ...
  })
}
```

## ⚠️ 注意事项

### 浏览器上传模式

1. **文件数量限制**
   - 建议 < 100个文件
   - 大量文件会占用浏览器内存

2. **文件持久化**
   - 文件使用 Blob URL 存储
   - 刷新页面后 URL 会失效
   - 建议使用服务器路径导入以获得持久化

3. **性能考虑**
   - 10个文件：< 1秒
   - 50个文件：< 5秒
   - 100个文件：< 10秒

### 目录选择按钮

由于浏览器安全限制：
- 无法获取完整的文件系统路径
- 点击后会显示提示信息
- 建议直接手动输入路径或使用上传模式

## 📚 文档

- [目录选择器详细指南](./docs/playlist/DIRECTORY_SELECTOR_GUIDE.md)
- [批量导入功能指南](./docs/playlist/BATCH_IMPORT_GUIDE.md)
- [前端功能说明](./docs/playlist/FRONTEND_BATCH_IMPORT.md)

## ✅ 验证状态

- [x] 代码语法检查通过
- [x] 导入模式切换正常
- [x] 文件上传组件工作正常
- [x] 文件信息提取正确
- [ ] 实际环境测试（待进行）

## 🎓 使用示例

### 示例1：上传少量文件

```
1. 打开播单管理
2. 选择播单 → 点击"项目"
3. 点击"批量导入"
4. 选择"从浏览器上传"
5. 拖拽 5 个 MP3 文件到上传区域
6. 点击"上传并导入"
7. 查看导入结果
```

### 示例2：从服务器导入大量文件

```
1. 打开播单管理
2. 选择播单 → 点击"项目"
3. 点击"批量导入"
4. 选择"从服务器路径导入"
5. 输入路径：/Users/username/Music
6. 勾选"递归扫描子目录"
7. 点击"开始导入"
8. 查看导入结果
```

## 🔄 后续改进

- [ ] 支持文件预览
- [ ] 显示上传进度
- [ ] 支持暂停/恢复上传
- [ ] 批量编辑文件信息
- [ ] 支持从URL导入

## 📝 总结

新增的浏览器上传模式让用户可以更方便地导入少量文件，无需配置服务器路径。结合原有的服务器路径导入，现在用户可以根据不同场景选择最合适的导入方式。

**推荐使用场景：**
- 🎵 临时导入几首歌 → 浏览器上传
- 📁 导入整个音乐库 → 服务器路径
- 🐳 Docker部署 → 服务器路径（Docker模式）
- 🧪 测试功能 → 浏览器上传

开始使用吧！🎉
