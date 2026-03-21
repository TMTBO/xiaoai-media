# 清理检查清单

HOME 目录迁移后的文件检查清单。

---

## ✅ 已完成的清理

### 代码文件

- [x] **backend/src/xiaoai_media/config.py**
  - `get_data_dir()` 改为直接返回 `Path.home()`
  - 移除 `.xiaoai-media` 子目录逻辑

### Docker 文件

- [x] **Dockerfile**
  - 移除 `/data/.xiaoai-media` 目录创建
  - 改为创建 `/data` 目录
  - VOLUME 从 `/data/.xiaoai-media` 改为 `/data`

- [x] **docker-compose.yml**
  - 挂载点从 `./data:/data/.xiaoai-media` 改为 `./data:/data`
  - 使用预构建镜像 `ghcr.io/tmtbo/xiaoai-media:latest`

- [x] **docker-entrypoint.sh**
  - 权限检查从 `/data/.xiaoai-media` 改为 `/data`

### 配置文件

- [x] **.gitignore**
  - 移除 `.xiaoai-media/`
  - 添加 `playlists/`、`conversation.db`、`*.db`

- [x] **Makefile**
  - 添加 `HOME=.` 环境变量到开发命令

- [x] **user_config_template.py**
  - 更新注释说明

### 测试文件

- [x] **test/config/test_data_dir.py**
  - 更新测试逻辑，检查 `Path.home()` 而非 `.xiaoai-media`
  - 移除旧的优先级测试

### 文档文件

- [x] **README.md**
  - 更新数据存储说明
  - 添加 Docker 镜像信息
  - 更新 GitHub 链接

- [x] **QUICK_START.md**
  - 更新开发和 Docker 部署说明
  - 添加镜像信息

- [x] **docs/README.md**
  - 更新文档中心
  - 更新 GitHub 链接

- [x] **docs/INDEX.md**
  - 更新文档索引
  - 更新 GitHub 链接

- [x] **docs/STRUCTURE.md**
  - 更新项目结构说明

- [x] **docs/config/README.md**
  - 重写配置指南
  - 更新数据目录说明

- [x] **docs/config/DEV_ENVIRONMENT.md**
  - 更新开发环境配置
  - 移除 `.xiaoai-media` 引用

- [x] **docs/config/DATA_STORAGE.md**
  - 完全重写数据存储说明
  - 使用 HOME 目录概念

- [x] **docs/deployment/DOCKER_GUIDE.md**
  - 重写 Docker 部署指南
  - 添加预构建镜像说明
  - 更新挂载点说明

- [x] **docs/deployment/DOCKER_QUICK_START.md**
  - 重写快速开始指南
  - 添加镜像信息

- [x] **docs/migration/README.md**
  - 创建迁移总览
  - 更新 GitHub 链接

- [x] **docs/migration/HOME_DIR_MIGRATION.md**
  - 创建 HOME 目录迁移指南
  - 说明从 `.xiaoai-media` 迁移的步骤

- [x] **docs/CONTRIBUTING.md**
  - 更新贡献指南
  - 更新 GitHub 链接

- [x] **docs/DOCUMENTATION_STATUS.md**
  - 创建文档状态追踪
  - 更新 GitHub 链接

### 脚本文件

- [x] **scripts/diagnose_docker_storage.sh**
  - 更新诊断脚本
  - 从 `/data/.xiaoai-media` 改为 `/data`

---

## 📋 保留的 `.xiaoai-media` 引用

以下文件中的 `.xiaoai-media` 引用是**正常的**，因为它们是在说明历史版本或迁移过程：

### 迁移文档（正常）

- **docs/migration/HOME_DIR_MIGRATION.md**
  - ✅ 说明变更前的目录结构
  - ✅ 说明如何从旧版本迁移
  - ✅ 提供回滚方案

- **docs/migration/README.md**
  - ✅ 版本兼容性表格
  - ✅ 历史版本说明

---

## 🔍 验证清单

### 代码验证

```bash
# 1. 搜索代码中的 .xiaoai-media
grep -r "\.xiaoai-media" backend/ --exclude-dir=__pycache__

# 2. 运行测试
HOME=. python test/config/test_data_dir.py

# 3. 检查配置加载
HOME=. python -c "from xiaoai_media.config import get_data_dir; print(get_data_dir())"
```

### Docker 验证

```bash
# 1. 构建镜像
docker build -t xiaoai-media-test .

# 2. 检查镜像
docker run --rm xiaoai-media-test ls -la /data

# 3. 检查 VOLUME
docker inspect xiaoai-media-test | grep -A 5 Volumes
```

### 文档验证

```bash
# 1. 搜索文档中的 .xiaoai-media（排除迁移文档）
grep -r "\.xiaoai-media" docs/ --exclude-dir=migration | grep -v "变更前" | grep -v "旧版本"

# 2. 检查链接有效性
# 手动检查所有 GitHub 链接是否正确
```

---

## 📊 统计信息

### 修改的文件数量

- 代码文件：2 个
- Docker 文件：3 个
- 配置文件：3 个
- 测试文件：1 个
- 文档文件：15+ 个
- 脚本文件：1 个

### 删除的文件数量

- 过时文档：20+ 个

### 新建的文件数量

- 核心文档：6 个
- 迁移文档：2 个

---

## ✅ 最终确认

- [x] 所有代码文件已更新
- [x] 所有 Docker 文件已更新
- [x] 所有配置文件已更新
- [x] 所有测试文件已更新
- [x] 所有文档已更新或重写
- [x] 所有脚本已更新
- [x] GitHub 链接已更新
- [x] Docker 镜像信息已添加
- [x] 迁移指南已创建
- [x] 测试通过

---

## 🎯 下一步

1. 运行完整测试套件
2. 构建并测试 Docker 镜像
3. 更新 CHANGELOG.md
4. 创建 Git tag
5. 推送到 GitHub
6. 触发 CI/CD 构建镜像
