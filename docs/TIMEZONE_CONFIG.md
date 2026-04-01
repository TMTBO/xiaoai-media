# 时区配置说明

## 概述

从本版本开始，时区配置已从环境变量迁移到 `user_config.py` 配置文件中，并提供了前端配置界面。

## 配置方式

### 1. 通过前端界面配置（推荐）

1. 访问前端管理界面
2. 进入"配置管理"页面
3. 在"日志配置"部分找到"时区"选项
4. 从下拉列表中选择合适的时区，或手动输入 IANA 时区标识符
5. 点击"保存配置"

### 2. 通过配置文件配置

在 `user_config.py` 中添加或修改：

```python
# 时区配置（IANA 时区标识符）
TIMEZONE = "Asia/Shanghai"  # 北京时间
```

## 常用时区列表

| 时区标识符 | 说明 | UTC 偏移 |
|-----------|------|---------|
| `Asia/Shanghai` | 中国标准时间（北京时间） | UTC+8 |
| `Asia/Hong_Kong` | 香港时间 | UTC+8 |
| `Asia/Tokyo` | 日本标准时间 | UTC+9 |
| `Asia/Singapore` | 新加坡时间 | UTC+8 |
| `Europe/London` | 英国时间 | UTC+0/+1 |
| `Europe/Paris` | 中欧时间 | UTC+1/+2 |
| `America/New_York` | 美国东部时间 | UTC-5/-4 |
| `America/Los_Angeles` | 美国太平洋时间 | UTC-8/-7 |
| `UTC` | 协调世界时 | UTC+0 |

完整的时区列表请参考：https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## 影响范围

时区配置会影响以下功能：

1. **日志时间戳**：所有日志输出的时间将使用配置的时区
2. **定时任务**：定时任务的执行时间将基于配置的时区
3. **API 响应**：涉及时间的 API 响应将使用配置的时区

## 默认值

如果未配置时区，系统默认使用 `Asia/Shanghai`（北京时间）。

## 配置生效

### 热重载支持

时区配置支持热重载，无需重启服务：

1. **通过前端界面修改**：修改后点击"保存配置"，配置会立即生效
2. **通过 API 修改**：调用 `/api/config` 接口更新配置后自动生效
3. **手动修改配置文件**：需要调用 `/api/config` 接口触发重载

### 热重载影响范围

- **日志时间戳**：立即生效，新的日志将使用新时区
- **定时任务调度器**：立即生效，已有任务的下次执行时间会根据新时区重新计算
- **已创建的任务**：保持原有的触发时间定义，但会按新时区解释

### 完全重启

虽然支持热重载，但以下情况建议重启服务以确保完全生效：

1. 首次配置时区
2. 时区变更跨越多个时区（如从 UTC+8 到 UTC-5）
3. 有大量定时任务需要重新计算执行时间

重启命令：
```bash
# Docker 环境
docker-compose restart

# 开发环境
make restart
```

## 注意事项

1. **时区标识符格式**：必须使用标准的 IANA 时区标识符（如 `Asia/Shanghai`），不支持缩写（如 `CST`）
2. **Docker 环境**：不再需要设置 `TZ` 环境变量，时区完全由 `user_config.py` 控制
3. **夏令时**：使用 IANA 时区标识符会自动处理夏令时转换
4. **热重载**：时区配置支持热重载，通过前端或 API 修改后立即生效

如果之前通过环境变量 `TZ` 设置时区：

1. 将 `TZ` 环境变量的值添加到 `user_config.py` 的 `TIMEZONE` 配置项
2. 移除 Docker Compose 或 Dockerfile 中的 `TZ` 环境变量设置
3. 重启服务

## 故障排查

### 日志时间不正确

1. 检查 `user_config.py` 中的 `TIMEZONE` 配置是否正确
2. 确认时区标识符格式是否符合 IANA 标准
3. 重启服务使配置生效

### 定时任务执行时间不对

1. 检查定时任务的 Cron 表达式是否正确
2. 确认 `TIMEZONE` 配置与预期一致
3. 查看日志中的"下次执行时间"是否符合预期

## 示例

### 配置北京时间

```python
# user_config.py
TIMEZONE = "Asia/Shanghai"
```

### 配置美国东部时间

```python
# user_config.py
TIMEZONE = "America/New_York"
```

### 配置 UTC 时间

```python
# user_config.py
TIMEZONE = "UTC"
```
