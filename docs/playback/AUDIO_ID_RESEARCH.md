# audio_id 调研报告

## 问题描述

在使用 `client.play_url()` 播放音频时，发现一曲播放完成后，再次调用会直接返回"播放完成"状态，无法正常播放下一首歌曲。

怀疑与 `play_by_music_url` 方法中使用的固定 `audio_id` 和 `cp_id` 有关。

## 当前实现

### client.py 中的代码

```python
# backend/src/xiaoai_media/client.py (Line 511-513)
audio_id = "1582971365183456177"
cp_id = "355454500"

result = await self._na_service.play_by_music_url(
    did, url, _type, audio_id, cp_id
)
```

### 参数说明

- `audio_id`: 音频ID，用于标识播放的音频内容
- `cp_id`: Content Provider ID（内容提供商ID），固定为 "355454500"
- `url`: 实际的音频URL
- `_type`: 播放类型（1=MUSIC带灯光，2=普通播放）

## 调研发现

### 1. audio_id 的来源

从文档 `docs/conversation/播放拦截问题分析.md` 中发现，这个固定的 `audio_id` 来自 `player_play_music` API 的数据结构：

```python
{
    "startaudioid": "1582971365183456177",
    "music": {
        "payload": {
            "audio_type": "MUSIC",
            "audio_items": [{
                "item_id": {
                    "audio_id": "1582971365183456177",
                    "cp": {
                        "album_id": "-1",
                        "episode_index": 0,
                        "id": "355454500",
                        "name": "xiaowei"
                    }
                },
                "stream": {"url": "实际音乐URL"}
            }]
        }
    }
}
```

### 2. 项目背景

本项目参考了 [xiaomusic](https://github.com/hanxi/xiaomusic) 项目的实现，使用 [miservice_fork](https://github.com/yihong0618/MiService) 库与小米音箱通信。

### 3. audio_id 在项目中的其他用途

通过搜索发现，`audio_id` 在项目中主要有两个用途：

#### 用途1：播放控制（client.py）
- 作为 `play_by_music_url` 的参数传递
- 用于标识要播放的音频

#### 用途2：播放状态监控（playback_monitor.py）
```python
# backend/src/xiaoai_media/playback_monitor.py (Line 156-182)
play_song_detail = info.get("play_song_detail", {})
audio_id = play_song_detail.get("audio_id", "")

# 用于检测歌曲是否切换
last_audio_id = last_status.get("audio_id", "")
```

播放监控器通过比较 `audio_id` 来判断是否切换了歌曲。

#### 用途3：播放列表数据（playlist_models.py）
```python
# backend/src/xiaoai_media/services/playlist_models.py
class PlaylistItem(BaseModel):
    audio_id: str = Field("", description="音频ID（如果有）")
```

播放列表中的每个项目可以有自己的 `audio_id`，但这个字段是可选的。

### 4. xiaomusic 的处理方式

根据文档引用，xiaomusic 项目也使用类似的方式：
- 使用固定的 `cp_id = "355454500"`（代表 "xiaowei" 内容提供商）
- 使用固定的 `audio_id = "1582971365183456177"`

但需要注意的是，xiaomusic 主要用于播放本地音乐文件，通过局域网HTTP服务器提供URL，每个文件的URL本身就是唯一的。

### 5. 问题分析

#### 可能的原因

固定的 `audio_id` 可能导致小米音箱认为：
1. 每次播放的都是"同一首歌"
2. 当一首歌播放完成后，音箱缓存了这个 `audio_id` 的播放状态
3. 再次用相同的 `audio_id` 播放时，音箱检查缓存发现"已播放完成"，直接返回完成状态

#### 但也有其他可能

1. **URL 的作用**: 虽然 `audio_id` 相同，但 `url` 参数不同，音箱可能主要依据 URL 来判断是否是不同的音频
2. **播放状态管理**: 问题可能不在 `audio_id`，而在于播放状态没有正确重置
3. **硬件差异**: 不同型号的音箱可能有不同的行为

## 可能的解决方案

### 方案1：生成唯一的 audio_id（推荐尝试）

```python
import time

# 基于时间戳生成唯一ID
audio_id = str(int(time.time() * 1000000))  # 微秒级时间戳
cp_id = "355454500"
```

**优点**:
- 每次播放都有唯一的ID
- 避免缓存问题
- 实现简单

**风险**:
- 不确定小米音箱是否会验证 audio_id 的格式
- 可能影响播放监控器的歌曲切换检测

### 方案2：基于 URL 哈希生成 audio_id

```python
import hashlib

# 基于URL生成稳定的ID
audio_id = str(int(hashlib.md5(url.encode()).hexdigest()[:16], 16))
cp_id = "355454500"
```

**优点**:
- 相同URL生成相同ID（可重复）
- 不同URL生成不同ID
- ID与内容相关

**缺点**:
- 如果URL带时间戳参数，每次都会生成不同ID
- 实现稍复杂

### 方案3：使用播放列表中的 audio_id

如果播放的是播放列表中的歌曲，可以使用 `PlaylistItem.audio_id`：

```python
# 如果有播放列表项的 audio_id，使用它
if item_audio_id:
    audio_id = item_audio_id
else:
    # 否则生成唯一ID
    audio_id = str(int(time.time() * 1000000))
```

**优点**:
- 利用现有数据结构
- 对播放列表更友好

**缺点**:
- 需要修改调用链，传递更多参数
- 播放列表外的播放仍需要生成ID

### 方案4：在播放前重置状态

```python
# 播放前先停止
await client.player_stop(device_id)
await asyncio.sleep(0.5)

# 然后播放
result = await self._na_service.play_by_music_url(
    did, url, _type, audio_id, cp_id
)
```

**优点**:
- 不修改 audio_id 逻辑
- 确保播放状态清空

**缺点**:
- 增加延迟
- 可能不能完全解决问题

## 建议的验证步骤

1. **先验证问题是否确实由 audio_id 引起**
   - 在日志中记录每次播放的 audio_id 和播放结果
   - 观察是否真的是 audio_id 相同导致的问题

2. **测试方案1（时间戳ID）**
   - 修改代码使用时间戳生成 audio_id
   - 测试连续播放多首歌曲
   - 观察是否解决问题

3. **检查播放监控器的影响**
   - 确认修改后播放监控器是否仍能正常工作
   - 特别是歌曲切换检测功能

4. **测试不同硬件型号**
   - 在不同型号的音箱上测试
   - 确认方案的通用性

## 参考资料

- [xiaomusic 项目](https://github.com/hanxi/xiaomusic)
- [MiService Fork](https://github.com/yihong0618/MiService)
- `docs/conversation/播放拦截问题分析.md`
- `docs/playback/PLAYBACK_TROUBLESHOOTING.md`

## 下一步行动

1. 添加详细日志，记录每次播放的 audio_id、URL 和结果
2. 复现问题，确认是否与 audio_id 相关
3. 如果确认相关，实施方案1（时间戳ID）
4. 测试验证并观察副作用
5. 根据测试结果决定是否需要调整方案

## 更新记录

- 2024-03-22: 初始调研完成
- 2024-03-22: 实施方案1（时间戳ID），添加详细日志和测试脚本

## 实施记录

### 修改内容

1. **修改 client.py 的 play_url 方法**
   - 使用 `time.time() * 1000000` 生成微秒级时间戳作为 audio_id
   - 添加详细日志标记（`=== play_url START/END ===`）
   - 在返回结果中包含 audio_id 以便追踪

2. **添加测试脚本**
   - `test/playback/test_audio_id_timestamp.py`
   - 测试 audio_id 生成逻辑
   - 测试连续播放多首歌曲

### 测试方法

#### 方法1：运行测试脚本

```bash
cd test/playback
python test_audio_id_timestamp.py
```

这个脚本会：
1. 测试 audio_id 生成逻辑的唯一性
2. 可选：连续播放 3 首测试音频
3. 验证每次生成的 audio_id 是否唯一

#### 方法2：观察实际使用日志

启动后端服务后，在播放音乐时观察日志：

```bash
# 启动服务
make dev

# 观察日志中的关键信息：
# === play_url START === device=xxx, hardware=xxx, type=x, url_length=xxx
# Calling play_by_music_url with audio_id=1234567890123456 (timestamp-based), cp_id=355454500
# === play_url END === device=xxx, audio_id=1234567890123456, success=True
```

### 预期效果

1. **每次播放生成不同的 audio_id**
   - 第一次播放：audio_id=1711234567890123
   - 第二次播放：audio_id=1711234570123456
   - 第三次播放：audio_id=1711234572345678

2. **解决连续播放问题**
   - 一首歌播放完成后
   - 再次调用 play_url 播放下一首
   - 应该能正常开始播放，而不是直接返回"播放完成"

3. **不影响播放监控器**
   - 播放监控器通过 `player_get_play_status` API 获取当前播放的 audio_id
   - 这个 audio_id 是音箱返回的，与我们传入的 audio_id 应该一致
   - 歌曲切换检测应该仍然正常工作

### 需要观察的问题

1. **audio_id 格式是否被接受**
   - 小米音箱是否接受时间戳格式的 audio_id
   - 是否有格式验证或长度限制

2. **播放监控器的兼容性**
   - 检查 `playback_monitor.py` 是否能正确识别歌曲切换
   - 观察 `audio_id` 比较逻辑是否正常

3. **不同硬件型号的表现**
   - 在不同型号的音箱上测试
   - 确认方案的通用性

### 回滚方案

如果测试发现问题，可以快速回滚到固定 audio_id：

```python
# 回滚到固定值
audio_id = "1582971365183456177"
cp_id = "355454500"
```

## 更新记录

- 2024-03-22: 初始调研完成
- 2024-03-22: 实施方案1（时间戳ID），添加详细日志和测试脚本，待验证效果
