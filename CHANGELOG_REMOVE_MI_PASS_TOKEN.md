# 移除 MI_PASS_TOKEN 配置项 - 变更日志

## 版本：v1.0.0

## 变更日期：2026-03-22

## 变更类型：Breaking Change（破坏性变更）

## 变更说明

移除了 `MI_PASS_TOKEN` 配置项，改用 `miservice` 库的 `token_store` 机制自动管理 token。

## 影响范围

### 后端

1. **配置模块**
   - ✅ `backend/src/xiaoai_media/config.py` - 移除 MI_PASS_TOKEN 配置项
   - ✅ `backend/src/xiaoai_media/api/routes/config.py` - 移除 API 字段
   - ✅ `backend/src/xiaoai_media/services/config_service.py` - 移除服务逻辑

2. **客户端模块**
   - ✅ `backend/src/xiaoai_media/client.py` - 使用 token_store 自动管理

3. **配置文件**
   - ✅ `user_config.py` - 移除 MI_PASS_TOKEN 配置
   - ✅ `user_config_template.py` - 更新模板

### 前端

1. **UI 组件**
   - ✅ `frontend/src/views/Settings.vue` - 移除 Pass Token 输入框
   - ✅ 添加 Token 自动管理提示

2. **类型定义**
   - ✅ `frontend/src/api/index.ts` - 移除 Config 接口中的 MI_PASS_TOKEN

### 文档

1. **开发文档**
   - ✅ `.github/copilot-instructions.md` - 更新开发指南

2. **用户文档**
   - ✅ `docs/conversation/QUICK_START.md` - 更新故障排查
   - ✅ `docs/tts/QUICK_TEST.md` - 更新错误提示
   - ✅ `docs/playback/PLAYBACK_TROUBLESHOOTING.md` - 更新错误码
   - ✅ `docs/config/GET_PASSTOKEN_GUIDE.md` - 标记为已过时
   - ✅ `docs/migration/REMOVE_MI_PASS_TOKEN.md` - 新建迁移指南

## 迁移指南

### 对于现有用户

1. **更新配置文件**

   编辑 `user_config.py`，删除 `MI_PASS_TOKEN` 行：
   
   ```python
   # 之前
   MI_USER = "your_account@example.com"
   MI_PASS = "your_password"
   MI_PASS_TOKEN = "V1:xxxxxxxx..."  # 删除这一行
   
   # 之后
   MI_USER = "your_account@example.com"
   MI_PASS = "your_password"
   ```

2. **清理旧 token 文件（可选）**

   ```bash
   rm .mi.token
   ```

3. **重启服务**

   ```bash
   docker-compose restart
   # 或
   make run
   ```

### 对于新用户

只需配置账号和密码：

```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
```

Token 会自动保存到 `.mi.token` 文件。

## 技术细节

### Token 管理机制

**之前**：手动配置 MI_PASS_TOKEN
```python
# 需要用户手动获取 token
MI_PASS_TOKEN = "V1:xxxxxxxx..."

# 客户端预注入 token
self._account.token = {
    "deviceId": "",
    "userId": config.MI_USER,
    "passToken": config.MI_PASS_TOKEN,
}
```

**现在**：自动管理
```python
# 用户只需配置密码
MI_PASS = "your_password"

# 使用 token_store 自动管理
self._account = MiAccount(
    self._session,
    config.MI_USER,
    config.MI_PASS,
    token_store=".mi.token",  # 自动保存/加载
)
```

### Token 文件格式

`.mi.token` 文件内容（自动生成）：
```json
{
  "deviceId": "...",
  "userId": "...",
  "passToken": "...",
  "micoapi": ["ssecurity", "serviceToken"],
  "xiaomiio": ["ssecurity", "serviceToken"]
}
```

### 工作流程

1. **首次启动**
   - 使用密码登录
   - 自动获取 micoapi 和 xiaomiio 的 token
   - 保存到 `.mi.token` 文件

2. **后续启动**
   - 从 `.mi.token` 加载 token
   - 如果有效，直接使用
   - 如果过期，自动重新登录

3. **Token 刷新**
   - 检测到 401 错误时自动重新登录
   - 更新 `.mi.token` 文件

## 优点

1. **简化配置**：用户只需配置账号密码
2. **自动管理**：token 自动保存、加载、刷新
3. **避免冲突**：正确处理 MiNA 和 MiIO 的不同 sid
4. **更可靠**：使用 miservice 的标准机制

## 注意事项

1. **首次登录可能需要验证码**
   - 在小米官网或 App 中登录一次即可
   - 参考：`docs/migration/MIIO_AUTH_FIX.md`

2. **密码必须配置**
   - Token 过期时需要密码重新登录
   - 不建议只依赖 token

3. **Token 文件安全**
   - `.mi.token` 包含敏感信息
   - 已添加到 `.gitignore`
   - 不要提交到版本控制

## 相关 PR/Issue

- 修复 MiIO 认证冲突问题
- 实现全局客户端单例模式
- 简化用户配置流程

## 测试

### 后端测试

```bash
# 语法检查
python3 -m py_compile backend/src/xiaoai_media/config.py
python3 -m py_compile backend/src/xiaoai_media/client.py
python3 -m py_compile backend/src/xiaoai_media/services/config_service.py

# 启动测试
make run
```

### 前端测试

```bash
# 类型检查
cd frontend
npm run type-check

# 构建测试
npm run build
```

### 功能测试

1. 删除旧配置中的 MI_PASS_TOKEN
2. 重启服务
3. 检查日志，应该只有一次登录
4. 检查 `.mi.token` 文件是否生成
5. 再次重启，应该直接使用已保存的 token

## 回滚方案

如果需要回滚到旧版本：

1. 恢复 `MI_PASS_TOKEN` 配置项到代码中
2. 手动获取 token 并配置
3. 重启服务

但不建议回滚，新机制更可靠。

## 后续计划

- [ ] 添加 token 状态查看 API
- [ ] 添加手动刷新 token 的功能
- [ ] 优化首次登录的验证码处理

## 贡献者

- @xpeng - 实现和文档

## 参考资源

- [miservice 库文档](https://github.com/Yonsm/MiService)
- [小米账号开发文档](https://dev.mi.com/docs/passport/)
- `docs/migration/REMOVE_MI_PASS_TOKEN.md` - 详细迁移指南
- `docs/migration/MIIO_AUTH_FIX.md` - MiIO 认证修复
