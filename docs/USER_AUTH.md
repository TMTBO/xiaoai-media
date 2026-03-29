# 用户认证功能说明

## 概述

XiaoAI Media 现已支持用户登录和权限管理功能，提供基于JWT的身份认证和基于角色的访问控制。

## 默认账户

系统初始化时会自动创建默认管理员账户：

- 用户名: `admin`
- 密码: `admin123`
- 角色: 管理员

**重要提示**: 首次登录后，建议立即修改默认密码以确保系统安全。

## 功能特性

### 1. 用户登录

- 访问系统时需要先登录
- 登录成功后获得JWT令牌，有效期7天
- 令牌过期或无效时自动跳转到登录页

### 2. 用户角色

系统支持两种用户角色：

- **管理员 (admin)**: 拥有所有权限，包括用户管理
- **普通用户 (user)**: 可以使用系统的所有功能，但无法管理其他用户

### 3. 用户管理（仅管理员）

管理员可以通过"用户管理"页面进行以下操作：

- 查看所有用户列表
- 创建新用户
- 编辑用户信息（修改密码、角色）
- 删除用户（不能删除admin账户）

### 4. 用户信息显示

登录后，用户信息会显示在左侧导航栏的底部，包括：

- 用户头像图标
- 用户名
- 角色标签
- 退出登录按钮

## API接口

### 认证接口

#### 登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "admin",
  "role": "admin"
}
```

#### 获取当前用户信息
```
GET /api/auth/me
Authorization: Bearer <token>

Response:
{
  "username": "admin",
  "role": "admin",
  "created_at": "2024-03-29T10:00:00"
}
```

### 用户管理接口（需要管理员权限）

#### 列出所有用户
```
GET /api/users
Authorization: Bearer <token>
```

#### 创建用户
```
POST /api/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "role": "user"
}
```

#### 更新用户
```
PUT /api/users/{username}
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "newpassword",  // 可选
  "role": "admin"             // 可选
}
```

#### 删除用户
```
DELETE /api/users/{username}
Authorization: Bearer <token>
```

## 数据存储

用户数据存储在 `~/.xiaoai_media/users.json` 文件中，包含：

- 用户名
- 密码哈希（SHA-256）
- 角色
- 创建时间

**注意**: 密码使用SHA-256哈希存储，不会以明文形式保存。

## 安全建议

1. **修改默认密码**: 首次部署后立即修改admin账户的默认密码
2. **使用强密码**: 创建用户时使用包含字母、数字和特殊字符的强密码
3. **定期更新**: 定期更新用户密码
4. **最小权限原则**: 仅在必要时授予管理员权限
5. **生产环境配置**: 在生产环境中，建议修改 `user_service.py` 中的 `SECRET_KEY` 为更安全的随机字符串

## 前端路由守卫

系统实现了路由守卫机制：

- 未登录用户访问任何页面都会被重定向到登录页
- 已登录用户访问登录页会被重定向到首页
- 普通用户访问用户管理页面会被重定向到首页
- 仅管理员可以看到和访问"用户管理"菜单项

## 开发说明

### 后端依赖

需要安装 `pyjwt` 库：

```bash
pip install pyjwt>=2.8.0
```

或使用项目的依赖管理：

```bash
cd backend
pip install -e .
```

### 前端实现

- 使用 axios 拦截器自动添加 Authorization 头
- 使用 localStorage 存储 token 和用户信息
- 使用 Vue Router 的 beforeEach 守卫实现路由保护

### 扩展开发

如需添加更多权限级别或功能，可以：

1. 在 `user_service.py` 中扩展 User 模型
2. 在 `auth.py` 中添加新的权限检查函数
3. 在前端路由中添加相应的 meta 字段
4. 在路由守卫中实现权限检查逻辑

## 故障排除

### 无法登录

1. 检查用户名和密码是否正确
2. 确认 `users.json` 文件存在且格式正确
3. 查看后端日志获取详细错误信息

### Token 过期

- Token 默认有效期为7天
- 过期后需要重新登录
- 可以在 `user_service.py` 中修改 `ACCESS_TOKEN_EXPIRE_MINUTES` 调整有效期

### 权限不足

- 确认当前用户角色是否满足要求
- 管理员功能仅对 role 为 "admin" 的用户开放

## 更新日志

- 2024-03-29: 初始版本发布
  - 实现基于JWT的用户认证
  - 实现基于角色的访问控制
  - 添加用户管理功能
  - 添加登录页面和用户信息显示
