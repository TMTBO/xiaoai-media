# Docker Hub CI 配置指南

## 概述

项目配置了自动构建并推送 Docker 镜像到 Docker Hub 的 GitHub Actions workflow。

## 安全说明

**重要**：workflow 文件中使用 `${{ secrets.XXX }}` 是完全安全的：

- ✅ Secrets 存储在 GitHub 加密数据库中，不在代码仓库
- ✅ GitHub Actions 自动屏蔽日志中的 secrets 值（显示为 `***`）
- ✅ 只有仓库管理员可以添加/修改 secrets
- ✅ Secrets 不会出现在 pull request 或 fork 中
- ✅ 这是 GitHub 官方推荐的标准做法

workflow 文件可以安全地提交到公开仓库，不会泄漏任何凭证。

## 配置步骤

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

编辑 `.github/workflows/docker-hub.yml` 文件，修改环境变量：

```yaml
env:
  DOCKER_HUB_IMAGE: your-dockerhub-username/xiaoai-media
```

将 `your-dockerhub-username` 替换为你的 Docker Hub 用户名。

## 触发条件

CI 会在以下情况自动触发：

- 推送到 `master` 分支
- 创建版本标签（如 `v1.0.0`）
- 手动触发（workflow_dispatch）

## 镜像标签规则

- `master` 分支推送 → `latest` 和 `master` 标签
- 版本标签 `v1.2.3` → `1.2.3`, `1.2`, `1`, `latest` 标签

## 支持的平台

- linux/amd64
- linux/arm64

## 手动触发构建

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Build and Push to Docker Hub" workflow
3. 点击 "Run workflow" 按钮

## 使用镜像

构建完成后，可以通过以下命令拉取镜像：

```bash
# 拉取最新版本
docker pull your-dockerhub-username/xiaoai-media:latest

# 拉取特定版本
docker pull your-dockerhub-username/xiaoai-media:1.0.0
```

## 故障排查

### 构建失败

1. 检查 GitHub Secrets 是否正确配置
2. 确认 Docker Hub token 有效且权限正确
3. 查看 Actions 日志获取详细错误信息

### 推送失败

1. 确认 Docker Hub 仓库存在（首次推送会自动创建）
2. 检查 token 权限是否包含写入权限
3. 确认用户名和镜像名称拼写正确
