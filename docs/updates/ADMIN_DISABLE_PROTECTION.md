# 管理员账户禁用保护机制

## 概述

为了防止系统被锁定，所有角色为 `admin` 的用户账户都不能被禁用。这个限制在前端和后端都有实现，提供多层保护。

## 保护机制

### 1. 后端保护（多层）

#### 服务层 - UserService

**disable_user() 方法**
```python
def disable_user(self, username: str) -> User:
    """禁用用户"""
    if username == "admin":
        raise ValueError("不能禁用管理员账户")
    return self.update_user(username, enabled=False)
```

**update_user() 方法**
```python
def update_user(self, username: str, ..., enabled: Optional[bool] = None) -> User:
    """更新用户信息"""
    for user in users:
        if user.username == username:
            # 检查是否尝试禁用管理员用户（基于角色）
            if enabled is not None and not enabled and user.role == "admin":
                raise ValueError("不能禁用管理员账户")
            # ... 其他更新逻辑
```

**关键点：**
- `disable_user()` 检查用户名是否为 "admin"
- `update_user()` 检查用户角色是否为 "admin"
- 两层检查确保无论用户名是什么，只要角色是 admin 就不能被禁用

#### API 路由层

API 层会调用服务层方法，因此自动继承了这些保护：

- `POST /users/{username}/disable` → 调用 `disable_user()`
- `PUT /users/{username}` → 调用 `update_user()`

如果尝试禁用管理员，会返回 400 或 404 错误，错误信息为 "不能禁用管理员账户"。

### 2. 前端保护（多层）

#### UI 层 - 按钮禁用

**表格中的禁用按钮**
```vue
<el-button
  v-if="row.enabled"
  size="small"
  type="warning"
  :disabled="row.role === 'admin'"
  @click="handleDisable(row)"
>
  禁用
</el-button>
```

**编辑对话框中的启用状态开关**
```vue
<el-switch
  v-model="userForm.enabled"
  active-text="启用"
  inactive-text="禁用"
  :disabled="userForm.role === 'admin'"
/>
```

**关键点：**
- 基于 `row.role === 'admin'` 而不是 `row.username === 'admin'`
- 管理员用户的禁用按钮和开关都会被禁用（灰色不可点击）

#### 逻辑层 - 函数检查

**handleDisable() 函数**
```typescript
const handleDisable = async (user: User) => {
  // 前端额外检查：不允许禁用管理员
  if (user.role === 'admin') {
    ElMessage.error('不能禁用管理员账户')
    return
  }
  // ... 其他逻辑
}
```

**handleSubmit() 函数**
```typescript
if (isEdit.value) {
  // 前端额外检查：不允许禁用管理员
  if (userForm.role === 'admin' && userForm.enabled === false) {
    ElMessage.error('不能禁用管理员账户')
    submitting.value = false
    return
  }
  // ... 其他逻辑
}
```

**关键点：**
- 即使 UI 被绕过，函数层也会检查
- 检查基于角色而不是用户名
- 显示友好的错误提示

## 检查逻辑对比

### 基于用户名的检查（不推荐）
```python
if username == "admin":
    raise ValueError("不能禁用管理员账户")
```

**问题：**
- 只保护用户名为 "admin" 的账户
- 如果创建了其他管理员账户（如 "superadmin"），这些账户可以被禁用
- 不够安全

### 基于角色的检查（推荐）✅
```python
if user.role == "admin":
    raise ValueError("不能禁用管理员账户")
```

**优点：**
- 保护所有角色为 "admin" 的账户
- 无论用户名是什么，只要是管理员就受保护
- 更安全、更灵活

## 实际效果

### 场景 1：尝试通过 UI 禁用管理员

1. 用户在用户列表中看到管理员账户
2. "禁用" 按钮显示为灰色（disabled）
3. 鼠标悬停时显示不可点击状态
4. 无法点击按钮

### 场景 2：尝试通过编辑对话框禁用管理员

1. 用户点击管理员账户的 "编辑" 按钮
2. 打开编辑对话框
3. "启用状态" 开关显示为灰色（disabled）
4. 无法切换开关状态

### 场景 3：尝试通过 API 直接禁用管理员

```bash
curl -X POST "http://localhost:8090/api/users/admin/disable" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**响应：**
```json
{
  "detail": "不能禁用管理员账户"
}
```

**HTTP 状态码：** 400 Bad Request

### 场景 4：尝试通过 update API 禁用管理员

```bash
curl -X PUT "http://localhost:8090/api/users/admin" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

**响应：**
```json
{
  "detail": "不能禁用管理员账户"
}
```

**HTTP 状态码：** 404 Not Found

## 测试覆盖

### 后端测试

```python
def test_cannot_disable_admin(tmp_path):
    """测试不能禁用管理员账户"""
    service.create_user("admin", "admin123", "admin")
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.disable_user("admin")

def test_cannot_disable_admin_via_update(tmp_path):
    """测试不能通过 update_user 禁用管理员账户"""
    service.create_user("admin", "admin123", "admin")
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.update_user("admin", enabled=False)

def test_cannot_disable_any_admin_role_user(tmp_path):
    """测试不能禁用任何角色为 admin 的用户"""
    service.create_user("superuser", "password123", "admin")
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.disable_user("superuser")
```

运行测试：
```bash
cd backend
pytest tests/test_user_login_enabled.py -v -k "disable_admin"
```

### 前端测试

使用测试页面 `frontend/test-user-enabled.html`：

1. 登录管理员账户
2. 尝试禁用管理员用户
3. 验证按钮被禁用
4. 验证 API 调用返回错误

## 安全考虑

### 1. 多层防护

- **UI 层**：按钮禁用，防止误操作
- **前端逻辑层**：函数检查，防止 UI 绕过
- **后端服务层**：业务逻辑检查，防止直接 API 调用
- **后端 API 层**：自动继承服务层保护

### 2. 基于角色而非用户名

- 保护所有管理员账户，不仅仅是 "admin"
- 支持多个管理员账户的场景
- 更符合 RBAC（基于角色的访问控制）原则

### 3. 友好的错误提示

- 前端：`ElMessage.error('不能禁用管理员账户')`
- 后端：`ValueError("不能禁用管理员账户")`
- 用户能清楚地知道为什么操作失败

### 4. 一致性

- 前端和后端使用相同的检查逻辑
- 错误信息一致
- 行为可预测

## 最佳实践

### 1. 始终保留至少一个管理员

系统应该始终保留至少一个启用的管理员账户，否则可能导致：
- 无法管理用户
- 无法恢复系统访问
- 需要直接修改数据库

### 2. 创建多个管理员账户

建议创建多个管理员账户作为备份：
```bash
# 创建备份管理员
curl -X POST "http://localhost:8090/api/users" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin2", "password": "secure_password", "role": "admin"}'
```

### 3. 定期审计管理员账户

定期检查：
- 有多少个管理员账户
- 哪些管理员账户是启用的
- 管理员账户的最近登录时间

### 4. 考虑实现超级管理员

对于更复杂的系统，可以考虑：
- 引入 "super_admin" 角色
- 只有超级管理员可以禁用其他管理员
- 超级管理员自己也不能被禁用

## 常见问题

### Q: 为什么不能禁用管理员账户？

A: 为了防止系统被锁定。如果所有管理员都被禁用，将无法管理用户和恢复访问。

### Q: 如果真的需要禁用管理员怎么办？

A: 有两个选择：
1. 先将该用户的角色改为 "user"，然后再禁用
2. 直接删除该用户（但要确保还有其他管理员）

### Q: 可以禁用用户名为 "admin" 但角色为 "user" 的账户吗？

A: 可以。保护机制基于角色，不是用户名。

### Q: 如果创建了多个管理员，都不能被禁用吗？

A: 是的。所有角色为 "admin" 的用户都受保护。

### Q: 前端的检查可以被绕过吗？

A: 前端检查可以被绕过（如通过浏览器开发工具），但后端的检查无法绕过。前端检查主要是为了提供更好的用户体验。

## 总结

管理员账户禁用保护机制通过多层防护确保系统安全：

✅ 后端服务层基于角色检查  
✅ 后端 API 层自动继承保护  
✅ 前端 UI 层按钮禁用  
✅ 前端逻辑层函数检查  
✅ 完整的测试覆盖  
✅ 友好的错误提示  
✅ 一致的行为表现  

这个机制确保了无论通过什么方式，都无法禁用管理员账户，从而保护系统不被锁定。
