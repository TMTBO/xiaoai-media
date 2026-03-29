# 小米账号 passToken 获取指南

> **⚠️ 本文档已过时**
> 
> 从 v1.0.0 开始，系统使用 `miservice` 的 `token_store` 机制自动管理 token。
> 你只需要配置 `MI_USER` 和 `MI_PASS`，token 会自动保存到 `.mi.token` 文件。
> 
> 本文档仅供参考，了解 token 的工作原理。
> 
> **新的配置方式**：
> ```python
> MI_USER = "your_account@example.com"
> MI_PASS = "your_password"  # 只需要密码
> # Token 会自动保存到 .mi.token 文件
> ```

---

# 以下内容已过时，仅供参考

## 问题说明

当使用密码登录小米账号时，可能会触发安全验证（验证码），导致无法自动登录。使用 `passToken` 可以避免这个问题。

## 方法一：通过浏览器获取 passToken（推荐）

这是最简单、最可靠的方法，不需要安装额外工具。

### 步骤

1. **打开浏览器开发者工具**
   - Chrome/Edge: 按 `F12` 或 `Ctrl+Shift+I` (Mac: `Cmd+Option+I`)
   - 切换到 `Network`（网络）标签页
   - 勾选 `Preserve log`（保留日志）

2. **访问小米账号登录页面**
   ```
   https://account.xiaomi.com/
   ```

3. **登录你的小米账号**
   - 输入账号和密码
   - 完成验证码验证（如果需要）
   - 等待登录成功

4. **查找 passToken**
   
   在 Network 标签页中：
   - 在过滤框中输入 `serviceLogin`
   - 找到 `serviceLoginAuth2` 请求
   - 点击该请求，查看 `Response`（响应）标签
   - 在响应中找到 `passToken` 字段
   
   或者：
   - 在过滤框中输入 `device_list`
   - 找到任意小米服务的请求
   - 点击该请求，查看 `Cookies` 标签
   - 找到名为 `passToken` 的 Cookie

5. **复制 passToken**
   - passToken 通常是一个很长的字符串，格式类似：
     ```
     V1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```
   - 完整复制这个值（包括 `V1:` 前缀）

6. **配置到项目中**
   
   编辑 `user_config.py`：
   ```python
   MI_USER = "your_account@example.com"  # 你的小米账号
   MI_PASS = "your_password"              # 保留密码（用于 token 过期时自动刷新）
   MI_PASS_TOKEN = "V1:xxxxxxxx..."       # 粘贴刚才复制的 passToken
   ```

7. **重启服务**
   ```bash
   # 如果使用 Docker
   docker-compose restart
   
   # 如果直接运行
   # 停止当前服务，然后重新启动
   ```

## 方法二：使用 Python 脚本获取（需要手动处理验证码）

如果方法一不可行，可以尝试这个方法。

### 步骤

1. **创建获取脚本**
   
   创建文件 `get_token.py`：
   ```python
   #!/usr/bin/env python3
   import asyncio
   from aiohttp import ClientSession
   from miservice import MiAccount
   
   async def get_token():
       username = input("请输入小米账号: ")
       password = input("请输入密码: ")
       
       async with ClientSession() as session:
           account = MiAccount(session, username, password)
           
           # 尝试登录
           success = await account.login("micoapi")
           
           if success and account.token:
               print("\n✅ 登录成功！")
               print(f"\npassToken: {account.token.get('passToken', 'N/A')}")
               print(f"userId: {account.token.get('userId', 'N/A')}")
               print(f"\n请将 passToken 复制到 user_config.py 的 MI_PASS_TOKEN 配置中")
           else:
               print("\n❌ 登录失败")
               print("可能原因：")
               print("1. 账号或密码错误")
               print("2. 需要安全验证（请使用方法一通过浏览器获取）")
               print("3. 网络问题")
   
   if __name__ == "__main__":
       asyncio.run(get_token())
   ```

2. **运行脚本**
   ```bash
   cd backend
   source .venv/bin/activate  # 激活虚拟环境
   python3 get_token.py
   ```

3. **如果触发验证码**
   - 脚本会失败
   - 请改用方法一（浏览器方式）

## 方法三：从现有的小米 App 中提取（高级）

如果你已经在手机上登录了小米 App，可以尝试从 App 中提取 token。

### Android 设备（需要 Root）

1. 使用 ADB 连接手机
2. 查找小米 App 的数据目录
3. 提取 token 文件

这个方法比较复杂，不推荐普通用户使用。

## 常见问题

### Q: passToken 会过期吗？

A: 会的。passToken 通常有效期较长（几周到几个月），但最终会过期。

**解决方案**：
- 在 `user_config.py` 中同时配置 `MI_PASS` 和 `MI_PASS_TOKEN`
- 当 token 过期时，系统会自动使用密码重新登录并更新 token

### Q: 为什么使用密码登录会触发验证码？

A: 小米的安全机制会检测异常登录行为：
- 新设备登录
- 频繁登录
- 异常 IP 地址
- 使用自动化工具登录

使用 passToken 可以避免重复登录，减少触发验证码的概率。

### Q: 如何避免 token 频繁过期？

A: 
1. 配置密码，支持自动刷新
2. 不要频繁重启服务
3. 使用稳定的网络环境
4. 不要在多个地方同时使用同一账号

### Q: 获取 passToken 时仍然需要验证码怎么办？

A: 
1. **在浏览器中完成验证**：使用方法一，在浏览器中正常登录并完成验证码验证，然后从浏览器中提取 token
2. **在小米官网或 App 中登录一次**：先在官方渠道登录，解除安全限制
3. **等待一段时间**：如果频繁尝试登录，可能会被临时限制，等待几小时后再试

### Q: 我的 passToken 在哪里存储？

A: 
- 配置文件：`user_config.py` 中的 `MI_PASS_TOKEN`
- 运行时缓存：`.mi.token` 文件（自动生成，不要手动编辑）

### Q: 可以分享 passToken 吗？

A: **不可以！** passToken 相当于你的登录凭证，泄露后他人可以：
- 控制你的小爱音箱
- 访问你的米家设备
- 查看你的账号信息

请妥善保管，不要分享给任何人。

## 推荐配置

```python
# user_config.py

# 推荐配置：同时配置密码和 token
MI_USER = "your_account@example.com"
MI_PASS = "your_password"              # 用于自动刷新 token
MI_PASS_TOKEN = "V1:xxxxxxxx..."       # 避免频繁登录触发验证码

# 不推荐：只配置 token，不配置密码
# MI_PASS = ""
# MI_PASS_TOKEN = "V1:xxxxxxxx..."
# 问题：token 过期后无法自动刷新

# 不推荐：只配置密码，不配置 token
# MI_PASS = "your_password"
# MI_PASS_TOKEN = ""
# 问题：每次启动都需要登录，容易触发验证码
```

## 验证配置

配置完成后，可以通过以下方式验证：

```bash
# 查看日志
docker-compose logs -f backend

# 或者直接运行
cd backend
python3 -m xiaoai_media.api.main
```

成功的日志应该显示：
```
INFO xiaoai_media.client — MiService: using passToken auth for user xxx
INFO xiaoai_media.client — MiService: authentication successful
INFO xiaoai_media.client — MiService: cached X merged device(s)
```

如果看到错误，请检查：
1. passToken 是否正确（包括 `V1:` 前缀）
2. MI_USER 是否正确
3. 网络连接是否正常

## 参考资源

- [小米账号官网](https://account.xiaomi.com/)
- [miservice 库文档](https://github.com/Yonsm/MiService)
- 项目配置文档：`docs/config/USER_CONFIG_GUIDE.md`
