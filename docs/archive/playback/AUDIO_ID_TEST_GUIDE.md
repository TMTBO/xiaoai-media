# audio_id 时间戳方案测试指南

## 修改内容

已将 `client.py` 中的固定 `audio_id` 改为基于时间戳动态生成：

```python
# 修改前
audio_id = "1582971365183456177"  # 固定值

# 修改后
import time
audio_id = str(int(time.time() * 1000000))  # 微秒级时间戳
```

## 快速测试步骤

### 1. 重启后端服务

```bash
# 如果使用 make dev
make dev

# 或者如果使用 Docker
docker-compose restart
```

### 2. 测试方法 A：使用测试脚本（推荐）

```bash
cd test/playback
python test_audio_id_timestamp.py
```

这个脚本会：
- ✅ 测试 audio_id 生成逻辑
- ✅ 验证 ID 唯一性
- ✅ 可选：实际播放测试

### 3. 测试方法 B：手动测试

1. 打开前端管理界面：http://localhost:8000
2. 搜索并播放一首歌曲
3. 等待歌曲播放完成（或手动停止）
4. 立即播放另一首歌曲
5. 观察是否能正常开始播放

### 4. 观察日志

在后端日志中查找以下关键信息：

```
=== play_url START === device=xxx, hardware=xxx, type=x, url_length=xxx
Calling play_by_music_url with audio_id=1711234567890123 (timestamp-based), cp_id=355454500
MiService: play_by_music_url result: {'code': 0, 'data': {'code': 0}}
=== play_url END === device=xxx, audio_id=1711234567890123, success=True
```

**关键点：**
- 每次播放的 `audio_id` 应该不同
- `success=True` 表示播放成功
- 连续播放时不应该出现"直接返回播放完成"的问题

## 验证清单

### ✅ 基本功能

- [ ] 单首歌曲能正常播放
- [ ] 每次播放生成不同的 audio_id
- [ ] 播放成功返回 `success=True`

### ✅ 连续播放

- [ ] 第一首歌播放完成后，能正常播放第二首
- [ ] 手动停止后，能立即播放下一首
- [ ] 快速切歌时不会出现"播放完成"错误

### ✅ 播放列表

- [ ] 播放列表能正常播放
- [ ] 自动播放下一首功能正常
- [ ] 播放监控器能正确检测歌曲切换

### ✅ 不同场景

- [ ] 语音命令播放正常
- [ ] API 调用播放正常
- [ ] 前端界面播放正常

## 预期结果

### 成功标志

1. **日志显示不同的 audio_id**
   ```
   第一次: audio_id=1711234567890123
   第二次: audio_id=1711234570456789
   第三次: audio_id=1711234573123456
   ```

2. **连续播放正常**
   - 一首歌播放完成后
   - 立即播放下一首
   - 音箱开始播放新歌曲，而不是返回"已完成"

3. **播放监控器正常**
   - 能检测到歌曲切换
   - `audio_id` 变化时触发相应事件

### 失败标志

1. **播放失败**
   - 日志显示 `success=False`
   - 音箱没有声音

2. **audio_id 被拒绝**
   - 返回错误码
   - 提示 audio_id 格式不正确

3. **播放监控器异常**
   - 无法检测歌曲切换
   - 状态更新不正常

## 问题排查

### 问题1：播放失败

**可能原因：**
- audio_id 格式不被接受
- 时间戳长度超出限制

**解决方法：**
1. 检查日志中的错误信息
2. 尝试使用更短的时间戳：`str(int(time.time() * 1000))`
3. 如果仍然失败，回滚到固定 audio_id

### 问题2：仍然出现"播放完成"

**可能原因：**
- 问题不在 audio_id
- 需要在播放前重置状态

**解决方法：**
1. 在播放前添加停止操作
2. 增加延迟等待
3. 检查是否是其他原因导致

### 问题3：播放监控器异常

**可能原因：**
- audio_id 变化影响了状态比较逻辑

**解决方法：**
1. 检查 `playback_monitor.py` 的日志
2. 确认 audio_id 比较逻辑
3. 可能需要调整监控器的实现

## 回滚方案

如果测试失败，可以快速回滚：

```python
# 在 backend/src/xiaoai_media/client.py 中
# 找到 play_url 方法，修改为：

# 回滚到固定值
audio_id = "1582971365183456177"
cp_id = "355454500"

# 删除或注释掉：
# import time
# audio_id = str(int(time.time() * 1000000))
```

然后重启服务。

## 反馈

测试完成后，请记录：

1. **测试环境**
   - 音箱型号：
   - 硬件版本：
   - 固件版本：

2. **测试结果**
   - 基本播放：✅/❌
   - 连续播放：✅/❌
   - 播放列表：✅/❌
   - 播放监控：✅/❌

3. **遇到的问题**
   - 问题描述：
   - 错误日志：
   - 复现步骤：

4. **建议**
   - 是否保留此方案：
   - 需要改进的地方：
   - 其他建议：

## 相关文档

- [audio_id 调研报告](AUDIO_ID_RESEARCH.md)
- [播放问题排查](PLAYBACK_TROUBLESHOOTING.md)
- [快速播放指南](QUICK_PLAYBACK_GUIDE.md)
