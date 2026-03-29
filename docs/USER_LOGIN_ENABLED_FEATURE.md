# 用户最近登录时间和启用开关功能

## 功能概述

新增了两个用户管理功能：
1. 最近登录时间跟踪
2. 用户启用/禁用开关

## 数据模型变更

### User 模型新增字段

```python
class User:
    username: str
    password_hash: str
    role: str
    created_at: str
    last_login: str | None  # 新增：最近登录时间
    enabled: bool = True    # 新增：启用状态
```

### 用户数据示例

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

## API 变更

### 1. 用户信息响应

所有返回用户信息的接口现在包含新字段：

```json
{
  "username": "testuser",
  "role": "user",
  "created_at": "2026-03-29T21:14:18.037715",
  "last_login": "2026-03-29T22:30:45.123456",
  "enabled": true
}
```

### 2. 登录接口变更

`POST /auth/login`

- 登录成功时自动更新 `last_login` 字段为当前时间
- 如果用户被禁用（`enabled: false`），返回 401 错误

### 3. 更新用户接口

`PUT /users/{username}`

新增 `enabled` 字段支持：

```json
{
  "new_username": "newname",
  "password": "newpassword",
  "role": "admin",
  "enabled": false
}
```

权限要求：
- 只有管理员可以修改 `enabled` 字段
- 普通用户无权修改启用状态

### 4. 新增启用/禁用接口

#### 启用用户
`POST /users/{username}/enable`

- 需要管理员权限
- 将用户的 `enabled` 设置为 `true`

#### 禁用用户
`POST /users/{username}/disable`

- 需要管理员权限
- 将用户的 `enabled` 设置为 `false`
- 不能禁用 admin 账户

## 使用场景

### 1. 查看用户最近登录时间

```bash
curl -X GET "http://localhost:8090/users" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

响应中包含每个用户的 `last_login` 字段。

### 2. 禁用用户

```bash
curl -X POST "http://localhost:8090/users/testuser/disable" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 3. 启用用户

```bash
curl -X POST "http://localhost:8090/users/testuser/enable" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 4. 通过更新接口修改启用状态

```bash
curl -X PUT "http://localhost:8090/users/testuser" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

## 业务逻辑

### 最近登录时间
- 初始值为 `null`
- 每次成功登录时自动更新为当前时间
- 用于追踪用户活跃度

### 启用开关
- 新用户默认启用（`enabled: true`）
- 禁用的用户无法登录
- 管理员账户不能被禁用
- 用于临时禁止用户访问而不删除账户

## 数据迁移

现有用户数据会自动兼容：
- `last_login` 默认为 `null`
- `enabled` 默认为 `true`

如需手动更新现有数据，编辑 `.xiaoai_media/users.json`：

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

## 安全考虑

1. 禁用用户后，其现有 token 仍然有效直到过期
2. 建议配合 token 刷新机制使用
3. 管理员账户受保护，不能被禁用
4. 只有管理员可以修改用户启用状态

## 测试

运行测试验证功能：

```bash
cd backend
pytest tests/test_user_login_enabled.py -v
```
