# FastAPI 依赖注入说明 - 全局认证

## 问题

在 `main.py` 中加了全局的依赖注入后，其他接口上还需要单独添加吗？

## 答案

**不需要！** 在 `main.py` 中使用全局依赖注入后，其他接口上就不需要再单独添加了。

## 工作原理

### 全局依赖注入

在 `main.py` 中，我们为每个 router 添加了全局依赖：

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

### 依赖传播

当你在 `include_router` 时添加 `dependencies` 参数：

```python
app.include_router(devices.router, prefix="/api", dependencies=[Depends(get_current_user)])
```

这个依赖会**自动应用到该 router 下的所有路由**，包括：
- 所有的 GET 请求
- 所有的 POST 请求
- 所有的 PUT 请求
- 所有的 DELETE 请求
- 所有的 PATCH 请求

### 示例

假设 `devices.py` 中有这样的路由：

```python
# backend/src/xiaoai_media/api/routes/devices.py

@router.get("")
async def list_devices(
    refresh: bool = Query(False),
    client: XiaoAiClient = Depends(get_client),
):
    """List all devices."""
    # 这个函数会自动执行 get_current_user 依赖
    # 不需要在参数中添加 current_user
    ...
```

当请求到达时，FastAPI 会：
1. 先执行全局依赖 `get_current_user`（验证 JWT token）
2. 如果验证失败，返回 401 错误
3. 如果验证成功，继续执行路由函数

## 优点

### 1. 代码简洁

**不推荐（冗余）：**
```python
@router.get("")
async def list_devices(
    client: XiaoAiClient = Depends(get_client),
    current_user: dict = Depends(get_current_user),  # 冗余！
):
    ...
```

**推荐（简洁）：**
```python
@router.get("")
async def list_devices(
    client: XiaoAiClient = Depends(get_client),
):
    # get_current_user 已经在全局执行了
    ...
```

### 2. 统一管理

所有的认证逻辑集中在 `main.py` 中，便于：
- 统一修改认证策略
- 添加或移除需要认证的路由
- 查看哪些路由需要认证

### 3. 避免遗漏

使用全局依赖注入，不会因为忘记添加 `current_user` 参数而导致安全漏洞。

## 何时需要访问用户信息

如果你的路由函数需要访问当前用户的信息（如用户名、角色），可以添加参数：

```python
@router.get("/my-data")
async def get_my_data(
    current_user: dict = Depends(get_current_user),
):
    username = current_user["sub"]
    role = current_user["role"]
    
    # 根据用户信息返回数据
    return {"username": username, "role": role}
```

但这是**可选的**，只在需要用户信息时才添加。

## 依赖注入的优先级

FastAPI 的依赖注入有以下优先级：

1. **应用级别** - `app.include_router(..., dependencies=[...])`
2. **路由器级别** - `APIRouter(..., dependencies=[...])`
3. **路由级别** - `@router.get(..., dependencies=[...])`
4. **函数参数** - `async def func(dep = Depends(...))`

所有级别的依赖都会执行，从上到下依次执行。

## 当前实现

### 需要认证的路由

所有这些路由都通过全局依赖注入自动要求认证：

- ✅ `/api/devices` - 设备管理
- ✅ `/api/tts` - TTS 朗读
- ✅ `/api/volume` - 音量控制
- ✅ `/api/command` - 语音指令
- ✅ `/api/config` - 配置管理
- ✅ `/api/music` - 音乐播放
- ✅ `/api/playlists` - 播放列表
- ✅ `/api/proxy` - 音频代理
- ✅ `/api/scheduler` - 定时任务
- ✅ `/api/state` - 状态流

### 不需要认证的路由

只有登录相关的路由不需要认证：

- ✅ `/api/auth/login` - 用户登录

## 代码清理

我们已经移除了各个路由文件中冗余的 `current_user` 参数和 `get_current_user` 导入：

**清理前：**
```python
from xiaoai_media.api.dependencies import get_client, get_current_user

@router.get("")
async def list_devices(
    client: XiaoAiClient = Depends(get_client),
    current_user: dict = Depends(get_current_user),  # 冗余
):
    ...
```

**清理后：**
```python
from xiaoai_media.api.dependencies import get_client

@router.get("")
async def list_devices(
    client: XiaoAiClient = Depends(get_client),
):
    # 认证已在全局处理
    ...
```

## 测试

### 测试认证是否生效

```bash
# 1. 未登录访问（应该返回 401）
curl -X GET http://localhost:8000/api/devices
# 预期: {"detail":"未授权"}

# 2. 登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.token')

# 3. 使用 token 访问（应该成功）
curl -X GET http://localhost:8000/api/devices \
  -H "Authorization: Bearer $TOKEN"
# 预期: {"devices":[...]}
```

## 总结

- ✅ 全局依赖注入已在 `main.py` 中配置
- ✅ 所有路由自动要求认证（除了 `/api/auth/login`）
- ✅ 不需要在每个路由函数中添加 `current_user` 参数
- ✅ 代码更简洁、更安全、更易维护
- ✅ 已清理冗余的依赖注入代码

**记住：在 FastAPI 中，全局依赖注入会自动应用到所有子路由，无需重复添加！**
