# 用户最近登录时间和启用开关功能 - 完整实现

## 概述

本次更新为用户管理系统添加了两个重要功能：
1. **最近登录时间跟踪** - 记录用户每次登录的时间
2. **用户启用/禁用开关** - 允许管理员临时禁用用户账户

## 后端实现

### 数据模型变更

#### User 类 (`backend/src/xiaoai_media/services/user_service.py`)

```python
class User:
    def __init__(self, username: str, password_hash: str, role: str = "user", 
                 created_at: str = None, last_login: str = None, enabled: bool = True):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login      # 新增
        self.enabled = enabled            # 新增
```

### 服务层变更

#### UserService 类新增/修改的方法

1. **authenticate()** - 修改
   - 检查用户是否被禁用
   - 登录成功时更新 `last_login` 字段

2. **update_user()** - 修改
   - 新增 `enabled` 参数

3. **enable_user()** - 新增
   - 启用指定用户

4. **disable_user()** - 新增
   - 禁用指定用户（不能禁用 admin）

### API 端点变更

#### 修改的端点

**POST /auth/login**
- 登录成功时自动更新 `last_login`
- 禁用用户返回 401 错误

**PUT /users/{username}**
- 新增 `enabled` 字段支持
- 只有管理员可以修改 `enabled` 字段

**GET /users**
- 返回数据包含 `last_login` 和 `enabled` 字段

#### 新增的端点

**POST /users/{username}/enable**
- 启用指定用户
- 需要管理员权限

**POST /users/{username}/disable**
- 禁用指定用户
- 需要管理员权限
- 不能禁用 admin 账户

### 数据结构

#### 用户 JSON 格式

```json
{
  "username": "testuser",
  "password_hash": "...",
  "role": "user",
  "created_at": "2026-03-29T21:14:18.037715",
  "last_login": "2026-03-29T22:30:45.123456",
  "enabled": true
}
```

## 前端实现

### API 接口更新 (`frontend/src/api/auth.ts`)

#### 类型定义

```typescript
interface UserInfo {
    username: string
    role: string
    created_at: string
    last_login?: string      // 新增
    enabled: boolean         // 新增
}

interface UpdateUserRequest {
    new_username?: string
    password?: string
    role?: string
    enabled?: boolean        // 新增
}
```

#### 新增函数

```typescript
// 启用用户
export async function enableUser(username: string): Promise<UserInfo>

// 禁用用户
export async function disableUser(username: string): Promise<UserInfo>
```

### 用户管理界面更新 (`frontend/src/views/UserManagement.vue`)

#### 表格新增列

1. **状态列**
   - 显示启用/禁用状态
   - 使用彩色标签

2. **最近登录列**
   - 显示最后登录时间
   - 从未登录显示 "从未登录"

#### 操作按钮

- **编辑按钮** - 打开编辑对话框
- **启用/禁用按钮** - 快速切换用户状态
- **删除按钮** - 删除用户

#### 编辑对话框

新增 "启用状态" 开关：
- 仅编辑模式显示
- admin 账户不可修改
- 可与其他字段一起修改

## 使用指南

### 管理员操作

#### 1. 查看用户状态

访问用户管理页面，可以看到：
- 每个用户的启用状态
- 最近登录时间
- 从未登录的用户会显示 "从未登录"

#### 2. 禁用用户

方法一：快速禁用
1. 在用户列表中找到目标用户
2. 点击 "禁用" 按钮
3. 确认操作

方法二：通过编辑
1. 点击 "编辑" 按钮
2. 关闭 "启用状态" 开关
3. 保存修改

#### 3. 启用用户

方法一：快速启用
1. 在用户列表中找到被禁用的用户
2. 点击 "启用" 按钮

方法二：通过编辑
1. 点击 "编辑" 按钮
2. 打开 "启用状态" 开关
3. 保存修改

#### 4. 查看登录历史

在用户列表的 "最近登录" 列查看每个用户的最后登录时间。

### API 调用示例

#### 禁用用户

```bash
curl -X POST "http://localhost:8090/api/users/testuser/disable" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 启用用户

```bash
curl -X POST "http://localhost:8090/api/users/testuser/enable" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 查看用户列表（包含新字段）

```bash
curl -X GET "http://localhost:8090/api/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

响应示例：
```json
[
  {
    "username": "testuser",
    "role": "user",
    "created_at": "2026-03-29T21:14:18.037715",
    "last_login": "2026-03-29T22:30:45.123456",
    "enabled": true
  }
]
```

## 业务逻辑

### 最近登录时间

- **初始值**: `null`（从未登录）
- **更新时机**: 每次成功登录时自动更新
- **用途**: 
  - 追踪用户活跃度
  - 识别长期未使用的账户
  - 安全审计

### 启用开关

- **默认值**: `true`（新用户默认启用）
- **禁用效果**: 用户无法登录
- **保护机制**: admin 账户不能被禁用
- **用途**:
  - 临时禁止用户访问
  - 不删除用户数据
  - 可随时恢复访问

## 安全考虑

### 1. Token 有效性

禁用用户后，其现有的 token 仍然有效直到过期。建议：
- 设置合理的 token 过期时间
- 考虑实现 token 黑名单机制
- 或在每次请求时检查用户启用状态

### 2. 权限控制

- 只有管理员可以启用/禁用用户
- admin 账户受保护，不能被禁用
- 普通用户无法修改任何用户的启用状态

### 3. 审计日志

建议记录以下操作：
- 用户被禁用的时间和操作者
- 用户被启用的时间和操作者
- 禁用用户尝试登录的记录

## 测试

### 后端测试

运行单元测试：
```bash
cd backend
pytest tests/test_user_login_enabled.py -v
```

测试覆盖：
- 用户模型包含新字段
- 用户默认启用
- 登录时更新最近登录时间
- 禁用用户无法登录
- 启用/禁用用户功能
- 不能禁用 admin 账户

### 前端测试

使用测试页面：
```
http://localhost:5173/test-user-enabled.html
```

测试场景：
1. 禁用用户后尝试登录
2. 启用用户后登录
3. 验证最近登录时间更新
4. 验证 UI 显示正确

### 集成测试

1. 创建新用户，验证默认启用
2. 禁用用户，尝试登录（应失败）
3. 启用用户，尝试登录（应成功）
4. 验证最近登录时间在登录后更新
5. 验证 admin 账户不能被禁用

## 数据迁移

### 现有数据兼容性

现有用户数据会自动兼容：
- `last_login` 默认为 `null`
- `enabled` 默认为 `true`

### 手动迁移

如需手动更新 `.xiaoai_media/users.json`：

```json
[
  {
    "username": "existing_user",
    "password_hash": "...",
    "role": "user",
    "created_at": "2026-03-29T21:14:18.037715",
    "last_login": null,
    "enabled": true
  }
]
```

## 文件清单

### 后端文件

- `backend/src/xiaoai_media/services/user_service.py` - 用户服务（已修改）
- `backend/src/xiaoai_media/api/routes/auth.py` - 认证路由（已修改）
- `backend/tests/test_user_login_enabled.py` - 单元测试（新增）
- `.xiaoai_media/users.json` - 用户数据（已更新）

### 前端文件

- `frontend/src/api/auth.ts` - API 接口（已修改）
- `frontend/src/views/UserManagement.vue` - 用户管理界面（已修改）
- `frontend/test-user-enabled.html` - 测试页面（新增）

### 文档文件

- `docs/USER_LOGIN_ENABLED_FEATURE.md` - 功能说明
- `docs/frontend/USER_LOGIN_ENABLED_UI.md` - 前端界面说明
- `docs/USER_LOGIN_ENABLED_COMPLETE.md` - 完整实现文档（本文件）

## 后续优化建议

### 1. Token 黑名单

实现 token 黑名单机制，禁用用户时立即使其 token 失效。

### 2. 审计日志

记录用户启用/禁用操作的完整日志。

### 3. 批量操作

支持批量启用/禁用多个用户。

### 4. 自动禁用

根据规则自动禁用长期未登录的用户。

### 5. 通知机制

用户被禁用时发送通知（邮件/短信）。

### 6. 登录历史

记录完整的登录历史，而不仅仅是最近一次。

## 常见问题

### Q: 禁用用户后，其现有 token 还能用吗？

A: 是的，现有 token 在过期前仍然有效。建议实现 token 黑名单或在每次请求时检查用户状态。

### Q: 可以禁用 admin 账户吗？

A: 不可以。系统会阻止禁用 admin 账户的操作。

### Q: 禁用和删除用户有什么区别？

A: 禁用是临时的，可以随时恢复；删除是永久的，会丢失用户数据。

### Q: 最近登录时间的精度是多少？

A: 精确到秒，使用 ISO 8601 格式存储。

### Q: 如何查看从未登录过的用户？

A: 在用户列表中，`last_login` 为 `null` 的用户会显示 "从未登录"。

## 总结

本次更新为用户管理系统添加了重要的安全和审计功能：

✅ 后端完整实现最近登录时间和启用开关
✅ 前端界面完整支持新功能
✅ API 端点完整更新
✅ 单元测试覆盖核心功能
✅ 测试页面方便功能验证
✅ 完整的文档说明

系统现在可以更好地管理用户账户，提供更强的安全控制能力。
