# 开发环境配置说明

## 数据目录设置

在开发环境中，通过设置 `HOME=.` 环境变量，使 `Path.home()` 指向项目根目录，从而实现开发和生产环境的统一配置逻辑。

### 目录结构

```
项目根目录/
├── user_config.py           # 用户配置文件
├── conversation.db          # 对话历史数据库
├── playlists/               # 播放列表数据
└── ...
```

### 环境对比

| 环境 | HOME 设置 | 数据目录路径 |
|------|-----------|-------------|
| 开发环境 | `HOME=.` | `./` |
| Docker 环境 | `HOME=/data` | `/data/` |

### 使用方式

开发环境已在 Makefile 中自动配置：

```bash
# 启动后端（自动设置 HOME=.）
make backend

# 启动前后端（自动设置 HOME=.）
make dev

# 列出设备（自动设置 HOME=.）
make list-devices
```

### 手动运行

如果需要手动运行 Python 脚本：

```bash
# 设置 HOME 环境变量
HOME=. PYTHONPATH=backend/src python your_script.py
```

### 优势

1. **统一逻辑**：开发和生产环境使用相同的代码路径
2. **环境隔离**：开发数据不会污染用户主目录
3. **简化代码**：无需在代码中检测和区分开发环境
4. **易于清理**：删除项目根目录的数据文件即可清理所有开发数据

### 初始化开发环境

```bash
# 复制配置文件模板
cp user_config_template.py user_config.py

# 编辑配置
vim user_config.py
```

### 注意事项

- 数据文件（`user_config.py`、`conversation.db`、`playlists/`）已添加到 `.gitignore`，不会被提交到版本控制
- 配置文件包含敏感信息（如账号密码），请勿分享或提交
