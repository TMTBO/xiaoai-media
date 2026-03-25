# 批量导入功能改进

## 改进内容

### 1. 导入成功后自动关闭对话框

**改进前：**
- 导入完成后对话框保持打开状态
- 用户需要手动点击"关闭"按钮

**改进后：**
- 导入成功后延迟 2 秒自动关闭对话框
- 给用户足够时间查看导入结果
- 提升用户体验，减少操作步骤

### 2. 目录选择器组件化

**改进前：**
- 目录浏览逻辑直接写在 PlaylistManager.vue 中
- 代码重复，难以维护
- Docker 和本地模式使用不同的界面

**改进后：**
- 创建独立的 `DirectorySelector.vue` 组件
- 可在任何地方复用
- Docker 和本地模式使用统一的目录浏览器
- 代码更清晰，易于维护

### 3. 智能文件排序

**改进前：**
- 所有文件按照文件系统顺序导入
- 有声书、播客等需要按章节顺序播放的内容顺序混乱

**改进后：**
- 根据播单类型自动决定是否排序
- 音乐类型：不排序（保持原始顺序）
- 其他类型（有声书、播客、广播剧等）：智能排序
- 支持多种编号格式识别

## 技术实现

### 1. 前端改进

#### DirectorySelector 组件

**文件：** `frontend/src/components/DirectorySelector.vue`

**特性：**
- 独立的可复用组件
- 支持 v-model 双向绑定
- 可自定义提示文本
- 内置目录浏览对话框
- 支持点击输入框或按钮打开浏览器

**使用示例：**
```vue
<DirectorySelector 
    v-model="importForm.directory"
    placeholder="点击选择目录"
    hint="点击输入框或浏览按钮选择目录"
/>
```

#### PlaylistManager 改进

**文件：** `frontend/src/views/PlaylistManager.vue`

**改进点：**
1. 使用 DirectorySelector 组件替代原有代码
2. 删除重复的目录浏览逻辑
3. 简化状态管理
4. 导入成功后自动关闭对话框

### 2. 后端改进

#### 智能排序算法

**文件：** `backend/src/xiaoai_media/services/playlist_service.py`

**新增函数：**

1. `_extract_sort_key(filename: str) -> tuple`
   - 从文件名中提取排序关键字
   - 支持多种编号格式
   - 返回 (数字, 文件名) 元组用于排序

2. `_should_sort_files(playlist_type: str) -> bool`
   - 判断是否需要排序
   - 音乐类型不排序
   - 其他类型需要排序

**支持的编号格式：**
- 中文章节：`第01章.mp3`, `第1集.mp3`, `1章.mp3`
- 英文章节：`Chapter 1.mp3`, `Episode 01.mp3`
- 纯数字：`001.mp3`, `01.mp3`, `1.mp3`
- 带分隔符：`001-标题.mp3`, `1.标题.mp3`, `1_标题.mp3`
- 中间数字：`标题001.mp3`

**排序逻辑：**
```python
# 提取排序关键字
item.custom_params["sort_key"] = PlaylistService._extract_sort_key(file_path.name)

# 根据播单类型决定是否排序
if imported_items and PlaylistService._should_sort_files(playlist.type):
    imported_items.sort(key=lambda item: item.custom_params.get("sort_key", (float('inf'), "")))
```

## 使用场景

### 音乐播单（不排序）

```
导入前：
- 03-歌曲C.mp3
- 01-歌曲A.mp3
- 02-歌曲B.mp3

导入后（保持原顺序）：
1. 03-歌曲C
2. 01-歌曲A
3. 02-歌曲B
```

### 有声书播单（自动排序）

```
导入前：
- 第10章.mp3
- 第2章.mp3
- 第1章.mp3

导入后（按章节排序）：
1. 第1章
2. 第2章
3. 第10章
```

### 播客播单（自动排序）

```
导入前：
- Episode 5.mp3
- Episode 10.mp3
- Episode 2.mp3

导入后（按集数排序）：
1. Episode 2
2. Episode 5
3. Episode 10
```

## 配置说明

### 播单类型与排序行为

| 播单类型 | type 值 | 是否排序 | 说明 |
|---------|---------|---------|------|
| 音乐 | music | ❌ 否 | 保持原始顺序 |
| 有声书 | audiobook | ✅ 是 | 按章节排序 |
| 播客 | podcast | ✅ 是 | 按集数排序 |
| 广播剧 | radio_drama | ✅ 是 | 按集数排序 |
| 其他 | other | ✅ 是 | 按编号排序 |

### 自定义排序行为

如果需要修改排序行为，可以编辑 `_should_sort_files` 函数：

```python
@staticmethod
def _should_sort_files(playlist_type: str) -> bool:
    # 添加更多不需要排序的类型
    return playlist_type not in ['music', 'custom_type', '']
```

## 测试建议

### 1. 目录选择器测试

- [ ] 点击输入框打开浏览器
- [ ] 点击"浏览"按钮打开浏览器
- [ ] 浏览子目录
- [ ] 返回父目录
- [ ] 选择目录后正确显示路径
- [ ] 本地和 Docker 模式行为一致

### 2. 自动关闭测试

- [ ] 导入成功后 2 秒自动关闭
- [ ] 导入失败时不自动关闭
- [ ] 关闭前能看到导入结果

### 3. 文件排序测试

#### 音乐播单
- [ ] 导入后顺序与文件系统一致
- [ ] 不进行任何排序

#### 有声书播单
- [ ] 测试 "第01章.mp3" 格式
- [ ] 测试 "001.mp3" 格式
- [ ] 测试 "Chapter 1.mp3" 格式
- [ ] 测试混合格式
- [ ] 验证排序正确性

#### 边界情况
- [ ] 没有编号的文件排在最后
- [ ] 编号不连续的文件正确排序
- [ ] 编号位数不同的文件正确排序（1, 10, 100）

## 兼容性

- ✅ 向后兼容现有功能
- ✅ 不影响已有播单
- ✅ API 接口保持不变
- ✅ 支持本地和 Docker 环境

## 性能优化

1. **组件复用**
   - DirectorySelector 可在多处使用
   - 减少代码重复

2. **智能排序**
   - 只对需要排序的类型进行排序
   - 使用高效的排序算法

3. **用户体验**
   - 自动关闭减少操作步骤
   - 统一界面降低学习成本

## 未来改进方向

1. **更多排序选项**
   - 支持用户自定义排序规则
   - 支持按文件修改时间排序
   - 支持按文件大小排序

2. **批量编辑**
   - 导入后批量修改标题
   - 批量设置艺术家/专辑

3. **预览功能**
   - 导入前预览文件列表
   - 显示排序结果
   - 允许手动调整顺序
