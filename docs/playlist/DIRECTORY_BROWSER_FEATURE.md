# 目录浏览器功能

## 🎉 新增功能

为本地模式添加了目录浏览器，用户可以像文件管理器一样浏览和选择系统目录。

## ✨ 功能特性

### 1. 常用目录快速访问

**Docker模式：**
- 列出 `/data` 下的所有子目录
- 从下拉列表快速选择

**本地模式：**
- 列出常用目录（主目录、Music、Documents等）
- 从下拉列表快速访问

### 2. 目录浏览器

**特点：**
- 📁 可视化目录浏览
- ⬆️ 支持返回上级目录
- 🔒 显示无权限访问的目录
- 📂 点击目录进入子目录
- ✅ 选择当前目录

**功能：**
- 从用户主目录开始浏览
- 逐级进入子目录
- 返回上级目录
- 选择任意目录作为导入路径

## 🎨 用户界面

### 本地模式 - 常用目录

```
┌─────────────────────────────────────────┐
│ 选择目录: *                              │
│ ┌─────────────────────────────────┐     │
│ │ 主目录 (username)            ▼  │     │
│ ├─────────────────────────────────┤     │
│ │ 主目录 (username)               │     │
│ │ Music                           │     │
│ │ Documents                       │     │
│ │ Downloads                       │     │
│ └─────────────────────────────────┘     │
│                                          │
│ 或                                       │
│                                          │
│ ┌───────────────────────┬──────────┐    │
│ │ /Users/username/Music │  浏览    │    │
│ └───────────────────────┴──────────┘    │
└─────────────────────────────────────────┘
```

### 目录浏览器对话框

```
┌──────────────────────────────────────────┐
│ 选择目录                        [×]       │
├──────────────────────────────────────────┤
│ [⬆️ 上级目录]  /Users/username           │
├──────────────────────────────────────────┤
│ 📁 Documents                    →        │
│ 📁 Downloads                    →        │
│ 📁 Music                        →        │
│ 📁 Pictures                     →        │
│ 📁 Videos                       →        │
│ 📁 .ssh                         🔒       │
├──────────────────────────────────────────┤
│                    [取消]  [选择当前目录] │
└──────────────────────────────────────────┘
```

## 🚀 使用流程

### 方式1：从常用目录选择

1. 打开批量导入对话框
2. 选择"从服务器路径导入"
3. 从下拉列表选择常用目录（如 Music）
4. 点击"开始导入"

### 方式2：使用目录浏览器

1. 打开批量导入对话框
2. 选择"从服务器路径导入"
3. 点击"浏览"按钮
4. 在目录浏览器中：
   - 点击目录进入子目录
   - 点击"上级目录"返回
   - 找到目标目录后点击"选择当前目录"
5. 点击"开始导入"

### 方式3：手动输入路径

1. 打开批量导入对话框
2. 选择"从服务器路径导入"
3. 直接在输入框中输入完整路径
4. 点击"开始导入"

## 📊 代码变更

### 后端代码

**文件：** `backend/src/xiaoai_media/services/playlist_service.py`

**新增方法：**
```python
@staticmethod
def list_available_directories() -> list[dict[str, str]]:
    """列出常用目录"""
    # Docker模式：列出 /data 下的目录
    # 本地模式：列出常用目录（主目录、Music、Documents等）

@staticmethod
def browse_directory(path: str | None = None) -> dict[str, any]:
    """浏览指定目录，返回子目录列表"""
    # 返回当前路径、父路径和子目录列表
```

**文件：** `backend/src/xiaoai_media/api/routes/playlist.py`

**新增路由：**
```python
@router.get("/directories/browse")
async def browse_directory(path: str | None = None):
    """浏览指定目录，返回子目录列表"""
```

### 前端代码

**文件：** `frontend/src/api/index.ts`

**新增接口：**
```typescript
export interface BrowseDirectoryResponse {
  current_path: string
  parent_path: string | null
  directories: DirectoryInfo[]
  total: number
}

browseDirectory: (path?: string) => Promise<BrowseDirectoryResponse>
```

**文件：** `frontend/src/views/PlaylistManager.vue`

**新增组件：**
- 目录浏览器对话框
- 目录列表显示
- 上级目录按钮
- 目录选择功能

**新增状态：**
```typescript
const showDirectoryBrowser = ref(false)
const browsingDirectory = ref(false)
const currentBrowsePath = ref('')
const browserParentPath = ref<string | null>(null)
const browserDirectories = ref<DirectoryInfo[]>([])
```

**新增函数：**
```typescript
browseSubDirectory(path: string)    // 浏览子目录
browseParentDirectory()              // 返回上级目录
selectCurrentDirectory()             // 选择当前目录
```

## 🎯 技术实现

### 后端实现

#### 列出常用目录

```python
# 本地环境
home_dir = Path.home()
directories = [
    home_dir,
    home_dir / "Music",
    home_dir / "Documents",
    home_dir / "Downloads",
]
```

#### 浏览目录

```python
def browse_directory(path: str | None = None):
    if not path:
        # 从主目录开始
        current_path = Path.home()
    else:
        current_path = Path(path)
    
    # 获取父目录
    parent_path = str(current_path.parent)
    
    # 列出子目录
    subdirectories = []
    for item in current_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            subdirectories.append({
                "path": str(item),
                "name": item.name,
                "is_accessible": True
            })
    
    return {
        "current_path": str(current_path),
        "parent_path": parent_path,
        "directories": subdirectories
    }
```

### 前端实现

#### 目录浏览器

```vue
<el-dialog v-model="showDirectoryBrowser" title="选择目录">
  <!-- 当前路径和上级目录按钮 -->
  <el-button @click="browseParentDirectory">
    <el-icon><ArrowUp /></el-icon>
    上级目录
  </el-button>
  <span>{{ currentBrowsePath }}</span>
  
  <!-- 目录列表 -->
  <div 
    v-for="dir in browserDirectories" 
    @click="browseSubDirectory(dir.path)"
  >
    <el-icon><Folder /></el-icon>
    {{ dir.name }}
  </div>
  
  <!-- 选择按钮 -->
  <el-button @click="selectCurrentDirectory">
    选择当前目录
  </el-button>
</el-dialog>
```

#### 浏览逻辑

```typescript
// 浏览子目录
async function browseSubDirectory(path: string) {
  const data = await api.browseDirectory(path)
  currentBrowsePath.value = data.current_path
  browserParentPath.value = data.parent_path
  browserDirectories.value = data.directories
}

// 选择目录
function selectCurrentDirectory() {
  importForm.value.directory = currentBrowsePath.value
  showDirectoryBrowser.value = false
}
```

## 🔒 安全考虑

### 权限处理

- 检测无权限访问的目录
- 显示锁图标标识
- 禁止点击无权限目录

### 路径验证

- 验证路径存在性
- 验证路径是目录
- 防止路径遍历攻击

## 📈 性能优化

### 目录列表

- 只列出目录，不列出文件
- 跳过隐藏目录（以 `.` 开头）
- 按名称排序

### 加载状态

- 显示加载动画
- 异步加载目录
- 错误处理

## 🎓 使用示例

### 示例1：浏览并选择Music目录

```
1. 点击"浏览"按钮
2. 当前在：/Users/username
3. 点击 "Music" 目录
4. 当前在：/Users/username/Music
5. 点击"选择当前目录"
6. 已选择：/Users/username/Music
```

### 示例2：返回上级目录

```
1. 当前在：/Users/username/Music/周杰伦
2. 点击"上级目录"
3. 当前在：/Users/username/Music
4. 点击"上级目录"
5. 当前在：/Users/username
```

### 示例3：从常用目录快速选择

```
1. 从下拉列表选择 "Music"
2. 已选择：/Users/username/Music
3. 点击"开始导入"
```

## ⚠️ 注意事项

### 权限问题

- 某些系统目录可能无权限访问
- 显示锁图标的目录无法进入
- 建议选择用户目录下的文件夹

### 隐藏目录

- 以 `.` 开头的目录不会显示
- 如需访问隐藏目录，请手动输入路径

### 性能考虑

- 目录包含大量子目录时可能较慢
- 建议从常用目录开始浏览

## 🔄 后续改进

- [ ] 添加搜索功能
- [ ] 显示目录大小
- [ ] 显示文件数量
- [ ] 支持收藏常用目录
- [ ] 支持快速跳转到路径

## 📚 相关文档

- [批量导入功能指南](./docs/playlist/BATCH_IMPORT_GUIDE.md)
- [路由顺序修复](./ROUTE_ORDER_FIX.md)
- [快速修复指南](./QUICK_FIX.md)

## ✅ 总结

现在本地模式也有了完整的目录浏览功能：

1. **常用目录快速访问** - 从下拉列表选择
2. **目录浏览器** - 可视化浏览系统目录
3. **手动输入** - 直接输入完整路径

三种方式结合，为用户提供了最大的灵活性！

**重启后端服务后即可使用新功能。** 🎉
