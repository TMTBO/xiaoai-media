# 更新日志

## [未发布] - 2024-XX-XX

### 重大变更 ⚠️

#### 配置系统重构
- **移除 .env 文件支持** - 不再支持通过 `.env` 文件配置
- **强制使用 user_config.py** - 所有配置必须在 `user_config.py` 中设置
- **简化配置加载逻辑** - 移除了 dotenv 依赖和环境变量读取
- 如果未找到 `user_config.py`，系统将抛出错误并提示创建

### 迁移指南

如果你之前使用 `.env` 文件，请按以下步骤迁移：

```bash
# 1. 复制配置模板
cp user_config_template.py user_config.py

# 2. 将 .env 中的配置复制到 user_config.py
# 3. 验证配置
make verify-config

# 4. 启动服务
make dev
```

详细迁移说明请查看：[docs/migration/MIGRATION_TO_USER_CONFIG.md](docs/migration/MIGRATION_TO_USER_CONFIG.md)

### 新增功能

#### 用户配置系统
- 支持通过 Python 配置文件 (`user_config.py`) 进行配置，参考 xiaomusic 设计
- 所有配置项可从 `.env` 迁移到 `user_config.py`
- 新增唤醒词过滤功能，只处理包含指定唤醒词的指令
- 支持自定义指令处理函数：
  - `should_handle_command()` - 自定义指令过滤逻辑
  - `preprocess_command()` - 自定义指令预处理逻辑
- 配置优先级：`user_config.py` > `.env` > 默认值
- 向后兼容：不创建 `user_config.py` 时继续使用 `.env`

### 配置项

新增配置项：
- `WAKE_WORDS` - 唤醒词列表
- `ENABLE_WAKE_WORD_FILTER` - 是否启用唤醒词过滤
- `LOG_LEVEL` - 日志级别
- `VERBOSE_PLAYBACK_LOG` - 是否显示详细播放日志

### 文档

- 新增 `user_config_template.py` - 用户配置模板文件
- 新增 `docs/USER_CONFIG_GUIDE.md` - 用户配置完整指南
- 更新 `README.md` - 添加配置系统说明
- 新增 `test/test_user_config.py` - 配置系统测试脚本

### 技术改进

- 重构 `backend/src/xiaoai_media/config.py`：
  - 支持动态加载 Python 配置文件
  - 统一配置读取接口
  - 支持自定义处理函数
- 更新 `backend/src/xiaoai_media/command_handler.py`：
  - 集成唤醒词过滤
  - 集成指令预处理
  - 改进日志输出

### 使用示例

```python
# user_config.py

# 基础配置
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"

# 唤醒词配置
WAKE_WORDS = ["小爱同学", "小爱"]
ENABLE_WAKE_WORD_FILTER = True

# 自定义处理函数
def should_handle_command(query: str) -> bool:
    """只处理音乐相关指令"""
    if not any(word in query for word in WAKE_WORDS):
        return False
    return "播放" in query or "音乐" in query

def preprocess_command(query: str) -> str:
    """标准化指令"""
    for wake_word in WAKE_WORDS:
        query = query.replace(wake_word, "")
    return query.strip()
```

### 迁移指南

从 `.env` 迁移到 `user_config.py`：

1. 复制模板：`cp user_config_template.py user_config.py`
2. 将 `.env` 中的配置复制到 `user_config.py`
3. 根据需要配置唤醒词和自定义函数
4. 启动服务，查看日志确认配置已加载

详细说明请查看：[docs/USER_CONFIG_GUIDE.md](docs/USER_CONFIG_GUIDE.md)

---

## 历史版本

（待补充）
