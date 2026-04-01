# 时区配置热重载说明

## 概述

时区配置支持热重载，修改后无需重启服务即可生效。

## 热重载机制

### 1. 日志时间戳

日志格式化器的 `converter()` 方法每次格式化日志时都会动态读取 `config.TIMEZONE`，因此：

- **立即生效**：修改时区后，新的日志条目会立即使用新时区
- **无需重启**：不需要重启服务或重新初始化日志系统

```python
def converter(self, timestamp):
    """转换时间戳为配置的时区"""
    try:
        from xiaoai_media import config
        import zoneinfo
        tz = zoneinfo.ZoneInfo(config.TIMEZONE)  # 动态读取
        return datetime.fromtimestamp(timestamp, tz=tz)
    except Exception:
        return datetime.fromtimestamp(timestamp)
```

### 2. 定时任务调度器

调度器提供了 `update_timezone()` 方法来更新时区：

```python
def update_timezone(self, timezone: str):
    """更新调度器时区"""
    try:
        self.scheduler.configure(timezone=timezone)
        _log.info("调度器时区已更新为: %s", timezone)
    except Exception as e:
        _log.error("更新调度器时区失败: %s", e, exc_info=True)
```

在配置变更回调中自动调用：

```python
# 4. 更新时区配置
if hasattr(cfg, 'TIMEZONE'):
    from xiaoai_media.services.scheduler_service import get_scheduler_service
    try:
        scheduler_service = get_scheduler_service()
        scheduler_service.update_timezone(cfg.TIMEZONE)
        logger.info("时区已更新: %s", cfg.TIMEZONE)
    except Exception as e:
        logger.error("更新时区失败: %s", e, exc_info=True)
```

### 3. 配置变更流程

```
用户修改配置
    ↓
前端调用 PUT /api/config
    ↓
ConfigService.write_user_config()
    ↓
config.reload_config()
    ↓
触发配置变更回调
    ↓
├─ 更新日志级别
├─ 重启对话监听器
├─ 重启播放控制器
└─ 更新调度器时区 ← 时区热重载
```

## 使用示例

### 通过前端界面

1. 访问"配置管理"页面
2. 在"日志配置"部分找到"时区"选项
3. 选择新的时区（如 `America/New_York`）
4. 点击"保存配置"
5. 配置立即生效，无需重启

### 通过 API

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"TIMEZONE": "Europe/London"}'
```

### 验证生效

查看日志输出，新的日志条目应该使用新时区的时间戳：

```
2026-04-01 10:30:45.123 INFO     xiaoai_media.config - 时区已更新: Europe/London
2026-04-01 10:30:45.124 INFO     xiaoai_media.services.scheduler_service - 调度器时区已更新为: Europe/London
```

## 技术细节

### 日志格式化器

- 使用 `logging.Formatter` 的 `converter()` 和 `formatTime()` 方法
- 每次格式化日志时动态读取配置
- 支持所有日志级别和日志处理器

### APScheduler 时区更新

- 使用 `scheduler.configure(timezone=...)` 方法
- 更新后，所有任务的下次执行时间会重新计算
- 已有任务的触发器定义保持不变，但按新时区解释

### 配置重载机制

- 使用回调模式通知配置变更
- 所有注册的回调函数会在 `reload_config()` 时被调用
- 支持多个回调函数，按注册顺序执行

## 限制和注意事项

### 1. 已创建的任务

已创建的定时任务会按新时区重新解释执行时间，但任务定义本身不变。

例如：
- 原任务：每天 09:00 执行（Asia/Shanghai，UTC+8）
- 改时区：Europe/London（UTC+0）
- 结果：仍然在"09:00"执行，但现在是伦敦时间的 09:00

### 2. 时区验证

系统不会验证时区标识符的有效性，如果提供无效的时区：
- 日志格式化器会回退到本地时间
- 调度器可能抛出异常

建议使用前端界面选择时区，避免手动输入错误。

### 3. 性能影响

时区热重载对性能影响极小：
- 日志格式化：每次格式化增加一次配置读取（纳秒级）
- 调度器更新：一次性操作，不影响运行时性能

## 测试

运行时区热重载测试：

```bash
cd backend
pytest tests/test_timezone_hot_reload.py -v
```

测试覆盖：
- 时区配置重新加载
- 调度器时区更新
- 日志格式化器动态读取
- 配置变更回调
- 集成测试

## 故障排查

### 时区未生效

1. 检查配置是否保存成功
2. 查看日志中是否有"时区已更新"消息
3. 验证时区标识符格式是否正确

### 调度器时区更新失败

1. 检查调度器是否已启动
2. 查看错误日志
3. 验证时区标识符是否有效

### 日志时间仍然不对

1. 确认配置已重新加载
2. 检查是否有多个日志处理器
3. 验证系统是否支持 zoneinfo 模块（Python 3.9+）

## 相关文档

- [时区配置说明](TIMEZONE_CONFIG.md)
- [配置热重载](config/CONFIG_HOT_RELOAD.md)
- [定时任务管理](FEATURES.md#定时任务)
