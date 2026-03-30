# 配置热重载 - 快速参考

## 问题

之前更新配置后需要手动重启服务才能生效。

## 解决方案

实现了配置热重载机制，配置更新后自动生效。

## 使用方法

### 通过 Web 界面

1. 登录管理后台
2. 进入"配置管理"页面
3. 修改配置项
4. 点击"保存"
5. ✅ 配置立即生效，无需重启！

### 通过 API

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "LOG_LEVEL": "DEBUG",
    "CONVERSATION_POLL_INTERVAL": 3.0
  }'
```

## 自动重启的服务

配置更新后，以下服务会自动重启并应用新配置：

- ✅ 对话监听器（轮询间隔更新）
- ✅ 播放监控器（监控间隔更新）
- ✅ 日志级别（立即生效）

## 开发模式注意事项

在开发模式下（`RELOAD=true`），系统会自动排除以下文件的监控：

- `user_config.py` - 由配置热重载处理
- `.xiaoai_media/*` - 数据目录
- `*.json` - 数据文件
- `.mi.token` - Token 文件

这样可以避免 uvicorn 的自动重载与配置热重载冲突。

## 验证配置是否生效

查看日志输出：

```
INFO - 配置已重新加载
INFO - 对话监听轮询间隔已更新: 3.0秒
INFO - 播放监控间隔已更新: 3.0秒
INFO - 日志级别已更新: DEBUG
INFO - 配置变更处理完成
```

## 常见问题

### Q: 配置更新后服务重启了？

A: 如果在开发模式下看到服务重启，请确保：
1. 使用最新版本的 `run.py`
2. `reload_excludes` 配置正确

### Q: 某些配置没有生效？

A: 检查日志是否有错误信息，确保：
1. 配置文件格式正确
2. 配置项名称正确
3. 配置值类型正确

### Q: 如何添加自定义配置热重载逻辑？

A: 在你的模块中注册回调函数：

```python
from xiaoai_media import config

def on_config_changed():
    # 你的配置更新逻辑
    pass

config.register_config_change_callback(on_config_changed)
```

## 更多信息

详细文档：[CONFIG_HOT_RELOAD.md](CONFIG_HOT_RELOAD.md)
