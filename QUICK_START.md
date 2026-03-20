# 快速开始

5 分钟快速启动 XiaoAi Media

## 1. 配置

```bash
# 复制配置模板
cp user_config_template.py user_config.py

# 编辑配置
vim user_config.py
```

最小配置：
```python
# user_config.py
MI_USER = "your_account@example.com"
MI_PASS = "your_password"
MUSIC_API_BASE_URL = "http://192.168.1.100:5050"  # 改为你的局域网IP
WAKE_WORDS = ["小爱同学", "小爱"]
```

## 2. 验证配置

```bash
make verify-config
```

## 3. 启动服务

```bash
make dev
```

访问：
- 前端：http://localhost:5173
- 后端：http://localhost:8000

## 常见问题

### Q: 配置文件在哪里？
A: 项目根目录的 `user_config.py`

### Q: 配置如何加载？
A: 使用 `make dev` 启动时会自动加载配置。

### Q: 音箱播放失败？
A: 将 `MUSIC_API_BASE_URL` 中的 `localhost` 改为本机局域网 IP。

## 完整文档

- [配置指南](docs/QUICK_CONFIG.md)
- [常见问题](docs/CONFIG_FAQ.md)
- [配置问题解答](docs/CONFIG_ANSWERS.md)
- [迁移指南](docs/migration/MIGRATION_TO_USER_CONFIG.md)
- [完整文档](docs/README.md)

## 命令速查

```bash
make install        # 安装依赖
make dev            # 启动前后端
make backend        # 只启动后端
make frontend       # 只启动前端
make test-config    # 测试配置
make verify-config  # 验证配置
make list-devices   # 查看设备列表
```
