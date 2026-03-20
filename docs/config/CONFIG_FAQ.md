# 配置系统常见问题

## Q1: 使用 user_config.py 后，还需要 .env 文件吗？

### 简短回答
**不需要**。使用 `user_config.py` 后，`.env` 文件不再必需。

### 详细说明

配置优先级：
```
user_config.py > .env > 默认值
```

#### 场景 1: 只使用 user_config.py（推荐）

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
WAKE_WORDS = ["小爱同学", "小爱"]
```

此时不需要 `.env` 文件，所有配置都在 `user_config.py` 中。

#### 场景 2: 混合使用（灵活）

```python
# user_config.py
# 只配置唤醒词等新功能
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True

# 其他配置从 .env 读取
```

```env
# .env
MI_USER=your_account@example.com
MI_PASS=your_password
MUSIC_API_BASE_URL=http://192.168.1.100:5050
```

此时 `user_config.py` 中未设置的配置项会从 `.env` 读取。

#### 场景 3: 在 user_config.py 中读取 .env（兼容旧配置）

```python
# user_config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path, override=True)

# 从环境变量读取基础配置
MI_USER = os.getenv("MI_USER", "")
MI_PASS = os.getenv("MI_PASS", "")
MUSIC_API_BASE_URL = os.getenv("MUSIC_API_BASE_URL", "http://localhost:5050")

# 配置新功能
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

这样可以保留现有的 `.env` 文件，同时使用新功能。

### 推荐做法

1. **新用户**：直接使用 `user_config.py`，不需要 `.env`
2. **老用户**：可以保留 `.env`，在 `user_config.py` 中只配置新功能
3. **迁移用户**：逐步将配置从 `.env` 迁移到 `user_config.py`

---

## Q2: 使用 Makefile 启动时，配置如何加载？

### 简短回答
**自动加载**。使用 `make backend` 或 `make dev` 启动时，配置会自动加载。

### 详细说明

#### 启动流程

```bash
# 启动后端
make backend

# 或同时启动前后端
make dev
```

#### 配置加载顺序

1. **服务启动** → `uvicorn xiaoai_media.api.main:app`
2. **导入模块** → `from xiaoai_media import config`
3. **加载配置** → `config.py` 自动执行
4. **检查文件** → 查找项目根目录的 `user_config.py`
5. **加载配置**：
   - 如果存在 `user_config.py` → 加载该文件
   - 如果不存在 → 从 `.env` 加载
   - 如果都不存在 → 使用默认值

#### 启动日志

成功加载 `user_config.py` 时会看到：
```
INFO:xiaoai_media.config:成功加载用户配置文件: /path/to/user_config.py
```

未找到 `user_config.py` 时会看到：
```
INFO:xiaoai_media.config:未找到用户配置文件 user_config.py，使用默认配置
```

#### 验证配置

```bash
# 测试配置加载
make test-config

# 查看输出
============================================================
配置加载测试
============================================================

小米账号配置:
  MI_USER: your_account@example.com
  ...

唤醒词配置:
  WAKE_WORDS: ['小爱同学', '小爱']
  ENABLE_WAKE_WORD_FILTER: True
```

### 无需额外配置

- ✅ 不需要修改 Makefile
- ✅ 不需要设置环境变量
- ✅ 不需要指定配置文件路径
- ✅ 配置文件放在项目根目录即可

---

## Q3: 如何验证配置是否生效？

### 方法 1: 使用测试命令

```bash
make test-config
```

### 方法 2: 查看启动日志

```bash
make backend
```

查看日志中的配置加载信息。

### 方法 3: 测试唤醒词

启动服务后，观察日志：

```
INFO:xiaoai_media.command_handler:收到设备 xxx 的指令: 小爱同学，播放周杰伦的晴天
DEBUG:xiaoai_media.command_handler:预处理后的指令: 播放周杰伦的晴天
INFO:xiaoai_media.command_handler:检测到播放指令: 播放周杰伦的晴天
```

如果没有唤醒词：
```
INFO:xiaoai_media.command_handler:收到设备 xxx 的指令: 播放周杰伦的晴天
DEBUG:xiaoai_media.command_handler:指令未包含唤醒词，忽略: 播放周杰伦的晴天
```

---

## Q4: 配置文件放在哪里？

### 文件位置

```
xiaoai-media/              # 项目根目录
├── user_config.py         # 用户配置（需创建）
├── user_config_template.py # 配置模板
├── user_config.example.py  # 配置示例
├── .env                   # 环境变量（可选）
├── backend/
├── frontend/
└── ...
```

### 重要提示

- ✅ `user_config.py` 必须放在**项目根目录**
- ✅ 与 `backend/`, `frontend/` 同级
- ✅ 不要放在 `backend/` 或其他子目录

---

## Q5: 如何从 .env 迁移到 user_config.py？

### 步骤 1: 复制模板

```bash
cp user_config_template.py user_config.py
```

### 步骤 2: 复制配置

将 `.env` 中的配置复制到 `user_config.py`：

```env
# .env (旧配置)
MI_USER=your_account@example.com
MI_PASS=your_password
MUSIC_API_BASE_URL=http://192.168.1.100:5050
```

↓ 迁移到 ↓

```python
# user_config.py (新配置)
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
```

### 步骤 3: 添加新功能

```python
# user_config.py
# ... 基础配置 ...

# 新增唤醒词配置
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True
```

### 步骤 4: 测试

```bash
make test-config
```

### 步骤 5: 启动服务

```bash
make dev
```

### 步骤 6: 删除 .env（可选）

确认一切正常后，可以删除 `.env` 文件：

```bash
# 备份
cp .env .env.backup

# 删除
rm .env
```

---

## Q6: Docker 部署时如何使用配置？

### 方法 1: 挂载 user_config.py

```bash
docker run -v $(pwd)/user_config.py:/app/user_config.py \
  -p 8000:8000 xiaoai-media:latest
```

### 方法 2: 构建时复制

```dockerfile
# Dockerfile
COPY user_config.py /app/user_config.py
```

### 方法 3: 继续使用 .env

```bash
docker run --env-file .env -p 8000:8000 xiaoai-media:latest
```

---

## Q7: 配置文件语法错误怎么办？

### 检查语法

```bash
# 检查 Python 语法
python3 -m py_compile user_config.py
```

### 常见错误

#### 错误 1: 缺少引号

```python
# ❌ 错误
MI_USER = your_account@example.com

# ✅ 正确
MI_USER = "your_account@example.com"
```

#### 错误 2: 缩进错误

```python
# ❌ 错误
def should_handle_command(query: str) -> bool:
return True  # 缺少缩进

# ✅ 正确
def should_handle_command(query: str) -> bool:
    return True
```

#### 错误 3: 列表语法错误

```python
# ❌ 错误
WAKE_WORDS = ["小爱同学" "小爱"]  # 缺少逗号

# ✅ 正确
WAKE_WORDS = ["小爱同学", "小爱"]
```

### 查看错误日志

```bash
make backend
# 查看启动日志中的错误信息
```

---

## Q8: 如何调试配置问题？

### 步骤 1: 测试配置加载

```bash
make test-config
```

### 步骤 2: 检查文件位置

```bash
ls -la user_config.py
# 确认文件在项目根目录
```

### 步骤 3: 检查语法

```bash
python3 -m py_compile user_config.py
```

### 步骤 4: 查看启动日志

```bash
make backend
# 观察配置加载日志
```

### 步骤 5: 使用 Python 直接测试

```bash
python3 -c "
import sys
sys.path.insert(0, 'backend/src')
from xiaoai_media import config
print('MI_USER:', config.MI_USER)
print('WAKE_WORDS:', config.WAKE_WORDS)
print('ENABLE_WAKE_WORD_FILTER:', config.ENABLE_WAKE_WORD_FILTER)
"
```

---

## Q9: 配置文件可以放在其他位置吗？

### 默认位置

配置文件必须放在**项目根目录**，文件名必须是 `user_config.py`。

### 自定义位置（高级）

如果需要自定义位置，可以修改 `backend/src/xiaoai_media/config.py`：

```python
# config.py
_user_config_path = Path("/path/to/your/config.py")  # 自定义路径
```

但**不推荐**这样做，因为会影响可移植性。

---

## Q10: 多环境配置怎么办？

### 方法 1: 使用不同的配置文件

```bash
# 开发环境
cp user_config.dev.py user_config.py
make dev

# 生产环境
cp user_config.prod.py user_config.py
make backend
```

### 方法 2: 在配置文件中判断环境

```python
# user_config.py
import os

ENV = os.getenv("ENV", "dev")

if ENV == "prod":
    MI_USER = "prod_account@example.com"
    MUSIC_API_BASE_URL = "http://prod-server:5050"
else:
    MI_USER = "dev_account@example.com"
    MUSIC_API_BASE_URL = "http://localhost:5050"

# 共同配置
WAKE_WORDS = ["小爱同学", "小爱"]
```

启动时指定环境：
```bash
ENV=prod make backend
```

---

## 快速参考

### 配置文件位置
```
项目根目录/user_config.py
```

### 启动命令
```bash
make dev          # 启动前后端
make backend      # 只启动后端
make test-config  # 测试配置
```

### 配置优先级
```
user_config.py > .env > 默认值
```

### 完整文档
- [快速配置指南](QUICK_CONFIG.md)
- [完整配置指南](USER_CONFIG_GUIDE.md)
- [配置速查表](CONFIG_CHEATSHEET.md)
