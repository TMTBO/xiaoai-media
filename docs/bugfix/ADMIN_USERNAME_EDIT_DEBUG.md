# Admin 用户名编辑功能调试指南

## 问题：前端页面无法编辑用户名

### 检查步骤

#### 1. 确认前端代码已更新

检查文件 `frontend/src/views/UserManagement.vue` 是否包含以下内容：

```vue
<el-form-item v-if="isEdit" label="新用户名">
  <el-input
    v-model="userForm.newUsername"
    placeholder="留空则不修改用户名"
    clearable
  />
</el-form-item>
```

#### 2. 重启前端开发服务器

如果你正在运行开发服务器，请重启：

```bash
cd frontend
npm run dev
```

#### 3. 清除浏览器缓存

- Chrome/Edge: 按 `Cmd+Shift+R` (Mac) 或 `Ctrl+Shift+R` (Windows/Linux) 进行硬刷新
- 或者打开开发者工具 (F12)，右键点击刷新按钮，选择"清空缓存并硬性重新加载"

#### 4. 检查浏览器控制台

打开浏览器开发者工具 (F12)，查看：

1. **Console 标签页**：是否有 JavaScript 错误？
2. **Network 标签页**：
   - 点击"编辑"按钮时，是否加载了最新的 Vue 组件？
   - 提交表单时，查看 PUT 请求的 payload 是否包含 `new_username` 字段

#### 5. 验证编辑对话框

当点击"编辑"按钮时，对话框应该显示：

- **当前用户名**：灰色禁用状态，显示原用户名
- **新用户名**：可编辑的输入框，带有清除按钮
- **密码**：可编辑，提示"留空则不修改密码"
- **角色**：下拉选择框

#### 6. 测试 API 请求

使用浏览器开发者工具的 Console，手动测试 API：

```javascript
// 获取当前 token
const token = localStorage.getItem('token');

// 测试更新用户名
fetch('/api/users/admin', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    new_username: 'superadmin',
    role: 'admin'
  })
})
.then(r => r.json())
.then(data => console.log('成功:', data))
.catch(err => console.error('错误:', err));
```

#### 7. 检查后端日志

查看后端日志，确认请求是否到达后端：

```bash
# 如果使用 Docker
docker-compose logs -f backend

# 如果直接运行
cd backend
python run.py
```

### 常见问题

#### 问题 1：对话框中没有"新用户名"字段

**原因**：前端代码未更新或浏览器缓存

**解决**：
1. 确认文件已保存
2. 硬刷新浏览器 (Cmd+Shift+R)
3. 重启开发服务器

#### 问题 2："新用户名"字段显示但无法输入

**原因**：可能是 Element Plus 组件问题

**解决**：
1. 检查浏览器控制台是否有错误
2. 确认 Element Plus 版本兼容
3. 尝试点击输入框，查看是否获得焦点

#### 问题 3：提交后报错 "无权修改用户名"

**原因**：当前登录用户不是管理员

**解决**：
1. 确认以管理员身份登录
2. 检查 localStorage 中的 role 是否为 'admin'：
   ```javascript
   console.log(localStorage.getItem('role'));
   ```

#### 问题 4：提交后报错 "用户名已存在"

**原因**：新用户名与现有用户冲突

**解决**：使用不同的用户名

### 验证功能是否正常

1. 以 admin 身份登录
2. 进入"用户管理"页面
3. 点击 admin 用户的"编辑"按钮
4. 应该看到：
   - 当前用户名：admin (禁用)
   - 新用户名：(空白，可输入)
   - 密码：(空白，可输入)
   - 角色：管理员
5. 在"新用户名"中输入 "superadmin"
6. 点击"确定"
7. 应该提示"用户名修改成功，请重新登录"
8. 自动跳转到登录页
9. 使用新用户名 "superadmin" 和原密码登录

### 如果问题仍然存在

请提供以下信息：

1. 浏览器控制台的错误信息（截图）
2. Network 标签页中 PUT 请求的详细信息
3. 后端日志输出
4. 当前使用的浏览器和版本
5. 是否使用 Docker 运行

### 临时测试页面

可以访问 `/test-user-edit.html` 查看一个简化的测试页面，验证表单逻辑是否正常。
