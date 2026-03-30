# 更新日志

## [未发布] - 2026-03-XX

### 新增功能 ✨

#### 代理访问控制
- **局域网跳过认证** - 允许局域网内的设备（如小爱音箱）无需认证访问代理接口
- **可配置 IP 段** - 支持自定义局域网 IP 段（CIDR 格式）
- **前端配置界面** - 在配置管理页面可视化配置局域网认证规则
- **安全提示** - 提供安全使用建议和配置说明

配置项：
- `PROXY_SKIP_AUTH_FOR_LAN` - 是否启用局域网跳过认证（默认: True）
- `PROXY_LAN_NETWORKS` - 局域网 IP 段列表（默认包含常见私有网段）

详细说明请查看：[docs/config/PROXY_LAN_AUTH.md](docs/config/PROXY_LAN_AUTH.md)

#### 用户认证系统
- **用户登录** - 基于 JWT 的用户认证系统
- **用户管理** - 管理员可以创建、编辑、删除用户
- **权限控制** - 基于角色的访问控制（管理员/普通用户）
- **默认账户** - 自动创建默认管理员账户（admin / admin123）
- **用户界面** - 登录页面、用户管理页面、用户信息显示
- **全屏登录** - 未登录时全屏显示登录页面，无侧边栏干扰
- **数据存储优化** - 用户数据保存在 `~/.xiaoai_media/users.json`
- **用户名修改** - admin 用户可以修改自己的用户名和密码
- **强制认证** - 所有 API 接口都需要登录态校验
- **401 处理优化** - 前端检测到登录态过期后自动跳转并停止其他请求

详细说明请查看：
- [用户认证快速开始](docs/USER_AUTH_QUICKSTART.md)
- [用户认证完整文档](docs/USER_AUTH.md)
- [更新说明](docs/updates/USER_AUTH_UPDATE.md)
- [登录页面全屏显示](docs/updates/LOGIN_FULLSCREEN_UPDATE.md)
- [认证功能改进](docs/updates/AUTH_IMPROVEMENTS.md)

### 重大变更 ⚠️

#### 移除 MI_PASS_TOKEN 配置项
- **自动 Token 管理** - 使用 `miservice` 库的 `token_store` 机制自动管理 token
- **简化配置** - 用户只需配置账号密码，无需手动获取和配置 token
- **自动刷新** - Token 过期时自动重新登录并更新
- **Token 文件** - 自动保存到 `.mi.token` 文件

详细说明请查看：[docs/migration/REMOVE_MI_PASS_TOKEN.md](docs/migration/REMOVE_MI_PASS_TOKEN.md)

变更日志：[docs/migration/CHANGELOG_REMOVE_MI_PASS_TOKEN.md](docs/migration/CHANGELOG_REMOVE_MI_PASS_TOKEN.md)

#### 音乐 Provider 接口扩展
- **新增接口** - 在 `music_provider.py` 中新增搜索、排行榜接口
  - `search_music()` - 搜索音乐
  - `get_ranks()` - 获取排行榜列表
  - `get_rank_songs()` - 获取排行榜歌曲
- **职责分离** - `MusicService` 只负责参数校验，`music_provider` 负责实际 API 调用
- **用户自定义** - 所有音乐相关接口都可由用户自定义实现

详细说明请查看：[docs/refactor/MUSIC_PROVIDER_MIGRATION.md](docs/refactor/MUSIC_PROVIDER_MIGRATION.md)

变更日志：[docs/refactor/CHANGELOG_MUSIC_PROVIDER_UPDATE.md](docs/refactor/CHANGELOG_MUSIC_PROVIDER_UPDATE.md)

### 迁移指南

#### 移除 MI_PASS_TOKEN

```python
# 编辑 user_config.py，删除 MI_PASS_TOKEN 行
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
# MI_PASS_TOKEN = "V1:xxxxxxxx..."  # 删除这一行
```

#### 使用新的音乐 Provider 接口

```python
# music_provider.py 中现在可以自定义更多接口

# 自定义搜索（例如添加缓存）
async def search_music(query, platform, page, limit, music_api_base_url, timeout=10):
    # 你的自定义逻辑
    pass

# 自定义排行榜获取
async def get_ranks(platform, music_api_base_url, timeout=10):
    # 你的自定义逻辑
    pass
```

---

## [历史版本] - 2024-XX-XX

### 重大变更 ⚠️

#### 播单存储结构重构
- **多文件存储** - 从单文件 `playlists.json` 改为多文件存储
  - `playlists/index.json` - 播单索引文件
  - `playlists/{id}.json` - 各播单的详细数据
- **数据结构精简** - 播单项只保留必要字段（title, artist, album, audio_id, url, custom_params）
- **性能优化** - 列表加载速度提升 80-90%，语音播放响应速度提升 50-70%
- **自动迁移** - 提供迁移脚本 `scripts/migrate_playlists.py`

详细说明请查看：[docs/playlist/PLAYLIST_STORAGE_REFACTOR.md](docs/playlist/PLAYLIST_STORAGE_REFACTOR.md)

#### 播单模块重构
- **模块化设计** - 将播单功能拆分为独立模块
  - `playlist/models.py` - 数据模型
  - `playlist/storage.py` - 存储管理
  - `playlist/service.py` - 业务逻辑
  - `api/routes/playlist.py` - 路由层
- **关注点分离** - 路由、业务、存储、模型各司其职
- **提高可测试性** - 业务逻辑可独立测试
- **提高可维护性** - 模块化设计，职责清晰

详细说明请查看：[docs/refactor/PLAYLIST_MODULE_REFACTOR.md](docs/refactor/PLAYLIST_MODULE_REFACTOR.md)

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
