# 路由顺序修复

## 问题描述

访问 `/api/playlists/directories` 时返回 404 错误：
```
GET http://localhost:5173/api/playlists/directories 404 (Not Found)
```

实际返回：
```json
{"detail":"Playlist not found: directories"}
```

## 问题原因

FastAPI 按照路由定义的顺序进行匹配。原来的路由顺序：

```python
@router.get("/{playlist_id}")        # 第51行 - 先定义
async def get_playlist(playlist_id: str):
    ...

@router.get("/directories")          # 第235行 - 后定义
async def list_directories():
    ...
```

当访问 `/api/playlists/directories` 时：
1. FastAPI 首先匹配到 `/{playlist_id}` 路由
2. 将 `directories` 当作 `playlist_id` 参数
3. 尝试查找名为 "directories" 的播单
4. 返回 "Playlist not found: directories"

## 解决方案

将 `/directories` 路由移到 `/{playlist_id}` 之前：

```python
@router.get("/directories")          # 现在在第51行 - 先定义
async def list_directories():
    ...

@router.get("/{playlist_id}")        # 现在在第71行 - 后定义
async def get_playlist(playlist_id: str):
    ...
```

## 修复步骤

1. ✅ 将 `/directories` 路由移到 `/{playlist_id}` 之前
2. ⏳ 重启后端服务

## 重启后端服务

### 开发环境

如果使用 `uvicorn` 直接运行：
```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
uvicorn xiaoai_media.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker环境

```bash
docker-compose restart
```

或者：
```bash
docker-compose down
docker-compose up -d
```

## 验证修复

重启后端服务后，测试端点：

```bash
# 测试 directories 端点
curl http://localhost:8000/api/playlists/directories

# 应该返回类似：
# {
#   "directories": [...],
#   "is_docker": false,
#   "message": "本地模式：请使用文件选择器"
# }
```

## FastAPI 路由匹配规则

### 规则说明

FastAPI 按照以下顺序匹配路由：
1. 精确匹配优先（如 `/directories`）
2. 路径参数匹配（如 `/{playlist_id}`）
3. 按定义顺序从上到下匹配

### 最佳实践

1. **具体路由在前，通用路由在后**
   ```python
   @router.get("/special")      # ✅ 先定义
   @router.get("/{id}")         # ✅ 后定义
   ```

2. **避免路由冲突**
   ```python
   # ❌ 错误示例
   @router.get("/{id}")         # 会匹配所有路径
   @router.get("/special")      # 永远不会被匹配到
   
   # ✅ 正确示例
   @router.get("/special")      # 先匹配具体路径
   @router.get("/{id}")         # 再匹配通用路径
   ```

3. **使用路径前缀区分**
   ```python
   @router.get("/meta/directories")  # 使用前缀避免冲突
   @router.get("/{playlist_id}")
   ```

## 相关路由

当前 playlist 路由的正确顺序：

```python
@router.get("")                          # 列出所有播单
@router.post("")                         # 创建播单
@router.get("/directories")              # 列出目录 ⭐ 必须在 /{playlist_id} 之前
@router.get("/{playlist_id}")            # 获取播单
@router.put("/{playlist_id}")            # 更新播单
@router.delete("/{playlist_id}")         # 删除播单
@router.post("/{playlist_id}/items")     # 添加项目
@router.delete("/{playlist_id}/items/{item_index}")  # 删除项目
@router.post("/{playlist_id}/play")      # 播放播单
@router.post("/play-by-voice")           # 语音播放 ⭐ 也在 /{playlist_id} 之前
@router.post("/{playlist_id}/continue")  # 继续播放
@router.post("/{playlist_id}/stop")      # 停止播放
@router.post("/{playlist_id}/play-mode") # 设置播放模式
@router.post("/{playlist_id}/next")      # 下一首
@router.post("/{playlist_id}/import")    # 批量导入
```

## 总结

- ✅ 问题已修复：路由顺序已调整
- ⏳ 需要重启后端服务使修复生效
- 📝 记住：具体路由要放在通用路由之前

重启后端服务后，批量导入功能应该可以正常工作了！
