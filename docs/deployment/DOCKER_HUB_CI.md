# Docker Hub CI 配置指南

## 概述

项目的 GitHub Actions workflow (`.github/workflows/docker-publish.yml`) 会自动构建并推送 Docker 镜像到：
- GitHub Container Registry (GHCR) - 默认启用
- Docker Hub - 可选，配置 secrets 后自动启用

## 配置 Docker Hub 推送（可选）

### 1. 创建 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 进入 Account Settings → Security → New Access Token
3. 创建一个新的 access token，权限选择 "Read, Write, Delete"
4. 保存生成的 token（只显示一次，无法再次查看）

### 2. 配置 GitHub Secrets

在 GitHub 仓库中添加以下 secrets：

1. 进入仓库的 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下两个 secrets：
   - Name: `DOCKERHUB_USERNAME`，Value: 你的 Docker Hub 用户名
   - Name: `DOCKERHUB_TOKEN`，Value: 刚才创建的 access token

**注意**：添加后，secrets 的值将被加密存储，你自己也无法再查看原始值

### 3. 修改镜像名称

编辑 `.github/workflows/docker-publish.yml` 文件，修改环境变量：

```yaml
env:
  GHCR_REGISTRY: ghcr.io
  GHCR_IMAGE: ${{ github.repository }}
  DOCKERHUB_IMAGE: your-dockerhub-username/xiaoai-media  # 修改这里
```

将 `your-dockerhub-username` 替换为你的 Docker Hub 用户名。

## 触发条件

CI 会在以下情况自动触发：

- 推送到 `master` 分支
- 推送到 `feature/**` 分支
- 创建版本标签（如 `v1.0.0`）

## 镜像推送目标

1. **GitHub Container Registry (GHCR)** - 始终推送
   - 镜像地址：`ghcr.io/<username>/<repo>`
   - 无需额外配置，使用 GitHub token 自动认证

2. **Docker Hub** - 可选推送
   - 镜像地址：配置的 `DOCKERHUB_IMAGE`
   - 需要配置 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` secrets
   - 如果未配置 secrets，会跳过 Docker Hub 推送

## 镜像标签规则

- `master` 分支推送 → `0.0.0-dev-<commit>` 标签
- `feature/**` 分支推送 → `<version>-beta<n>` 标签
- 版本标签 `v1.2.3` → `1.2.3`, `1.2`, `latest` 标签

## 支持的平台

- linux/amd64
- linux/arm64

## 使用镜像

构建完成后，可以从两个源拉取镜像：

```bash
# 从 GitHub Container Registry 拉取
docker pull ghcr.io/<username>/<repo>:latest

# 从 Docker Hub 拉取（如果已配置）
docker pull your-dockerhub-username/xiaoai-media:latest

# 拉取特定版本
docker pull ghcr.io/<username>/<repo>:1.0.0
```

## 故障排查

### Docker Hub 推送被跳过

如果 Docker Hub 推送被跳过，检查：
1. 确认已添加 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` secrets
2. Secrets 名称拼写正确（区分大小写）
3. 查看 Actions 日志确认是否检测到 secrets

### 构建失败

1. 检查 GitHub Secrets 是否正确配置
2. 确认 Docker Hub token 有效且权限正确
3. 查看 Actions 日志获取详细错误信息

### 推送失败

1. 确认 Docker Hub 仓库存在（首次推送会自动创建）
2. 检查 token 权限是否包含写入权限
3. 确认用户名和镜像名称拼写正确
4. 验证 token 未过期

## 安全说明

**重要**：workflow 文件中使用 `${{ secrets.XXX }}` 是完全安全的：

- ✅ Secrets 存储在 GitHub 加密数据库中，不在代码仓库
- ✅ GitHub Actions 自动屏蔽日志中的 secrets 值（显示为 `***`）
- ✅ 只有仓库管理员可以添加/修改 secrets
- ✅ Secrets 不会出现在 pull request 或 fork 中
- ✅ 这是 GitHub 官方推荐的标准做法

workflow 文件可以安全地提交到公开仓库，不会泄漏任何凭证。
