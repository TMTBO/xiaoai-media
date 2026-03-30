# 快速修复指南

## 问题

访问 `/api/playlists/directories` 返回 404 错误。

## 原因

路由顺序问题：`/directories` 被 `/{playlist_id}` 捕获了。

## 解决方案

✅ 代码已修复！现在只需要重启后端服务。

## 重启步骤

### 方式1：开发环境

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
cd backend
HOME=.. uvicorn xiaoai_media.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 方式2：Docker环境

```bash
docker-compose restart
```

## 验证

重启后测试：

```bash
curl http://localhost:8000/api/playlists/directories
```

应该返回：
```json
{
  "directories": [...],
  "is_docker": false,
  "message": "本地模式：请使用文件选择器"
}
```

## 完成

重启后，前端的批量导入功能应该可以正常工作了！

打开浏览器：
1. 进入播单管理
2. 选择播单 → 项目 → 批量导入
3. 应该能看到导入模式选择器
4. 可以正常使用批量导入功能

---

**详细说明请查看：** [ROUTE_ORDER_FIX.md](./ROUTE_ORDER_FIX.md)
