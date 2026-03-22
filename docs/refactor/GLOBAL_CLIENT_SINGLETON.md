# 全局客户端单例模式重构

## 问题

之前每个 API 请求都会创建新的 `XiaoAiClient` 实例，导致：
1. 每次请求都重新登录小米账号
2. 日志中充满重复的登录信息
3. 性能浪费和不必要的网络请求
4. 可能触发小米的频率限制

## 解决方案

使用全局单例模式，在应用启动时创建一个 `XiaoAiClient` 实例，所有请求共享这个实例。

### 实现方式

1. **创建依赖注入模块** (`backend/src/xiaoai_media/api/dependencies.py`)
   - 维护全局客户端实例
   - 提供 `get_client()` 用于 FastAPI 依赖注入
   - 提供 `get_client_sync()` 用于服务类

2. **应用启动时初始化** (`backend/src/xiaoai_media/api/main.py`)
   ```python
   @app.on_event("startup")
   async def startup_event():
       client = XiaoAiClient()
       await client.connect()  # 只登录一次
       set_global_client(client)
   ```

3. **路由使用依赖注入**
   ```python
   @router.get("")
   async def list_devices(client: XiaoAiClient = Depends(get_client)):
       devices = await client.list_devices()
       return {"devices": devices}
   ```

4. **服务类使用同步获取**
   ```python
   async def _poll_conversations(self):
       client = get_client_sync()
       devices = await client.list_devices()
   ```

## 已更新的文件

### API 路由
- ✅ `backend/src/xiaoai_media/api/routes/devices.py`
- ✅ `backend/src/xiaoai_media/api/routes/tts.py`
- ✅ `backend/src/xiaoai_media/api/routes/volume.py`
- ✅ `backend/src/xiaoai_media/api/routes/command.py`

### 后台服务
- ✅ `backend/src/xiaoai_media/conversation.py`
- ⏳ `backend/src/xiaoai_media/playback_monitor.py` (待更新)
- ⏳ `backend/src/xiaoai_media/command_handler.py` (待更新)
- ⏳ `backend/src/xiaoai_media/player.py` (待更新)
- ⏳ `backend/src/xiaoai_media/services/voice_command_service.py` (待更新)
- ⏳ `backend/src/xiaoai_media/services/playlist_service.py` (待更新)

## 效果

### 之前
```
2026-03-22 18:52:13 INFO — MiService: using password auth for user xxx
2026-03-22 18:52:13 INFO — MiService: testing authentication...
2026-03-22 18:52:13 INFO — MiService: MiNA authentication successful
2026-03-22 18:52:13 INFO — MiService: MiIO authentication successful
INFO: 127.0.0.1:56780 - "GET /api/config HTTP/1.1" 200 OK
2026-03-22 18:52:14 INFO — MiService: using password auth for user xxx  # 又登录了！
2026-03-22 18:52:14 INFO — MiService: testing authentication...
2026-03-22 18:52:14 INFO — MiService: MiNA authentication successful
2026-03-22 18:52:14 INFO — MiService: MiIO authentication successful
INFO: 127.0.0.1:56781 - "GET /api/devices HTTP/1.1" 200 OK
```

### 之后
```
2026-03-22 19:00:00 INFO — MiService: using password auth for user xxx
2026-03-22 19:00:00 INFO — MiService: testing authentication...
2026-03-22 19:00:00 INFO — MiService: MiNA authentication successful
2026-03-22 19:00:00 INFO — MiService: MiIO authentication successful
2026-03-22 19:00:00 INFO — XiaoAiClient 已初始化
2026-03-22 19:00:00 INFO — 应用启动完成
INFO: 127.0.0.1:56780 - "GET /api/config HTTP/1.1" 200 OK  # 不再登录
INFO: 127.0-0.1:56781 - "GET /api/devices HTTP/1.1" 200 OK  # 不再登录
```

## 优点

1. **性能提升**：避免重复登录，减少网络请求
2. **日志清晰**：只在启动时登录一次
3. **Token 复用**：`.mi.token` 文件被有效利用
4. **避免限流**：减少对小米服务器的请求频率
5. **连接复用**：HTTP 连接可以被复用

## 注意事项

1. **Token 过期处理**：`miservice` 库会自动检测 401 错误并重新登录
2. **线程安全**：Python 的 asyncio 是单线程的，不需要额外的锁
3. **应用重启**：重启应用会重新登录，但这是正常的

## 待完成

还有一些服务类文件需要更新，但核心 API 路由已经完成。这些服务类的更新可以逐步进行，不影响主要功能。

## 测试

重启服务后，观察日志：
- 应该只在启动时看到一次登录日志
- 后续 API 请求不应该再有登录日志
- 功能应该正常工作
