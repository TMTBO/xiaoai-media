# MiIO 认证问题修复说明

## 问题描述

在之前的版本中，MiNA 服务可以正常认证，但 MiIO 服务会报错：

```
KeyError: 'passToken'
Exception on login 2910500078: 'passToken'
MiService: MiIOService device_list failed: Error https://api.io.mi.com/app/home/device_list: Login failed
```

## 根本原因

### 小米服务的认证机制

小米账号系统使用 **sid（服务标识符）** 来区分不同的服务：

- **MiNAService** 使用 `sid = "micoapi"`（小爱音箱服务）
- **MiIOService** 使用 `sid = "xiaomiio"`（米家智能家居服务）

每个 sid 需要独立的 `serviceToken`，token 结构如下：

```python
{
    "deviceId": "...",
    "userId": "...",
    "passToken": "...",           # 通用 token
    "micoapi": (ssecurity, serviceToken),    # MiNA 服务的 token
    "xiaomiio": (ssecurity, serviceToken)    # MiIO 服务的 token
}
```

### 之前的错误实现

之前的代码尝试预注入 `passToken` 来避免触发验证码：

```python
self._account.token = {
    "deviceId": "",
    "userId": config.MI_USER,
    "passToken": config.MI_PASS_TOKEN,
}
```

**问题**：
1. 只设置了基础字段，缺少 `micoapi` 和 `xiaomiio` 的 serviceToken
2. 当 MiNA 服务调用 `login("micoapi")` 时，成功获取 token
3. 当 MiIO 服务调用 `login("xiaomiio")` 时：
   - 使用已有的 `passToken` 重新登录
   - 小米服务器返回的响应中没有 `passToken` 字段（因为已经登录过了）
   - 导致 `KeyError: 'passToken'`

### 为什么会这样？

小米的登录逻辑：
- **首次登录**：返回完整的响应，包括 `passToken`、`userId`、`serviceToken` 等
- **使用 passToken 再次登录**：只返回新的 `serviceToken`，不再返回 `passToken`

`miservice` 库的代码（`miaccount.py:75`）：
```python
self.token["userId"] = resp["userId"]
self.token["passToken"] = resp["passToken"]  # 这里会报 KeyError
```

## 解决方案

### 修复方法

不再手动预注入 token，而是让 `miservice` 库自动处理认证：

```python
# 使用 token_store 自动保存/加载 token
self._account = MiAccount(
    self._session,
    config.MI_USER,
    config.MI_PASS,
    token_store=".mi.token",  # 自动持久化 token
)
```

### 工作流程

1. **首次启动**：
   - 使用密码登录
   - 自动获取 `micoapi` 和 `xiaomiio` 的 serviceToken
   - 保存完整的 token 到 `.mi.token` 文件

2. **后续启动**：
   - 从 `.mi.token` 加载已保存的 token
   - 如果 token 有效，直接使用
   - 如果 token 过期，自动使用密码重新登录

3. **Token 刷新**：
   - `miservice` 库会自动检测 401 错误
   - 自动使用密码重新登录
   - 更新 `.mi.token` 文件

### 优点

1. **自动化**：无需手动管理 token
2. **可靠性**：避免了 sid 冲突问题
3. **持久化**：token 自动保存，重启后无需重新登录
4. **容错性**：token 过期自动刷新

## 配置变更

### 之前的配置

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MI_PASS_TOKEN = "V1:xxxxxxxx..."  # 需要手动获取
```

### 现在的配置

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"  # 只需要密码
# MI_PASS_TOKEN 不再需要
```

### 迁移步骤

1. **删除 MI_PASS_TOKEN 配置**（可选，保留也不影响）
2. **确保配置了 MI_PASS**
3. **删除旧的 token 文件**（如果存在）：
   ```bash
   rm .mi.token
   ```
4. **重启服务**

## 首次登录验证码问题

### 问题

首次使用密码登录时，可能会触发小米的安全验证（验证码）。

### 解决方法

**方法 1：在小米官网或 App 中登录一次**

1. 访问 [https://account.xiaomi.com/](https://account.xiaomi.com/)
2. 使用你的账号密码登录
3. 完成验证码验证
4. 登录成功后，再启动本服务

这样可以解除账号的安全限制，后续使用密码登录时不会再触发验证码。

**方法 2：使用已登录的设备**

如果你已经在其他设备（如手机 App）上登录了小米账号，通常不会触发验证码。

**方法 3：等待一段时间**

如果频繁尝试登录导致触发验证码，等待几小时后再试。

### 为什么不再支持手动配置 passToken？

虽然手动配置 passToken 可以避免验证码，但会导致：
1. MiIO 服务认证失败（本次修复的问题）
2. 需要用户手动从浏览器提取 token（复杂）
3. Token 过期后需要重新提取（维护成本高）

使用密码登录虽然首次可能需要验证码，但：
1. 只需要验证一次
2. 后续自动刷新，无需人工干预
3. 更可靠，不会出现 sid 冲突

## 验证修复

启动服务后，查看日志：

### 成功的日志

```
INFO xiaoai_media.client — MiService: using password auth for user xxx
INFO xiaoai_media.client — MiService: testing authentication...
INFO xiaoai_media.client — MiService: MiNA authentication successful
INFO xiaoai_media.client — MiService: MiIO authentication successful
INFO xiaoai_media.client — MiService: cached X merged device(s)
```

### 如果 MiIO 失败（不影响核心功能）

```
INFO xiaoai_media.client — MiService: MiNA authentication successful
WARNING xiaoai_media.client — MiService: MiIO authentication failed: ...
WARNING xiaoai_media.client — MiService: MiIO features will be unavailable, but MiNA features will work
```

这种情况下：
- 基本功能（TTS、播放、控制）仍然可用（通过 MiNA）
- 高级功能（某些设备的特殊命令）可能不可用（需要 MiIO）

## 技术细节

### MiAccount.login() 流程

```python
async def login(self, sid):
    # 1. 调用 serviceLogin 获取登录参数
    resp = await self._serviceLogin(f"serviceLogin?sid={sid}&_json=true")
    
    # 2. 如果需要认证，使用密码登录
    if resp["code"] != 0:
        data = {
            "user": self.username,
            "hash": hashlib.md5(self.password.encode()).hexdigest().upper(),
            # ...
        }
        resp = await self._serviceLogin("serviceLoginAuth2", data)
    
    # 3. 保存通用 token
    self.token["userId"] = resp["userId"]
    self.token["passToken"] = resp["passToken"]  # 首次登录才有
    
    # 4. 获取并保存 sid 专用的 serviceToken
    serviceToken = await self._securityTokenService(...)
    self.token[sid] = (resp["ssecurity"], serviceToken)
    
    # 5. 持久化到文件
    if self.token_store:
        self.token_store.save_token(self.token)
```

### MiAccount.mi_request() 流程

```python
async def mi_request(self, sid, url, data, headers, relogin=True):
    # 1. 检查是否已登录该 sid
    if (self.token and sid in self.token) or await self.login(sid):
        # 2. 使用 sid 对应的 serviceToken 发送请求
        cookies = {
            "userId": self.token["userId"],
            "serviceToken": self.token[sid][1],  # 使用 sid 专用的 token
        }
        # 3. 发送请求...
        
        # 4. 如果返回 401，自动重新登录
        if status == 401 and relogin:
            self.token = None
            return await self.mi_request(sid, url, data, headers, False)
```

## 相关文件

- `backend/src/xiaoai_media/client.py` - 主要修改
- `docs/config/USER_CONFIG_GUIDE.md` - 配置文档更新
- `docs/config/GET_PASSTOKEN_GUIDE.md` - 已过时，仅供参考

## 参考资源

- [miservice 库源码](https://github.com/Yonsm/MiService)
- [小米账号开发文档](https://dev.mi.com/docs/passport/)
