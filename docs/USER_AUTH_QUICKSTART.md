# 用户认证功能快速开始

## 安装步骤

### 1. 安装后端依赖

```bash
cd backend
pip install -e .
```

这会自动安装包括 `pyjwt` 在内的所有依赖。

### 2. 启动后端服务

```bash
cd backend
python run.py
```

首次启动时，系统会自动创建默认管理员账户和用户数据文件。

### 3. 启动前端服务（开发模式）

```bash
cd frontend
npm install  # 如果还没有安装依赖
npm run dev
```

## 使用步骤

### 1. 访问登录页面

打开浏览器访问: `http://localhost:5173/login`

### 2. 使用默认账户登录

- 用户名: `admin`
- 密码: `admin123`

### 3. 修改默认密码（推荐）

1. 登录后，点击左侧菜单的"用户管理"
2. 找到 admin 用户，点击"编辑"
3. 输入新密码并保存

### 4. 创建新用户（可选）

1. 在"用户管理"页面点击"添加用户"
2. 填写用户名、密码和角色
3. 点击"确定"创建用户

### 5. 退出登录

点击左侧栏底部用户信息区域的菜单按钮，选择"退出登录"

## 文件位置

- 用户数据文件: `~/.xiaoai_media/users.json`
- 后端认证路由: `backend/src/xiaoai_media/api/routes/auth.py`
- 用户服务: `backend/src/xiaoai_media/services/user_service.py`
- 前端登录页面: `frontend/src/views/Login.vue`
- 前端用户管理: `frontend/src/views/UserManagement.vue`

## Docker 部署

如果使用 Docker 部署，用户数据会保存在容器的数据卷中。建议挂载 `~/.xiaoai_media` 目录以持久化用户数据：

```bash
docker run -v ~/.xiaoai_media:/root/.xiaoai_media ...
```

## 常见问题

**Q: 忘记密码怎么办？**

A: 可以直接删除 `~/.xiaoai_media/users.json` 文件，重启服务后会重新创建默认管理员账户。

**Q: 如何批量创建用户？**

A: 可以直接编辑 `users.json` 文件，或使用 API 接口批量创建。

**Q: 可以禁用登录功能吗？**

A: 目前不支持禁用。如果不需要多用户管理，可以只使用默认的 admin 账户。

## 下一步

查看完整文档: [docs/USER_AUTH.md](./USER_AUTH.md)
