# 配置管理 API

## 概述

配置管理 API 允许通过管理后台动态修改 `user_config.py` 中的配置项，无需重启服务即可生效。

## API 端点

### 获取当前配置

```http
GET /api/config
```

**响应示例：**
```json
{
  "MI_USER": "your_account",
  "MI_PASS": "***",
  "MI_PASS_TOKEN": "***",
  "MI_DID": "device_id",
  "MI_REGION": "cn",
  "MUSIC_API_BASE_URL": "http://10.184.62.160:5050",
  "MUSIC_DEFAULT_PLATFORM": "tx",
  "SERVER_BASE_URL": "http://10.184.62.160:8000",
  "ENABLE_CONVERSATION_POLLING": false,
  "CONVERSATION_POLL_INTERVAL": 2,
  "ENABLE_WAKE_WORD_FILTER": true,
  "LOG_LEVEL": "INFO",
  "VERBOSE_PLAYBACK_LOG": false,
  "PLAYLIST_STORAGE_DIR": "~/.xiaoai-media"
}
```

**说明：**
- 敏感字段（`MI_PASS`、`MI_PASS_TOKEN`）会被掩码为 `"***"`
- 空值显示为空字符串 `""`

### 更新配置

```http
PUT /api/config
Content-Type: application/json
```

**请求体：**
```json
{
  "MUSIC_API_BASE_URL": "http://192.168.1.100:5050",
  "SERVER_BASE_URL": "http://192.168.1.100:8000",
  "ENABLE_CONVERSATION_POLLING": true,
  "LOG_LEVEL": "DEBUG"
}
```

**响应：**
```json
{
  "message": "Configuration updated successfully"
}
```

## 支持的配置项

### 必填配置

| 配置项 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `MI_USER` | string | 小米账号 | `"your_account"` |
| `MI_PASS` | string | 小米密码 | `"password"` |
| `MI_PASS_TOKEN` | string | 小米密码令牌 | `"V1:..."` |

### 服务配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `MUSIC_API_BASE_URL` | string | 音乐搜索服务地址 | `"http://localhost:5050"` |
| `MUSIC_DEFAULT_PLATFORM` | string | 默认音乐平台 (tx/wy/kg/kw/mg) | `"tx"` |
| `SERVER_BASE_URL` | string | 本服务地址（用于代理） | `"http://localhost:8000"` |

### 设备配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `MI_DID` | string | 设备 ID | `""` |
| `MI_REGION` | string | 区域 (cn/de/i2/ru/sg/us) | `"cn"` |

### 功能配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `ENABLE_CONVERSATION_POLLING` | boolean | 启用对话监听 | `true` |
| `CONVERSATION_POLL_INTERVAL` | number | 对话轮询间隔（秒） | `2.0` |
| `ENABLE_WAKE_WORD_FILTER` | boolean | 启用唤醒词过滤 | `true` |

### 日志配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `LOG_LEVEL` | string | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) | `"INFO"` |
| `VERBOSE_PLAYBACK_LOG` | boolean | 显示详细播放日志 | `false` |

### 存储配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `PLAYLIST_STORAGE_DIR` | string | 播单数据存储目录 | `"~/.xiaoai-media"` |

## 配置更新流程

1. **验证配置项**：检查是否为允许的配置项
2. **过滤敏感字段**：值为 `"***"` 的敏感字段会被忽略（不更改）
3. **写入文件**：更新 `user_config.py` 文件
4. **重新加载**：重新加载配置模块，立即生效

## 注意事项

### 敏感字段处理

- `MI_PASS` 和 `MI_PASS_TOKEN` 在 GET 响应中会被掩码
- 更新时，如果值为 `"***"`，则不会修改该字段
- 如果要清空密码，传递空字符串 `""`

### 网络配置重要提示

⚠️ **`MUSIC_API_BASE_URL` 和 `SERVER_BASE_URL` 必须使用局域网 IP，不能使用 `localhost`**

错误示例：
```json
{
  "MUSIC_API_BASE_URL": "http://localhost:5050",
  "SERVER_BASE_URL": "http://localhost:8000"
}
```

正确示例：
```json
{
  "MUSIC_API_BASE_URL": "http://192.168.1.100:5050",
  "SERVER_BASE_URL": "http://192.168.1.100:8000"
}
```

### 配置文件格式

配置 API 会智能识别并更新 `user_config.py` 中的简单变量赋值：
- 字符串：`VAR_NAME = "value"`
- 数字：`VAR_NAME = 123` 或 `VAR_NAME = 1.5`
- 布尔：`VAR_NAME = True` 或 `VAR_NAME = False`

复杂类型（列表、字典、函数）不支持通过 API 修改，需要手动编辑 `user_config.py`。

## 前端集成

参考 `frontend/src/views/Settings.vue` 实现：

```typescript
import { ref } from 'vue'
import api from '@/api'

const config = ref({})

// 加载配置
async function loadConfig() {
  const data = await api.get('/config')
  config.value = data
}

// 保存配置
async function saveConfig() {
  await api.put('/config', config.value)
  ElMessage.success('配置已保存')
}
```

## 相关文档

- [配置快速指南](QUICK_CONFIG.md)
- [用户配置指南](USER_CONFIG_GUIDE.md)
- [配置常见问题](CONFIG_FAQ.md)
