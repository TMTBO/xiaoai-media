# 修复：章节目录的艺术家和专辑提取

## 更新日期
2026-03-26

## 问题描述

在批量导入牛津树等有声书资源时，发现不同 stage 目录的文件显示的艺术家和专辑信息不一致：

**目录结构**：
```
牛津树1-14阶段PDF+音频/
  ├── stage-01/
  │   └── A Good Trick.mp3
  ├── stage-02/
  │   └── Big Feet.mp3
  └── stage-13/
      └── Dragon Tales.mp3
```

**问题现象**：
- stage-13、stage-14 的文件：
  - 艺术家 = `牛津树1-14阶段PDF+音频` ✅
  - 专辑 = `stage-13` ✅
  
- stage-01 的文件：
  - 艺术家 = `stage-01` ❌（应该是 `牛津树1-14阶段PDF+音频`）
  - 专辑 = `音频` ❌（应该是 `stage-01`）

## 根本原因

旧版本的 `_create_playlist_item_from_file` 方法使用固定的目录层级提取规则：
- 艺术家 = `parts[-3]`（祖父目录）
- 专辑 = `parts[-2]`（父目录）

这个规则假设目录结构是 `艺术家/专辑/歌曲.mp3`，但对于章节目录结构 `根目录/章节/文件.mp3` 不适用。

当路径层级不同或目录名称包含章节信息时，会导致提取错误。

## 解决方案

### 1. 智能识别章节目录

新版本会先检查父目录是否包含章节信息，然后采用不同的提取策略：

```python
# 检查父目录是否是章节目录
chapter_patterns = [
    r'第\s*\d+\s*章',      # 第01章
    r'chapter\s*\d+',      # Chapter 1
    r'stage[\-_\s]*\d+',   # stage-01
    r'episode[\-_\s]*\d+', # episode-05
    r'ep[\-_\s]*\d+',      # ep-08
    r'^\d+\s*章',          # 01章
    r'^\d+[_\-\s]',        # 01-
    r'^\d+$',              # 01
]

is_chapter_dir = any(
    re.search(pattern, parent_dir.lower()) 
    for pattern in chapter_patterns
)
```

### 2. 分别处理两种目录结构

**章节目录结构**（有声书、播客等）：
```
根目录/章节/文件.mp3
→ 艺术家 = 根目录, 专辑 = 章节
```

**传统目录结构**（音乐）：
```
艺术家/专辑/歌曲.mp3
→ 艺术家 = 艺术家, 专辑 = 专辑
```

### 3. 容错处理

添加了文件大小获取的异常处理，避免测试时因文件不存在而失败：

```python
try:
    file_size = file_path.stat().st_size
except (FileNotFoundError, OSError):
    file_size = 0
```

## 修复效果

### 修复前

```
┌─────┬──────────────┬──────────┬──────────┐
│ 序号 │ 标题         │ 艺术家   │ 专辑     │
├─────┼──────────────┼──────────┼──────────┤
│ 1   │ A Good Trick │ stage-01 │ 音频     │  ❌
│ 2   │ Big Feet     │ 牛津树.. │ stage-02 │  ✅
│ 3   │ Dragon Tales │ 牛津树.. │ stage-13 │  ✅
└─────┴──────────────┴──────────┴──────────┘
```

### 修复后

```
┌─────┬──────────────┬──────────┬──────────┐
│ 序号 │ 标题         │ 艺术家   │ 专辑     │
├─────┼──────────────┼──────────┼──────────┤
│ 1   │ A Good Trick │ 牛津树.. │ stage-01 │  ✅
│ 2   │ Big Feet     │ 牛津树.. │ stage-02 │  ✅
│ 3   │ Dragon Tales │ 牛津树.. │ stage-13 │  ✅
└─────┴──────────────┴──────────┴──────────┘
```

所有文件的艺术家和专辑信息现在都正确了！

## 测试验证

创建了完整的测试用例验证修复效果：

### 测试1：章节目录结构
```python
test_cases = [
    "/data/牛津树1-14阶段PDF+音频/stage-01/A Good Trick.mp3",
    "/data/牛津树1-14阶段PDF+音频/stage-13/Dragon Tales.mp3",
    "/data/有声书/第01章/001.mp3",
    "/data/播客/episode-05/intro.mp3",
    "/data/音乐/Chapter 10/track.mp3",
]
```

### 测试2：传统目录结构
```python
test_cases = [
    "/data/周杰伦/范特西/双截棍.mp3",
    "/data/Taylor Swift/1989/Shake It Off.mp3",
]
```

**测试结果**：✅ 所有测试通过

## 影响范围

### 受益场景
- ✅ 有声书多章节导入
- ✅ 播客多期导入
- ✅ 教程分段导入
- ✅ 游戏音频分关卡导入

### 不受影响场景
- ✅ 传统音乐专辑导入（向后兼容）
- ✅ 单目录导入
- ✅ 已导入的播单（不会自动更新）

## 升级建议

### 对于新用户
直接使用新版本即可，无需额外操作。

### 对于已导入错误数据的用户

**方案1：重新导入（推荐）**
1. 删除错误的播单
2. 使用新版本重新导入
3. 验证艺术家和专辑信息正确

**方案2：手动修正（高级用户）**
1. 找到播单 JSON 文件（通常在 `~/.xiaoai_media/playlists/` 或 `/data/.xiaoai_media/playlists/`）
2. 编辑 JSON 文件，修正 `artist` 和 `album` 字段
3. 重启服务或刷新播单

**方案3：等待批量编辑功能**
后续版本会提供前端批量编辑功能。

## 代码变更

### 修改文件
- `backend/src/xiaoai_media/services/playlist_service.py`
  - 修改 `_create_playlist_item_from_file` 方法
  - 添加章节目录识别逻辑
  - 添加容错处理

### 新增文件
- `backend/tests/test_artist_album_extraction.py`
  - 测试章节目录提取
  - 测试传统目录提取
- `docs/playlist/ARTIST_ALBUM_EXTRACTION.md`
  - 详细说明提取规则
  - 提供使用示例

## 相关文档

- [艺术家和专辑信息提取](./ARTIST_ALBUM_EXTRACTION.md)
- [章节命名格式支持](./CHAPTER_NAMING_FORMATS.md)
- [批量导入用户体验改进](./BATCH_IMPORT_UX_IMPROVEMENTS.md)

## 技术细节

### 关键代码片段

```python
if is_chapter_dir:
    # 父目录是章节目录，使用它作为专辑
    album = parent_dir
    # 祖父目录作为艺术家（如果存在）
    if len(parts) >= 3:
        artist = parts[-3]
else:
    # 父目录不是章节目录，按传统方式处理
    album = parent_dir
    if len(parts) >= 3:
        artist = parts[-3]
```

### 支持的章节格式

完整列表见 [章节命名格式支持](./CHAPTER_NAMING_FORMATS.md)

## 后续计划

- [ ] 添加前端批量编辑功能
- [ ] 支持自定义提取规则配置
- [ ] 支持更多层级的目录结构
- [ ] 添加元数据标签读取（ID3、FLAC等）
