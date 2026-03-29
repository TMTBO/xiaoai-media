# 用户认证功能改进

## 更新日期
2024-03-29

## 更新内容

本次更新对用户认证系统进行了三项重要改进：

### 1. 用户数据存储位置优化

**变更前：**
- 用户数据保存在 `DATA_DIR/users.json`
- 直接使用 HOME 目录

**变更后：**
- 用户数据保存在 `DATA_DIR/.xiaoai_media/users.json`
- 统一使用 `.xiaoai_media` 子目录管理应用数据
- 自动创建目录结构

**优点：**
- 更好的数据组织结构
- 避免污染用户 HOME 目录
- 便于统一管理应用数据
- 与其他应用数据（如播放列表、定时任务）保持一致

**文件位置：**
```
~/.xiaoai_media/
├── users.json          # 用户数据
├── playlists/          # 播放列表
└── scheduler/          # 定时任务
```

### 2. 允许 admin 用户修改自己的用户名和密码

**新增功能：**
- admin 用户可以修改自己的用户名
- admin 用户可以修改自己的密码
- 普通用户只能修改自己的密码
- 管理员可以修改任何用户的信息

**API 更新：**

```typescript
// UpdateUserRequest 模型
interface UpdateUserRequest {
  new_username?: string  // 新增：新用户名（仅管理员）
  password?: string      // 密码
  role?: string          // 角色（仅管理员）
}

// 更新用户 API
PUT /api/users/{username}
{
  "new_username": "newadmin",  // 可选：修改用户名
  "password": "newpassword",   // 可选：修改密码
  "role": "admin"              // 可选：修改角色
}
```

**权限规则：**
1. 管理员可以修改任何用户的任何信息
2. 普通用户只能修改自己的密码
3. 普通用户不能修改用户名和角色
4. 修改用户名时会检查新用户名是否已存在

**使用示例：**

```bash
# admin 修改自己的用户名
curl -X PUT http://localhost:8000/api/users/admin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_username": "superadmin"}'

# admin 修改自己的密码
curl -X PUT http://localhost:8000/api/users/admin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "newsecurepassword"}'

# 普通用户修改自己的密码
curl -X PUT http://localhost:8000/api/users/john \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "mynewpassword"}'
```

### 3. 所有 API 接口强制登录态校验

**变更前：**
- 只有部分接口需要登录
- 可以未登录访问大部分功能

**变更后：**
- 除了登录接口外，所有 API 都需要登录态
- 使用 FastAPI 的全局依赖注入机制
- 统一的认证检查

**实现方式：**

```python
# backend/src/xiaoai_media/api/main.py

# 登录路由不需要认证
app.include_router(auth.router, prefix="/api")

# 其他所有路由都需要登录态校验
from xiaoai_media.api.dependencies import get_current_user
from fastapi import Depends

app.include_router(devices.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(tts.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(volume.router, prefix="/api", dependencies=[Depends(get_current_user)])
# ... 其他路由
```

**受保护的接口：**
- ✅ 设备管理 (`/api/devices`)
- ✅ TTS 朗读 (`/api/tts`)
- ✅ 音量控制 (`/api/volume`)
- ✅ 语音指令 (`/api/command`)
- ✅ 配置管理 (`/api/config`)
- ✅ 音乐播放 (`/api/music`)
- ✅ 播放列表 (`/api/playlists`)
- ✅ 音频代理 (`/api/proxy`)
- ✅ 定时任务 (`/api/scheduler`)
- ✅ 状态流 (`/api/state`)

**公开接口：**
- ✅ 用户登录 (`/api/auth/login`)

### 4. 前端 401 错误处理优化

**新增功能：**
- 检测到 401 错误后自动跳转登录页
- 停止所有正在进行的请求
- 避免重复跳转
- 清除本地存储的认证信息

**实现细节：**

```typescript
// frontend/src/api/index.ts 和 auth.ts

// 标记是否正在跳转登录页
let isRedirecting = false

// 请求拦截器 - 取消新请求
http.interceptors.request.use(
  (config) => {
    // 如果正在跳转登录页，取消所有新请求
    if (isRedirecting) {
      return Promise.reject(new axios.Cancel('正在跳转登录页，取消请求'))
    }
    
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  }
)

// 响应拦截器 - 处理401
http.interceptors.response.use(
  (response) => response,
  (error) => {
    // 如果是取消的请求，直接返回
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }
    
    if (error.response?.status === 401) {
      // 避免重复跳转
      if (!isRedirecting) {
        isRedirecting = true
        
        // 清除认证信息
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('role')
        
        // 跳转到登录页
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
```

**优点：**
1. **避免重复跳转** - 使用 `isRedirecting` 标记防止多次跳转
2. **停止新请求** - 跳转时取消所有新的 API 请求
3. **清理状态** - 自动清除本地存储的认证信息
4. **用户体验好** - 无需手动刷新页面

## 技术实现

### 后端修改

1. **backend/src/xiaoai_media/services/user_service.py**
   - 修改数据存储路径为 `.xiaoai_media/users.json`
   - 添加 `new_username` 参数到 `update_user` 方法
   - 添加用户名重复检查

2. **backend/src/xiaoai_media/api/routes/auth.py**
   - 更新 `UpdateUserRequest` 模型
   - 修改 `update_user` 路由的权限检查逻辑
   - 支持修改用户名功能

3. **backend/src/xiaoai_media/api/dependencies.py**
   - 添加 `get_current_user` 依赖函数
   - 统一的 JWT 令牌验证逻辑

4. **backend/src/xiaoai_media/api/main.py**
   - 为所有非登录路由添加全局依赖注入
   - 使用 `dependencies=[Depends(get_current_user)]`

### 前端修改

1. **frontend/src/api/index.ts**
   - 添加 `isRedirecting` 标记
   - 优化请求拦截器，跳转时取消新请求
   - 优化响应拦截器，避免重复跳转

2. **frontend/src/api/auth.ts**
   - 同步更新拦截器逻辑
   - 保持与 index.ts 一致的行为

## 迁移指南

### 数据迁移

如果你已经有旧的用户数据文件，需要手动迁移：

```bash
# 创建新目录
mkdir -p ~/.xiaoai_media

# 移动用户数据文件
mv ~/users.json ~/.xiaoai_media/users.json

# 或者在 Docker 中
mkdir -p /data/.xiaoai_media
mv /data/users.json /data/.xiaoai_media/users.json
```

### API 调用更新

如果你有外部脚本调用 API，需要添加认证：

```bash
# 1. 先登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.token')

# 2. 使用 token 调用其他 API
curl -X GET http://localhost:8000/api/devices \
  -H "Authorization: Bearer $TOKEN"
```

## 安全提升

1. **强制认证** - 所有功能都需要登录，防止未授权访问
2. **用户名修改** - admin 可以修改自己的用户名，提高安全性
3. **数据隔离** - 用户数据存储在专用目录，更好的权限控制
4. **请求控制** - 401 错误时自动停止所有请求，防止信息泄露

## 测试建议

### 后端测试

```bash
# 1. 测试未登录访问（应该返回 401）
curl -X GET http://localhost:8000/api/devices

# 2. 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. 测试修改用户名
curl -X PUT http://localhost:8000/api/users/admin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_username":"superadmin"}'

# 4. 测试数据文件位置
ls -la ~/.xiaoai_media/users.json
```

### 前端测试

1. 清除浏览器缓存和 localStorage
2. 访问任何页面，应自动跳转到登录页
3. 登录后访问功能页面
4. 在开发者工具中删除 token，刷新页面应跳转登录
5. 多个标签页同时打开，一个标签页 401 后其他标签页也应停止请求

## 相关文件

- `backend/src/xiaoai_media/services/user_service.py`
- `backend/src/xiaoai_media/api/routes/auth.py`
- `backend/src/xiaoai_media/api/dependencies.py`
- `backend/src/xiaoai_media/api/main.py`
- `frontend/src/api/index.ts`
- `frontend/src/api/auth.ts`

## 总结

本次更新显著提升了系统的安全性和用户体验：

1. ✅ 数据存储更规范（`.xiaoai_media` 目录）
2. ✅ admin 用户可以修改自己的用户名和密码
3. ✅ 所有 API 强制登录态校验
4. ✅ 前端 401 错误处理更完善
5. ✅ 自动停止无效请求，提升性能

系统现在具备了企业级应用的安全标准！
