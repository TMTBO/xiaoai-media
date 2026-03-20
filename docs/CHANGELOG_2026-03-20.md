# 配置管理和文档整理更新 (2026-03-20)

## 更新概览

本次更新主要完成了两项重要工作：
1. **配置管理系统升级** - 支持所有配置项通过管理后台动态修改
2. **文档结构优化** - 按功能模块整理文档，提升可读性

---

## 1. 配置管理系统升级

### 新增配置项支持

配置管理 API 现在支持 `user_config.py` 中的所有配置变量：

#### 新增支持的配置项
- ✅ `SERVER_BASE_URL` - 本服务地址（用于生成代理链接）
- ✅ `ENABLE_CONVERSATION_POLLING` - 对话监听开关
- ✅ `CONVERSATION_POLL_INTERVAL` - 对话轮询间隔
- ✅ `ENABLE_WAKE_WORD_FILTER` - 唤醒词过滤开关
- ✅ `LOG_LEVEL` - 日志级别
- ✅ `VERBOSE_PLAYBACK_LOG` - 详细播放日志开关
- ✅ `PLAYLIST_STORAGE_DIR` - 播单存储目录

#### 原有支持的配置项
- `MI_USER`
- `MI_PASS`
- `MI_PASS_TOKEN`
- `MI_DID`
- `MI_REGION`
- `MUSIC_API_BASE_URL`
- `MUSIC_DEFAULT_PLATFORM`

### 技术改进

#### 从 .env 迁移到 user_config.py
- **之前**：配置 API 操作 `.env` 文件（不存在）
- **现在**：配置 API 直接操作 `user_config.py`
- **优势**：
  - 与项目配置系统统一
  - 支持更多数据类型（字符串、数字、布尔）
  - 保留注释和格式

#### 智能配置更新
```python
def _write_user_config(data: dict[str, str | bool | int | float]) -> None:
    """更新 user_config.py 中的配置变量"""
    # 使用正则表达式匹配并替换配置项
    # 保留原有的注释和代码格式
```

#### 类型验证
```python
class ConfigUpdate(BaseModel):
    CONVERSATION_POLL_INTERVAL: float | None = Field(None, ge=0.1, le=60)
    LOG_LEVEL: str | None = Field(None, pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
```

### 配置文件更新

#### backend/src/xiaoai_media/config.py
添加日志配置加载：
```python
# ============================================
# 日志配置
# ============================================

LOG_LEVEL: str = _get_config("LOG_LEVEL", "INFO")
VERBOSE_PLAYBACK_LOG: bool = _get_config("VERBOSE_PLAYBACK_LOG", False)
```

#### user_config.py 变量整理
所有变量定义已移到方法前面，结构清晰：
1. 小米账号配置
2. 音乐服务配置
3. 本服务配置
4. 对话监听配置
5. 唤醒词配置
6. 日志配置
7. 播单管理配置
8. 自定义处理函数

---

## 2. 文档结构优化

### 新建功能目录

```
docs/
├── api/           # API 文档
├── config/        # 配置文档
├── playlist/      # 播放列表文档
├── playback/      # 播放功能文档（已存在）
├── tts/           # TTS 文档（已存在）
├── conversation/  # 对话监听文档（已存在）
└── migration/     # 迁移文档（已存在）
```

### 文档迁移

#### 配置相关 → `docs/config/`
- CONFIG_ANSWERS.md
- CONFIG_CHEATSHEET.md
- CONFIG_FAQ.md
- QUICK_CONFIG.md
- USER_CONFIG_GUIDE.md
- USER_CONFIG_IMPLEMENTATION.md
- USER_CONFIG_SUMMARY.md
- **新增**: CONFIG_API.md

#### 播放列表 → `docs/playlist/`
- PLAYLIST_GUIDE.md
- PLAYLIST_FEATURE_UPDATE.md
- PLAYLIST_IMPROVEMENTS.md

#### API 文档 → `docs/api/`
- API_REFERENCE.md
- API实现说明.md

#### 迁移文档 → `docs/migration/`
- MISERVICE_MIGRATION.md（从根目录移入）

### 新增文档

#### 功能目录 README
- `docs/config/README.md` - 配置系统目录入口
- `docs/playlist/README.md` - 播放列表目录入口
- `docs/api/README.md` - API 文档目录入口

#### 配置管理 API 文档
- `docs/config/CONFIG_API.md` - 完整的配置管理 API 文档
  - API 端点说明
  - 所有配置项详解
  - 使用示例
  - 注意事项

#### 文档结构说明
- `docs/STRUCTURE.md` - 完整的文档组织结构说明
  - 目录树
  - 快速导航
  - 文档维护原则

#### 更新主文档
- `docs/README.md` - 重新组织文档入口
  - 按功能分类
  - 快速导航链接
  - 问题排查指引

---

## 3. 代理接口实现

### 新增代理路由

创建了项目内部的音频代理接口，替代外部 `/main/proxy`：

#### backend/src/xiaoai_media/api/routes/proxy.py
```python
@router.get("/stream")
async def proxy_audio_stream(url: str):
    """代理音频流，添加必要的请求头以绕过防盗链限制"""
    # 使用 httpx 请求原始 URL
    # 添加 User-Agent、Accept 等请求头
    # 以流式方式转发音频数据
```

### 配置更新

#### 新增 SERVER_BASE_URL
区分音乐搜索服务和本服务：
- `MUSIC_API_BASE_URL` - 音乐搜索服务地址（如 music_download）
- `SERVER_BASE_URL` - 本服务地址（用于生成代理链接）

#### 代理 URL 生成
```python
def _make_proxy_url(original_url: str) -> str:
    # 之前：使用 MUSIC_API_BASE_URL（错误）
    # 现在：使用 SERVER_BASE_URL（正确）
    return f"{config.SERVER_BASE_URL}/api/proxy/stream?url={quote(original_url)}"
```

---

## 4. 依赖更新

### 添加 httpx
```toml
dependencies = [
    "miservice_fork",
    "aiohttp",
    "aiofiles",
    "fastapi",
    "uvicorn[standard]",
    "httpx",  # 新增：用于代理音频流
]
```

---

## 使用指南

### 1. 配置管理

#### 通过管理后台
1. 访问 http://localhost:8000
2. 进入"设置"页面
3. 修改配置项
4. 点击"保存"，配置立即生效

#### 通过 API
```bash
# 获取当前配置
curl http://localhost:8000/api/config

# 更新配置
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "SERVER_BASE_URL": "http://192.168.1.100:8000",
    "LOG_LEVEL": "DEBUG",
    "ENABLE_CONVERSATION_POLLING": true
  }'
```

### 2. 查看文档

访问文档入口：
- [docs/README.md](docs/README.md) - 文档中心
- [docs/STRUCTURE.md](docs/STRUCTURE.md) - 文档结构
- [docs/config/CONFIG_API.md](docs/config/CONFIG_API.md) - 配置 API

---

## 注意事项

### ⚠️ 网络配置
`SERVER_BASE_URL` 和 `MUSIC_API_BASE_URL` 必须使用局域网 IP：
```python
# ❌ 错误
SERVER_BASE_URL = "http://localhost:8000"
MUSIC_API_BASE_URL = "http://localhost:5050"

# ✅ 正确
SERVER_BASE_URL = "http://192.168.1.100:8000"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
```

### 敏感信息保护
- 密码字段自动掩码为 `"***"`
- 更新时，值为 `"***"` 的字段会被忽略
- 支持使用 token 代替密码

---

## 技术架构

### 配置管理流程
```
用户配置 → user_config.py → config.py → 配置 API
    ↑                                        ↓
    └────────── 动态更新（importlib.reload）─┘
```

### 音频代理流程
```
音箱 → 本服务代理 (/api/proxy/stream) → 音乐平台
         ↑                                    ↓
         └──── 添加请求头，流式转发 ────────┘
```

---

## 相关文件

### 后端代码
- `backend/src/xiaoai_media/api/routes/config.py` - 配置 API
- `backend/src/xiaoai_media/api/routes/proxy.py` - 代理接口
- `backend/src/xiaoai_media/config.py` - 配置加载
- `user_config.py` - 用户配置文件

### 配置文件
- `backend/pyproject.toml` - 依赖管理
- `user_config_template.py` - 配置模板
- `user_config.example.py` - 配置示例

### 文档
- `docs/config/CONFIG_API.md` - 配置 API 文档
- `docs/STRUCTURE.md` - 文档结构
- `docs/README.md` - 文档入口

---

## 测试验证

所有更新已通过测试：
```bash
✓ 应用加载成功
✓ 配置 API 端点正常
✓ 代理模块导入正常
✓ httpx 依赖安装成功
```

---

## 下一步计划

1. **前端更新** - 在设置页面添加新配置项的 UI
2. **配置分组** - 在管理后台按功能分组显示配置
3. **配置验证** - 添加更严格的配置值验证
4. **配置备份** - 支持配置的导出和导入
