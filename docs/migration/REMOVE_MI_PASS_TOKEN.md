# 移除 MI_PASS_TOKEN 配置项

## 变更说明

从 v1.0.0 开始，系统使用 `miservice` 库的 `token_store` 机制自动管理 token，不再需要手动配置 `MI_PASS_TOKEN`。

## 变更原因

1. **自动化管理**：token 由 miservice 自动保存和加载，无需手动配置
2. **简化配置**：用户只需配置账号和密码，降低使用门槛
3. **避免冲突**：解决了 MiNA 和 MiIO 服务的 sid 冲突问题
4. **自动刷新**：token 过期时自动使用密码重新登录

## 迁移步骤

### 1. 更新配置文件

**之前的配置**：
```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MI_PASS_TOKEN = "V1:xxxxxxxx..."  # 需要手动获取和配置
```

**现在的配置**：
```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"  # 只需要密码
# MI_PASS_TOKEN 已移除，token 自动管理
```

### 2. 删除旧的 token 配置

编辑 `user_config.py`，删除或注释掉 `MI_PASS_TOKEN` 行：

```python
# MI_PASS_TOKEN = "..."  # 不再需要
```

### 3. 清理旧的 token 文件（可选）

如果之前手动创建过 token 文件，可以删除它让系统重新生成：

```bash
rm .mi.token
```

### 4. 重启服务

```bash
# Docker 方式
docker-compose restart

# 或直接运行
make run
```

## Token 存储位置

Token 现在自动保存在项目根目录的 `.mi.token` 文件中：

```json
{
  "deviceId": "...",
  "userId": "...",
  "passToken": "...",
  "micoapi": ["ssecurity", "serviceToken"],
  "xiaomiio": ["ssecurity", "serviceToken"]
}
```

**注意**：
- 这个文件由 miservice 自动管理，不要手动编辑
- 文件包含敏感信息，已添加到 `.gitignore`
- 如果认证失败，可以删除此文件让系统重新登录

## 工作原理

### 启动时

1. 系统创建 `MiAccount` 实例，指定 `token_store=".mi.token"`
2. miservice 自动从文件加载已保存的 token
3. 如果文件不存在或 token 无效，使用密码登录
4. 登录成功后，自动保存 token 到文件

### 运行时

1. 每次 API 请求使用对应 sid 的 serviceToken
2. 如果返回 401 错误，miservice 自动重新登录
3. 新的 token 自动保存到文件

### Token 刷新

- Token 过期时，miservice 自动使用密码重新登录
- 无需人工干预
- 新 token 自动保存

## 优点

1. **简化配置**：用户只需配置账号密码
2. **自动管理**：token 自动保存、加载、刷新
3. **避免冲突**：正确处理 MiNA 和 MiIO 的不同 sid
4. **更可靠**：使用 miservice 的标准机制，而不是自定义逻辑

## 常见问题

### Q: 我的旧 token 还能用吗？

A: 可以。如果 `.mi.token` 文件中有有效的 token，系统会继续使用。但建议删除旧文件，让系统重新生成标准格式的 token。

### Q: 如何查看当前的 token？

A: 查看 `.mi.token` 文件：

```bash
cat .mi.token | python3 -m json.tool
```

### Q: Token 多久过期？

A: 通常几周到几个月。过期后系统会自动使用密码重新登录。

### Q: 如果忘记密码怎么办？

A: 
1. 如果 `.mi.token` 文件中的 token 仍然有效，可以继续使用
2. 如果 token 也过期了，需要重置小米账号密码

### Q: 可以不配置密码吗？

A: 不建议。虽然有 token 时可以暂时不配置密码，但 token 过期后将无法自动刷新，需要手动重新登录。

### Q: 首次登录触发验证码怎么办？

A: 参考 [MIIO_AUTH_FIX.md](./MIIO_AUTH_FIX.md) 中的说明：
1. 在小米官网或 App 中登录一次
2. 完成验证码验证
3. 再启动本服务

## 相关文档

- [MIIO_AUTH_FIX.md](./MIIO_AUTH_FIX.md) - MiIO 认证问题修复
- [GLOBAL_CLIENT_SINGLETON.md](../refactor/GLOBAL_CLIENT_SINGLETON.md) - 全局客户端单例
- [USER_CONFIG_GUIDE.md](../config/USER_CONFIG_GUIDE.md) - 用户配置指南

## 技术细节

### 代码变更

1. **config.py**：移除 `MI_PASS_TOKEN` 配置项
2. **client.py**：使用 `token_store` 参数初始化 MiAccount
3. **config_service.py**：移除 token 相关的 API 字段
4. **user_config_template.py**：更新配置模板

### Token Store 机制

miservice 的 `MiTokenStore` 类负责：
- 从文件加载 token
- 保存 token 到文件
- 自动处理文件不存在的情况

```python
# miservice 内部实现
class MiTokenStore:
    def load_token(self):
        if os.path.isfile(self.token_path):
            with open(self.token_path) as f:
                return json.load(f)
        return None
    
    def save_token(self, token=None):
        if token:
            with open(self.token_path, "w") as f:
                json.dump(token, f, indent=2)
```

### 自动登录流程

```python
# 初始化时指定 token_store
account = MiAccount(session, user, password, token_store=".mi.token")

# miservice 自动处理
# 1. 尝试从文件加载 token
# 2. 如果文件不存在或 token 无效，使用密码登录
# 3. 登录成功后保存 token 到文件
# 4. 后续请求使用已保存的 token
# 5. 如果返回 401，自动重新登录并更新文件
```

## 总结

移除 `MI_PASS_TOKEN` 配置项简化了用户配置，同时提高了系统的可靠性和可维护性。用户只需配置账号和密码，系统会自动处理 token 的管理。
