# 重构：章节正则表达式抽离复用

## 更新日期
2026-03-26

## 重构目标

将章节识别相关的正则表达式从多个方法中抽离出来，统一管理，提高代码的可维护性和复用性。

## 重构前的问题

### 代码重复

章节正则表达式在两个地方重复定义：

1. **`_extract_directory_sort_key` 方法**（用于排序）
```python
chapter_patterns = [
    r'第\s*(\d+)\s*章',
    r'chapter\s*(\d+)',
    r'stage[\-_\s]*(\d+)',
    # ... 8个模式
]
```

2. **`_create_playlist_item_from_file` 方法**（用于识别章节目录）
```python
chapter_patterns = [
    r'第\s*\d+\s*章',
    r'chapter\s*\d+',
    r'stage[\-_\s]*\d+',
    # ... 8个模式
]
```

### 维护困难

- 添加新格式需要在两个地方同时修改
- 容易出现不一致的情况
- 代码可读性差

## 重构方案

### 1. 定义类常量

将章节正则表达式定义为 `PlaylistService` 类的常量：

```python
class PlaylistService:
    """播单业务逻辑服务"""
    
    # 章节目录识别的正则表达式模式
    # 用于识别目录名中的章节信息，支持多种命名格式
    CHAPTER_PATTERNS = [
        r'第\s*(\d+)\s*章',      # 第01章、第 1 章
        r'chapter\s*(\d+)',      # Chapter 1、Chapter01
        r'stage[\-_\s]*(\d+)',   # stage-02、stage_02、stage 02、stage02
        r'episode[\-_\s]*(\d+)', # episode-02、episode_02、episode 02
        r'ep[\-_\s]*(\d+)',      # ep-02、ep_02、ep 02
        r'^(\d+)\s*章',          # 01章、1 章
        r'^(\d+)[_\-\s]',        # 01-、01_、01 开头
        r'^(\d+)$',              # 纯数字目录名
    ]
```

### 2. 创建辅助方法

#### `_is_chapter_directory(dir_name: str) -> bool`

检查目录名是否包含章节信息：

```python
@staticmethod
def _is_chapter_directory(dir_name: str) -> bool:
    """检查目录名是否包含章节信息
    
    Args:
        dir_name: 目录名称
        
    Returns:
        是否为章节目录
    """
    import re
    
    for pattern in PlaylistService.CHAPTER_PATTERNS:
        if re.search(pattern, dir_name.lower()):
            return True
    return False
```

#### `_extract_chapter_number(dir_name: str) -> int | float`

从目录名中提取章节号：

```python
@staticmethod
def _extract_chapter_number(dir_name: str) -> int | float:
    """从目录名中提取章节号
    
    Args:
        dir_name: 目录名称
        
    Returns:
        章节号（整数），如果没有找到则返回 float('inf')
    """
    import re
    
    for pattern in PlaylistService.CHAPTER_PATTERNS:
        match = re.search(pattern, dir_name.lower())
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue
    
    return float('inf')  # 没有章节号，排在最后
```

### 3. 更新使用方

#### 更新 `_extract_directory_sort_key`

**重构前**（30+ 行）：
```python
@staticmethod
def _extract_directory_sort_key(file_path: str) -> tuple:
    import re
    from pathlib import Path
    
    path = Path(file_path)
    parent_dir = path.parent.name if path.parent else ""
    file_name = path.name
    
    # 定义章节模式
    chapter_patterns = [
        r'第\s*(\d+)\s*章',
        # ... 更多模式
    ]
    
    # 循环匹配
    chapter_num = float('inf')
    for pattern in chapter_patterns:
        match = re.search(pattern, parent_dir.lower())
        if match:
            try:
                chapter_num = int(match.group(1))
                break
            except (ValueError, IndexError):
                continue
    
    return (chapter_num, parent_dir, file_name)
```

**重构后**（10 行）：
```python
@staticmethod
def _extract_directory_sort_key(file_path: str) -> tuple:
    from pathlib import Path
    
    path = Path(file_path)
    parent_dir = path.parent.name if path.parent else ""
    file_name = path.name
    
    # 提取章节号
    chapter_num = PlaylistService._extract_chapter_number(parent_dir)
    
    return (chapter_num, parent_dir, file_name)
```

#### 更新 `_create_playlist_item_from_file`

**重构前**（20+ 行章节识别逻辑）：
```python
# 检查父目录是否是章节目录
chapter_patterns = [
    r'第\s*\d+\s*章',
    # ... 更多模式
]

is_chapter_dir = False
for pattern in chapter_patterns:
    if re.search(pattern, parent_dir.lower()):
        is_chapter_dir = True
        break
```

**重构后**（1 行）：
```python
# 检查父目录是否是章节目录
is_chapter_dir = PlaylistService._is_chapter_directory(parent_dir)
```

## 重构效果

### 代码行数减少

| 方法 | 重构前 | 重构后 | 减少 |
|------|--------|--------|------|
| `_extract_directory_sort_key` | ~35 行 | ~15 行 | -57% |
| `_create_playlist_item_from_file` | ~60 行 | ~45 行 | -25% |
| 总计 | ~95 行 | ~60 行 + 30 行辅助方法 | -5% |

虽然总行数略有增加（因为添加了辅助方法），但代码结构更清晰，可维护性大幅提升。

### 可维护性提升

✅ **单一数据源**：章节模式只在一个地方定义
✅ **易于扩展**：添加新格式只需修改 `CHAPTER_PATTERNS`
✅ **代码复用**：两个辅助方法可在其他地方使用
✅ **可读性强**：方法名清晰表达意图

### 功能不变

✅ 所有测试用例通过
✅ 向后兼容
✅ 性能无影响

## 使用示例

### 添加新的章节格式

现在只需在一个地方添加：

```python
class PlaylistService:
    CHAPTER_PATTERNS = [
        # ... 现有格式 ...
        r'part[\-_\s]*(\d+)',    # 新增：part-01、part_01
        r'section[\-_\s]*(\d+)', # 新增：section-01
    ]
```

所有使用章节识别的功能都会自动支持新格式！

### 在其他地方使用

如果将来需要在其他方法中识别章节目录：

```python
# 检查是否为章节目录
if PlaylistService._is_chapter_directory("stage-02"):
    print("这是一个章节目录")

# 提取章节号
chapter_num = PlaylistService._extract_chapter_number("episode-05")
print(f"章节号: {chapter_num}")  # 输出: 章节号: 5
```

## 测试验证

### 测试1：目录排序
```bash
$ python backend/tests/test_directory_sort.py
✅ 所有测试通过！
```

### 测试2：艺术家专辑提取
```bash
$ python backend/tests/test_artist_album_extraction.py
✅ 所有测试通过！
```

## 技术细节

### 正则表达式说明

所有正则表达式都包含捕获组 `(\d+)` 用于提取章节号：

```python
r'stage[\-_\s]*(\d+)'
#               ^^^^^ 捕获组，提取数字部分
```

### 类型注解

使用 Python 3.10+ 的类型注解：

```python
def _extract_chapter_number(dir_name: str) -> int | float:
    #                         ^^^^^^^^^^^    ^^^^^^^^^^^
    #                         参数类型        返回类型
```

返回 `int | float` 是因为：
- 找到章节号时返回 `int`
- 没有章节号时返回 `float('inf')`（用于排序）

## 后续优化建议

### 1. 配置化

可以考虑将章节模式移到配置文件：

```python
# config.py
CHAPTER_PATTERNS = [
    r'第\s*(\d+)\s*章',
    # ...
]
```

### 2. 缓存优化

如果性能成为瓶颈，可以添加缓存：

```python
from functools import lru_cache

@staticmethod
@lru_cache(maxsize=1000)
def _extract_chapter_number(dir_name: str) -> int | float:
    # ...
```

### 3. 自定义模式

允许用户在 `user_config.py` 中自定义章节模式：

```python
# user_config.py
CUSTOM_CHAPTER_PATTERNS = [
    r'part[\-_\s]*(\d+)',
]
```

## 相关文档

- [章节命名格式支持](./CHAPTER_NAMING_FORMATS.md)
- [艺术家和专辑信息提取](./ARTIST_ALBUM_EXTRACTION.md)
- [批量导入用户体验改进](./BATCH_IMPORT_UX_IMPROVEMENTS.md)

## 总结

这次重构通过抽离章节正则表达式，实现了：

1. ✅ 消除代码重复
2. ✅ 提高可维护性
3. ✅ 增强代码复用性
4. ✅ 保持功能完整性
5. ✅ 通过所有测试

是一次成功的代码优化！
