# 艺术家和专辑信息提取

## 概述

批量导入音频文件时，系统会自动从文件路径中提取艺术家和专辑信息。本文档说明提取规则和逻辑。

## 提取规则

### 1. 章节目录结构（推荐用于有声书、播客等）

当父目录名包含章节信息时，系统会识别为章节目录结构：

```
根目录/
  ├── 章节目录1/
  │   └── 文件.mp3
  └── 章节目录2/
      └── 文件.mp3
```

**提取规则**：
- 标题 = 文件名（去除扩展名）
- 艺术家 = 根目录名
- 专辑 = 章节目录名

**示例1：牛津树**
```
路径: /data/牛津树1-14阶段PDF+音频/stage-01/A Good Trick.mp3

提取结果:
- 标题: A Good Trick
- 艺术家: 牛津树1-14阶段PDF+音频
- 专辑: stage-01
```

**示例2：有声书**
```
路径: /data/三体/第01章/序章.mp3

提取结果:
- 标题: 序章
- 艺术家: 三体
- 专辑: 第01章
```

**示例3：播客**
```
路径: /data/科技播客/episode-05/AI的未来.mp3

提取结果:
- 标题: AI的未来
- 艺术家: 科技播客
- 专辑: episode-05
```

### 2. 传统目录结构（用于音乐）

当父目录名不包含章节信息时，系统会识别为传统目录结构：

```
艺术家/
  └── 专辑/
      └── 歌曲.mp3
```

**提取规则**：
- 标题 = 文件名（去除扩展名）
- 艺术家 = 祖父目录名
- 专辑 = 父目录名

**示例1：中文歌曲**
```
路径: /data/周杰伦/范特西/双截棍.mp3

提取结果:
- 标题: 双截棍
- 艺术家: 周杰伦
- 专辑: 范特西
```

**示例2：英文歌曲**
```
路径: /data/Taylor Swift/1989/Shake It Off.mp3

提取结果:
- 标题: Shake It Off
- 艺术家: Taylor Swift
- 专辑: 1989
```

## 章节目录识别规则

系统通过以下正则表达式识别章节目录：

| 格式 | 正则表达式 | 示例 |
|------|-----------|------|
| 中文章节 | `第\s*\d+\s*章` | 第01章、第 1 章 |
| 英文章节 | `chapter\s*\d+` | Chapter 1、Chapter01 |
| Stage | `stage[\-_\s]*\d+` | stage-01、stage_01 |
| Episode | `episode[\-_\s]*\d+` | episode-05、episode_05 |
| EP | `ep[\-_\s]*\d+` | ep-08、ep_08 |
| 数字章节 | `^\d+\s*章` | 01章、1 章 |
| 前缀数字 | `^\d+[_\-\s]` | 01-、01_ |
| 纯数字 | `^\d+$` | 01、1 |

匹配时不区分大小写。

## 对比示例

### 场景1：牛津树（章节目录）

```
目录结构:
/data/牛津树1-14阶段PDF+音频/
  ├── stage-01/
  │   ├── A Good Trick.mp3
  │   └── At the Park.mp3
  ├── stage-02/
  │   └── Big Feet.mp3
  └── stage-13/
      └── Dragon Tales.mp3

导入结果:
┌─────┬──────────────┬────────────────────┬──────────┐
│ 序号 │ 标题         │ 艺术家             │ 专辑     │
├─────┼──────────────┼────────────────────┼──────────┤
│ 1   │ A Good Trick │ 牛津树1-14阶段...  │ stage-01 │
│ 2   │ At the Park  │ 牛津树1-14阶段...  │ stage-01 │
│ 3   │ Big Feet     │ 牛津树1-14阶段...  │ stage-02 │
│ 4   │ Dragon Tales │ 牛津树1-14阶段...  │ stage-13 │
└─────┴──────────────┴────────────────────┴──────────┘

✅ 所有文件的艺术家都是 "牛津树1-14阶段PDF+音频"
✅ 专辑名对应各自的 stage 目录
```

### 场景2：音乐专辑（传统目录）

```
目录结构:
/data/周杰伦/
  ├── 范特西/
  │   ├── 双截棍.mp3
  │   └── 爱在西元前.mp3
  └── 叶惠美/
      └── 以父之名.mp3

导入结果:
┌─────┬──────────────┬──────────┬──────────┐
│ 序号 │ 标题         │ 艺术家   │ 专辑     │
├─────┼──────────────┼──────────┼──────────┤
│ 1   │ 双截棍       │ 周杰伦   │ 范特西   │
│ 2   │ 爱在西元前   │ 周杰伦   │ 范特西   │
│ 3   │ 以父之名     │ 周杰伦   │ 叶惠美   │
└─────┴──────────────┴──────────┴──────────┘

✅ 艺术家统一为 "周杰伦"
✅ 专辑名对应各自的专辑目录
```

## 常见问题

### Q1: 为什么我的 stage-01 显示的艺术家和专辑不对？

**A**: 这通常是因为旧版本的提取逻辑没有识别章节目录。请确保使用最新版本，新版本会自动识别 stage-XX 格式的章节目录。

**修复前**：
- 艺术家: stage-01
- 专辑: 音频

**修复后**：
- 艺术家: 牛津树1-14阶段PDF+音频
- 专辑: stage-01

### Q2: 如何让系统识别自定义的章节格式？

**A**: 修改 `playlist_service.py` 中的 `_create_playlist_item_from_file` 方法，在 `chapter_patterns` 列表中添加你的正则表达式。

例如，添加 `part-XX` 格式：
```python
chapter_patterns = [
    # ... 现有格式 ...
    r'part[\-_\s]*\d+',  # part-01、part_01
]
```

### Q3: 我的目录结构是 艺术家/年份/专辑/歌曲，怎么办？

**A**: 当前系统只支持两层目录结构。建议调整目录结构为：
- 章节内容：根目录/章节/文件
- 音乐内容：艺术家/专辑/文件

或者手动编辑导入后的播单项信息。

### Q4: 可以在导入后修改艺术家和专辑信息吗？

**A**: 目前前端界面不支持批量修改，但可以：
1. 在导入前调整目录结构
2. 直接编辑播单 JSON 文件（高级用户）
3. 等待后续版本支持批量编辑功能

## 技术实现

### 核心代码

```python
@staticmethod
def _create_playlist_item_from_file(file_path: Path) -> PlaylistItem:
    """从文件路径创建播单项"""
    import re
    
    title = file_path.stem
    parts = file_path.parts
    artist = ""
    album = ""
    
    if len(parts) >= 2:
        parent_dir = parts[-2]  # 父目录
        
        # 检查父目录是否是章节目录
        chapter_patterns = [
            r'第\s*\d+\s*章',
            r'chapter\s*\d+',
            r'stage[\-_\s]*\d+',
            r'episode[\-_\s]*\d+',
            r'ep[\-_\s]*\d+',
            r'^\d+\s*章',
            r'^\d+[_\-\s]',
            r'^\d+$',
        ]
        
        is_chapter_dir = any(
            re.search(pattern, parent_dir.lower()) 
            for pattern in chapter_patterns
        )
        
        if is_chapter_dir:
            # 章节目录结构
            album = parent_dir
            if len(parts) >= 3:
                artist = parts[-3]
        else:
            # 传统目录结构
            album = parent_dir
            if len(parts) >= 3:
                artist = parts[-3]
    
    return PlaylistItem(
        title=title,
        artist=artist,
        album=album,
        url=f"file://{file_path.absolute()}",
        audio_id="",
        custom_params={...}
    )
```

## 相关文档

- [批量导入功能指南](./BATCH_IMPORT_GUIDE.md)
- [章节命名格式支持](./CHAPTER_NAMING_FORMATS.md)
- [批量导入用户体验改进](./BATCH_IMPORT_UX_IMPROVEMENTS.md)
