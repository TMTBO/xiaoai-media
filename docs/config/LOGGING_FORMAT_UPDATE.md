# 日志格式统一更新

## 更新日期
2026-03-26

## 问题描述
应用程序的日志格式与uvicorn的访问日志格式不一致，导致日志输出混乱，难以阅读。

### 原有格式
```
2026-03-26 14:06:54,328 INFO xiaoai_media.services.playlist_service — Removed item 0 from playlist: 我的_1774335884330
INFO:     127.0.0.1:56398 - "POST /api/playlists/%E6%88%91%E7%9A%84_1774335884330/import HTTP/1.1" 200 OK
```

### 新格式
```
2026-03-26 14:06:54 INFO     xiaoai_media.services.playlist_service - Removed item 0 from playlist: 我的_1774335884330
2026-03-26 14:06:54 INFO     uvicorn.access - 127.0.0.1:56398 - "POST /api/playlists/%E6%88%91%E7%9A%84_1774335884330/import HTTP/1.1" 200 OK
```

## 修改内容

### 1. 应用日志格式配置
修改了`backend/src/xiaoai_media/api/main.py`中的日志配置：

```python
# 新格式
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

### 2. Uvicorn日志配置
创建了统一的日志配置模块：

**文件：`backend/src/xiaoai_media/log_config.py`**
- 动态生成uvicorn日志配置
- 支持从环境变量`LOG_LEVEL`读取日志级别
- 统一应用日志和uvicorn日志的格式

**文件：`backend/run.py`**
- 启动脚本，使用动态日志配置启动uvicorn
- 支持环境变量配置（HOST, PORT, RELOAD, LOG_LEVEL）

**文件：`backend/log_config.json`**
- 静态日志配置文件（备用）
- 可用于直接使用uvicorn命令启动

### 3. 格式说明
- `%(asctime)s`: 时间戳，格式为`YYYY-MM-DD HH:MM:SS`
- `%(levelname)-8s`: 日志级别，左对齐，固定8个字符宽度
- `%(name)s`: 日志记录器名称（模块名）
- `%(message)s`: 日志消息

### 4. 访问日志格式
```
%(asctime)s %(levelname)-8s %(name)s - %(client_addr)s - "%(request_line)s" %(status_code)s
```

## 效果对比

### 修改前
```
2026-03-26 14:06:54,328 INFO xiaoai_media.services.playlist_service — Removed item 0
INFO:     127.0.0.1:56398 - "POST /api/playlists/..." 200 OK
INFO:     Application startup complete.
```
- 时间戳格式不同（毫秒 vs 无时间戳）
- 分隔符不同（— vs -）
- 对齐方式不同
- uvicorn日志缺少时间戳

### 修改后
```
2026-03-26 14:06:54 INFO     xiaoai_media.services.playlist_service - Removed item 0
2026-03-26 14:06:54 INFO     uvicorn.access - 127.0.0.1:56398 - "POST /api/playlists/..." 200 OK
2026-03-26 14:06:54 INFO     uvicorn - Application startup complete.
```
- 时间戳格式统一（秒级精度）
- 分隔符统一（-）
- 日志级别对齐
- 所有日志都包含时间戳
- 易于阅读和解析

## 启动方式

### 1. 开发环境（Makefile）
```bash
# 启动后端
make backend

# 同时启动前后端
make dev
```

### 2. Docker环境
```bash
# 构建镜像
docker build -t xiaoai-media .

# 运行容器
docker run -p 8000:8000 -e LOG_LEVEL=DEBUG xiaoai-media
```

### 3. 直接使用Python
```bash
cd backend
PYTHONPATH=src LOG_LEVEL=DEBUG python run.py
```

### 4. 直接使用uvicorn（使用静态配置）
```bash
cd backend
PYTHONPATH=src uvicorn xiaoai_media.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-config log_config.json
```

## 配置方式

### 环境变量
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `LOG_COLORS`: 是否启用彩色日志（true/false，默认：true）
- `HOST`: 监听地址（默认：0.0.0.0）
- `PORT`: 监听端口（默认：8000）
- `RELOAD`: 是否启用热重载（true/false，默认：false）

### 示例
```bash
# 启用DEBUG级别和彩色日志
export LOG_LEVEL=DEBUG
export LOG_COLORS=true
python backend/run.py

# 禁用彩色日志（适合日志文件或CI环境）
export LOG_COLORS=false
python backend/run.py
```

## 技术细节

### 彩色日志
日志格式化器会自动检测终端环境，在TTY终端中启用彩色输出：

**日志级别颜色：**
- `DEBUG`: 灰色
- `INFO`: 蓝色
- `WARNING`: 黄色
- `ERROR`: 红色
- `CRITICAL`: 粗体红色

**访问日志颜色：**
- 客户端地址: 灰色
- HTTP方法和路径: 青色
- 状态码:
  - 2xx (成功): 绿色
  - 3xx (重定向): 青色
  - 4xx (客户端错误): 黄色
  - 5xx (服务器错误): 红色

**模块名**: 青色

**禁用颜色：**
- 设置环境变量 `LOG_COLORS=false`
- 非TTY环境（如重定向到文件）会自动禁用颜色
- Docker日志收集时建议禁用颜色

### 时间戳格式
- 使用`%Y-%m-%d %H:%M:%S`格式
- 秒级精度（不包含毫秒）
- 与大多数日志系统兼容
- 易于人类阅读

### 日志级别宽度
使用8个字符的固定宽度来显示日志级别：
- `INFO    ` (4个字符 + 4个空格)
- `WARNING ` (7个字符 + 1个空格)
- `ERROR   ` (5个字符 + 3个空格)
- `DEBUG   ` (5个字符 + 3个空格)
- `CRITICAL` (8个字符 + 0个空格)

使用`%(levelname)-8s`可以确保所有日志级别都对齐。

### 分隔符
统一使用` - `（空格-空格）作为模块名和消息之间的分隔符。

### 特殊日志处理

**watchfiles日志：**
- watchfiles是uvicorn热重载功能使用的文件监控库
- 默认设置为WARNING级别，隐藏文件变化通知（如"2 changes detected"）
- 如果需要查看文件变化日志，可以设置`LOG_LEVEL=DEBUG`

**miservice日志：**
- miservice会记录每个HTTP请求，默认设置为WARNING级别以减少噪音
- 配置位置：`backend/src/xiaoai_media/api/main.py`

## 日志示例

### 应用启动
```
2026-03-26 14:22:29 INFO     xiaoai_media.client - MiService: using password auth for user 29105000782
2026-03-26 14:22:29 INFO     xiaoai_media.client - MiService: testing authentication...
2026-03-26 14:22:29 INFO     xiaoai_media.client - MiService: MiNA authentication successful
2026-03-26 14:22:29 INFO     xiaoai_media.client - MiService: MiIO authentication successful
2026-03-26 14:22:29 INFO     xiaoai_media.api.main - XiaoAiClient 已初始化
2026-03-26 14:22:29 INFO     xiaoai_media.api.main - 对话监听已禁用
2026-03-26 14:22:29 INFO     xiaoai_media.api.main - 播放监控已启用，检查是否需要恢复监听...
2026-03-26 14:22:29 INFO     xiaoai_media.api.main - 应用启动完成
2026-03-26 14:22:29 INFO     uvicorn - Application startup complete.
```

### API请求
```
2026-03-26 14:22:32 INFO     xiaoai_media.client - MiService: fetching device list (MiNA + MiIO)
2026-03-26 14:22:32 INFO     xiaoai_media.client - MiService: cached 1 merged device(s)
2026-03-26 14:22:32 INFO     uvicorn.access - 127.0.0.1:62331 - "GET /api/devices?refresh=true HTTP/1.1" 200 OK
2026-03-26 14:22:32 INFO     uvicorn.access - 127.0.0.1:62332 - "GET /api/playlists HTTP/1.1" 200 OK
```

### 错误日志
```
2026-03-26 14:07:10 ERROR    xiaoai_media.client - Failed to connect to device: Connection timeout
2026-03-26 14:07:10 WARNING  xiaoai_media.services.playlist_service - Skipped 3 files due to invalid format
```

## 文件结构

```
backend/
├── src/
│   └── xiaoai_media/
│       ├── api/
│       │   └── main.py          # 应用日志配置
│       └── log_config.py        # Uvicorn日志配置生成器
├── run.py                       # 启动脚本（推荐）
└── log_config.json              # 静态日志配置（备用）
```

## 向后兼容性
- 不影响日志内容，只改变格式
- 所有现有的日志记录调用无需修改
- 日志级别配置保持不变
- 仍然支持直接使用uvicorn命令启动

## 未来改进建议
1. 考虑使用结构化日志（JSON格式）
2. 添加请求ID追踪
3. 集成日志聚合服务（如ELK、Loki）
4. 添加日志轮转配置
5. 支持彩色日志输出（开发环境）
6. 添加日志过滤器（按模块、级别）
