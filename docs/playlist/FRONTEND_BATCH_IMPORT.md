# 前端批量导入功能说明

## 功能概述

在播单管理页面添加了批量导入功能，用户可以通过图形界面从指定目录批量导入音频文件到播单中。

## 功能特性

### 1. 环境自适应

- **自动检测运行环境**（本地/Docker）
- **Docker模式**：显示下拉选择器，列出可用的挂载目录
- **本地模式**：显示文本输入框，用户输入本地路径

### 2. 灵活的导入选项

- **递归扫描**：可选择是否扫描子目录
- **文件格式过滤**：支持多选音频格式
  - MP3 (.mp3)
  - M4A (.m4a)
  - FLAC (.flac)
  - WAV (.wav)
  - OGG (.ogg)
  - AAC (.aac)
  - WMA (.wma)

### 3. 实时反馈

- **导入进度**：显示"导入中..."状态
- **导入结果**：显示详细的导入统计
  - 成功导入的文件数
  - 跳过的文件数
  - 扫描的总文件数
  - 播单中的总项目数
  - 跳过的文件列表（最多10个）

## 使用流程

### 步骤1：打开播单管理页面

访问播单管理页面，选择要导入文件的播单。

### 步骤2：点击"项目"按钮

在播单列表中，点击对应播单的"项目"按钮，打开播单项目管理对话框。

### 步骤3：点击"批量导入"按钮

在项目管理对话框中，点击"批量导入"按钮，打开批量导入对话框。

### 步骤4：选择目录

- **Docker模式**：从下拉列表中选择已挂载的目录
- **本地模式**：输入本地文件系统的完整路径

### 步骤5：配置导入选项

- 勾选"递归扫描子目录"（如果需要）
- 选择要导入的文件格式

### 步骤6：开始导入

点击"开始导入"按钮，等待导入完成。

### 步骤7：查看结果

导入完成后，会显示详细的导入统计信息。

## 界面说明

### 批量导入对话框

```
┌─────────────────────────────────────────┐
│ 批量导入音频文件                         │
├─────────────────────────────────────────┤
│ [环境提示]                               │
│ Docker模式 / 本地模式                    │
│ 从挂载的volume中选择目录                 │
├─────────────────────────────────────────┤
│ 选择目录: [下拉选择器/文本输入框]        │
│                                          │
│ 扫描选项:                                │
│ ☑ 递归扫描子目录                         │
│                                          │
│ 文件格式:                                │
│ ☑ MP3  ☑ M4A  ☑ FLAC  ☑ WAV            │
│ ☑ OGG  ☑ AAC  ☐ WMA                     │
├─────────────────────────────────────────┤
│ [导入结果显示区域]                       │
│ ✅ 成功导入：50 个文件                   │
│ ⏭️ 跳过：2 个文件                        │
│ 📁 扫描总数：100 个文件                  │
│ 🎵 播单总数：50 首                       │
├─────────────────────────────────────────┤
│              [关闭]  [开始导入]          │
└─────────────────────────────────────────┘
```

### 环境提示

#### Docker模式
```
ℹ️ Docker模式
从挂载的volume中选择目录
```

#### 本地模式
```
✅ 本地模式
输入本地文件系统的完整路径
```

## 代码变更

### 1. API接口 (`frontend/src/api/index.ts`)

新增接口定义：

```typescript
export interface ImportFromDirectoryRequest {
  directory: string
  recursive?: boolean
  file_extensions?: string[]
}

export interface ImportResult {
  imported: number
  skipped: number
  total_scanned: number
  skipped_files?: string[]
  playlist_total_items: number
}

export interface DirectoryInfo {
  path: string
  name: string
  is_docker: boolean
}

export interface DirectoriesResponse {
  directories: DirectoryInfo[]
  is_docker: boolean
  message: string
}
```

新增API方法：

```typescript
// Playlist: Batch import
getAvailableDirectories: () =>
  http.get<DirectoriesResponse>('/playlists/directories').then(r => r.data),
importFromDirectory: (playlistId: string, data: ImportFromDirectoryRequest) =>
  http.post<ImportResult>(`/playlists/${playlistId}/import`, data).then(r => r.data),
```

### 2. 播单管理页面 (`frontend/src/views/PlaylistManager.vue`)

#### 新增状态变量

```typescript
// 批量导入相关
const isDockerEnv = ref(false)
const environmentMessage = ref('')
const availableDirectories = ref<DirectoryInfo[]>([])
const directoriesLoading = ref(false)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)

const importForm = ref({
    directory: '',
    recursive: true,
    file_extensions: ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac'] as string[],
})
```

#### 新增函数

```typescript
// 加载可用目录
async function loadAvailableDirectories()

// 批量导入
async function handleBatchImport()

// 重置批量导入表单
function resetImportForm()
```

#### 新增UI组件

- 批量导入按钮
- 批量导入对话框
- 环境提示组件
- 目录选择器（Docker模式）
- 路径输入框（本地模式）
- 导入选项配置
- 导入结果显示

## 用户体验优化

### 1. 智能默认值

- Docker模式：自动选择第一个非根目录
- 文件格式：默认选中常用格式（MP3, M4A, FLAC, WAV, OGG, AAC）
- 递归扫描：默认开启

### 2. 实时验证

- 目录路径必填
- 至少选择一种文件格式
- 必须先选择播单

### 3. 友好提示

- 环境标识（Docker/本地）
- 操作说明文字
- 错误提示信息
- 成功反馈

### 4. 加载状态

- 目录加载中显示loading
- 导入中显示"导入中..."
- 按钮禁用状态

## 错误处理

### 常见错误及提示

1. **未选择目录**
   ```
   请选择或输入目录路径
   ```

2. **未选择文件格式**
   ```
   请至少选择一种文件格式
   ```

3. **未选择播单**
   ```
   请先选择一个播单
   ```

4. **目录不存在**
   ```
   导入失败: Directory not found: /path/to/dir
   ```

5. **权限错误**
   ```
   导入失败: Permission denied
   ```

6. **没有文件被导入**
   ```
   没有文件被导入，请检查目录路径和文件格式
   ```

## 测试建议

### 功能测试

1. **环境检测**
   - [ ] Docker环境显示正确
   - [ ] 本地环境显示正确
   - [ ] 环境提示信息正确

2. **目录列表**
   - [ ] Docker模式加载目录列表
   - [ ] 本地模式显示输入框
   - [ ] 默认选择正确

3. **导入功能**
   - [ ] 非递归导入成功
   - [ ] 递归导入成功
   - [ ] 文件格式过滤正确
   - [ ] 导入结果显示正确

4. **错误处理**
   - [ ] 空目录提示
   - [ ] 无效路径提示
   - [ ] 权限错误提示
   - [ ] 网络错误提示

### UI测试

1. **对话框**
   - [ ] 打开/关闭正常
   - [ ] 表单重置正常
   - [ ] 布局美观

2. **交互**
   - [ ] 按钮状态正确
   - [ ] 加载状态显示
   - [ ] 禁用状态正确

3. **响应式**
   - [ ] 不同屏幕尺寸正常
   - [ ] 移动端适配

## 后续改进

### 短期

- [ ] 添加文件预览功能
- [ ] 支持拖拽上传
- [ ] 添加进度条

### 中期

- [ ] WebSocket实时进度
- [ ] 批量编辑元信息
- [ ] 导入历史记录

### 长期

- [ ] 智能分类
- [ ] 重复检测
- [ ] 封面图片提取

## 相关文档

- [后端API文档](./BATCH_IMPORT_GUIDE.md)
- [前端集成示例](./BATCH_IMPORT_FRONTEND_EXAMPLE.md)
- [完整更新日志](./CHANGELOG_BATCH_IMPORT.md)

## 截图示例

### Docker模式

```
┌─────────────────────────────────────────┐
│ ℹ️ Docker模式                            │
│ 从挂载的volume中选择目录                 │
├─────────────────────────────────────────┤
│ 选择目录: [music ▼]                      │
│           ├─ 数据根目录 (/data)          │
│           ├─ music (/data/music)         │
│           └─ audiobooks (/data/audiobooks)│
└─────────────────────────────────────────┘
```

### 本地模式

```
┌─────────────────────────────────────────┐
│ ✅ 本地模式                              │
│ 输入本地文件系统的完整路径               │
├─────────────────────────────────────────┤
│ 目录路径: [/Users/username/Music      ] │
│           输入本地文件系统的完整路径     │
└─────────────────────────────────────────┘
```

### 导入结果

```
┌─────────────────────────────────────────┐
│ ✅ 导入完成                              │
├─────────────────────────────────────────┤
│ ✅ 成功导入：50 个文件                   │
│ ⏭️ 跳过：2 个文件                        │
│ 📁 扫描总数：100 个文件                  │
│ 🎵 播单总数：50 首                       │
│                                          │
│ ─────────────────────────────────────   │
│ ⚠️ 部分文件被跳过：                      │
│   • file1.txt                            │
│   • file2.log                            │
└─────────────────────────────────────────┘
```

## 总结

前端批量导入功能已完整实现，提供了友好的用户界面和完善的错误处理。用户可以轻松地从本地或Docker环境中批量导入音频文件到播单中。
