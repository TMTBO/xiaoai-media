# 自然排序算法实现

## 概述

本项目采用了自然排序（Natural Sort）算法来对有声书、播客等媒体文件进行排序，参考了 audiobookshelf 和 ECMAScript Intl.Collator 的实现思路。

## 什么是自然排序？

自然排序是一种更符合人类直觉的排序方式，能够正确处理文件名中的数字。

### 传统排序 vs 自然排序

**传统字母排序：**
```
Chapter 1
Chapter 10
Chapter 2
Chapter 3
```

**自然排序：**
```
Chapter 1
Chapter 2
Chapter 3
Chapter 10
```

## 算法原理

### 核心思想

将字符串分解为数字部分和非数字部分，分别进行比较：
- 数字部分按数值大小比较
- 非数字部分按字母顺序比较

### 实现步骤

1. **分解字符串**
   ```python
   "Chapter 10" -> ["Chapter ", "10"]
   ```

2. **转换数字部分**
   ```python
   ["Chapter ", "10"] -> [(1, "chapter "), (0, 10)]
   ```

3. **生成排序键**
   - 数字：`(0, 整数值)` - 类型标识 0
   - 字符串：`(1, 字符串值)` - 类型标识 1

### 为什么使用元组？

使用 `(类型, 值)` 元组的原因：
1. **类型安全**：避免 int 和 str 直接比较导致的错误
2. **优先级控制**：数字（类型 0）排在字符串（类型 1）前面
3. **可比较性**：元组之间可以直接比较

## 代码实现

```python
@staticmethod
def _natural_sort_key(text: str) -> list:
    """生成自然排序的键"""
    import re
    
    # 分解字符串为数字和非数字部分
    parts = re.split(r'(\d+)', text.lower())
    
    # 转换为可比较的元组
    result = []
    for part in parts:
        if part:
            if part.isdigit():
                result.append((0, int(part)))  # 数字
            else:
                result.append((1, part))  # 字符串
    
    return result
```

## 使用示例

### 示例 1: 基本章节排序

```python
files = [
    "Chapter 10",
    "Chapter 2",
    "Chapter 1",
]

sorted_files = sorted(files, key=PlaylistService._natural_sort_key)
# 结果: ["Chapter 1", "Chapter 2", "Chapter 10"]
```

### 示例 2: 中文章节

```python
files = [
    "第10章",
    "第2章",
    "第1章",
]

sorted_files = sorted(files, key=PlaylistService._natural_sort_key)
# 结果: ["第1章", "第2章", "第10章"]
```

### 示例 3: 前导零

```python
files = [
    "010",
    "002",
    "001",
]

sorted_files = sorted(files, key=PlaylistService._natural_sort_key)
# 结果: ["001", "002", "010"]
```

### 示例 4: 复杂格式（Moby Dick）

```python
files = [
    "Chapter 010",
    "Chapter 001-002",
    "Chapter 003",
    "Chapter 004-007",
    "Chapter 000: Etymology and Extracts",
]

sorted_files = sorted(files, key=PlaylistService._natural_sort_key)
# 结果:
# ["Chapter 000: Etymology and Extracts",
#  "Chapter 001-002",
#  "Chapter 003",
#  "Chapter 004-007",
#  "Chapter 010"]
```

## 排序规则详解

### 1. 大小写不敏感

```python
"Chapter 1" == "chapter 1" == "CHAPTER 1"
```

所有字符串在比较前都会转换为小写。

### 2. 数字优先

```python
"001" < "Chapter 1" < "第1章"
```

纯数字文件名排在最前面。

### 3. 多个数字的处理

```python
"Book 1 Chapter 5" < "Book 1 Chapter 10" < "Book 2 Chapter 1"
```

从左到右依次比较每个数字。

### 4. 前导零的处理

```python
"001" == "01" == "1"  # 数值相同
```

前导零会被忽略，按数值比较。

## 与其他实现的比较

### Python natsort 库

```python
from natsort import natsorted
natsorted(files)
```

我们的实现更轻量，无需外部依赖。

### JavaScript Intl.Collator

```javascript
const collator = new Intl.Collator(undefined, {
  numeric: true,
  sensitivity: 'base'
});
files.sort((a, b) => collator.compare(a, b));
```

我们的 Python 实现提供了类似的功能。

### audiobookshelf

audiobookshelf 使用 JavaScript 的 natural sort 库，我们的实现遵循相同的原理。

## 性能分析

### 时间复杂度

- 单个文件名处理：O(n)，n 为文件名长度
- 排序 m 个文件：O(m log m)

### 空间复杂度

- O(m * k)，m 为文件数量，k 为平均文件名长度

### 性能测试

```python
# 1000 个文件
import time

files = [f"Chapter {i}" for i in range(1000, 0, -1)]

start = time.time()
sorted_files = sorted(files, key=PlaylistService._natural_sort_key)
end = time.time()

print(f"排序 1000 个文件耗时: {(end - start) * 1000:.2f}ms")
# 预期: < 50ms
```

## 边界情况处理

### 1. 空字符串

```python
_natural_sort_key("") -> []
```

### 2. 纯数字

```python
_natural_sort_key("123") -> [(0, 123)]
```

### 3. 纯字母

```python
_natural_sort_key("abc") -> [(1, "abc")]
```

### 4. 特殊字符

```python
_natural_sort_key("Chapter-01") -> [(1, "chapter-"), (0, 1)]
```

### 5. Unicode 字符

```python
_natural_sort_key("第1章") -> [(1, "第"), (0, 1), (1, "章")]
```

## 测试用例

### 基本测试

```python
def test_natural_sort_basic():
    files = ["10", "2", "1"]
    result = sorted(files, key=PlaylistService._natural_sort_key)
    assert result == ["1", "2", "10"]
```

### 中文测试

```python
def test_natural_sort_chinese():
    files = ["第10章", "第2章", "第1章"]
    result = sorted(files, key=PlaylistService._natural_sort_key)
    assert result == ["第1章", "第2章", "第10章"]
```

### 混合格式测试

```python
def test_natural_sort_mixed():
    files = ["Chapter 5", "001", "第10章", "Episode 2"]
    result = sorted(files, key=PlaylistService._natural_sort_key)
    # 验证排序正确
```

## 应用场景

### 1. 有声书章节排序

```python
playlist_type = "audiobook"
if PlaylistService._should_sort_files(playlist_type):
    items.sort(key=lambda item: PlaylistService._natural_sort_key(
        item.custom_params.get("file_name", item.title)
    ))
```

### 2. 播客集数排序

```python
playlist_type = "podcast"
# 自动使用自然排序
```

### 3. 音乐不排序

```python
playlist_type = "music"
# 保持原始顺序，不排序
```

## 常见问题

### Q: 为什么音乐不排序？

A: 音乐通常按专辑顺序或用户偏好排列，不需要按文件名排序。

### Q: 如何处理不同语言的文件名？

A: 算法对所有语言都有效，因为它只关注数字和非数字的区分。

### Q: 前导零会影响排序吗？

A: 不会，"001"、"01"、"1" 会被视为相同的数字 1。

### Q: 如何处理多个数字？

A: 从左到右依次比较，例如 "Book 1 Chapter 10" < "Book 2 Chapter 1"。

### Q: 性能如何？

A: 对于常见的文件数量（< 10000），性能非常好，通常 < 100ms。

## 参考资料

1. [Natural Alphanumeric Sorting in JavaScript](https://dbushell.com/2021/05/17/javascript-natural-alphanumeric-sorting/)
2. [ECMAScript Intl.Collator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Collator)
3. [audiobookshelf](https://github.com/advplyr/audiobookshelf)
4. [Natural Sort Algorithm](https://en.wikipedia.org/wiki/Natural_sort_order)

## 未来改进

1. **支持更多语言特性**
   - 处理重音字符
   - 支持不同的排序规则

2. **性能优化**
   - 缓存排序键
   - 并行排序

3. **自定义排序规则**
   - 允许用户定义排序优先级
   - 支持自定义正则表达式

## 总结

自然排序算法通过智能识别文件名中的数字部分，提供了更符合人类直觉的排序方式。我们的实现：

- ✅ 轻量级，无外部依赖
- ✅ 支持多种语言和格式
- ✅ 性能优秀
- ✅ 易于理解和维护
- ✅ 参考业界最佳实践

这使得有声书、播客等媒体文件能够按照正确的章节/集数顺序播放，极大提升了用户体验。
