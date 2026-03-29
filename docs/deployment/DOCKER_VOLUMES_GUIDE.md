# Docker Volumes 挂载指南

## 问题描述

在 Docker 中运行时，批量导入功能无法列出挂载的 volumes 目录（如 `/data/audiobooks`）。

## 原因分析

1. **挂载配置未生效**: docker-compose.yml 中的 volumes 配置被注释或未正确配置
2. **容器未重启**: 修改 volumes 配置后需要重启容器才能生效
3. **权限问题**: 挂载的目录权限不正确，容器内的用户无法访问
4. **源目录不存在**: 宿主机上的源目录（如 `/mnt/NAS/audiobooks`）不存在

## 解决方案

### 1. 配置 docker-compose.yml

在 `docker-compose.yml` 中添加 volumes 挂载：

```yaml
services:
  xiaoai-media:
    volumes:
      - ./data:/data
      # 挂载 NAS 上的 audiobooks 目录
      - /mnt/NAS/audiobooks:/data/audiobooks
      # 可以挂载多个目录
      - /mnt/NAS/music:/data/music
      - /mnt/NAS/podcasts:/data/podcasts
```

### 2. 验证源目录存在

在宿主机上检查目录是否存在：

```bash
ls -la /mnt/NAS/audiobooks
```

如果目录不存在，需要先创建或挂载 NAS：

```bash
# 创建挂载点
sudo mkdir -p /mnt/NAS

# 挂载 NAS（示例，具体命令取决于你的 NAS 类型）
sudo mount -t nfs nas-server:/audiobooks /mnt/NAS/audiobooks
```

### 3. 检查目录权限

确保目录权限允许容器内的用户访问：

```bash
# 查看权限
ls -ld /mnt/NAS/audiobooks

# 如果需要，调整权限（谨慎操作）
sudo chmod 755 /mnt/NAS/audiobooks
```

### 4. 重启容器

修改配置后必须重启容器：

```bash
# 停止并删除容器
docker-compose down

# 重新创建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 5. 验证挂载

进入容器检查挂载是否成功：

```bash
# 进入容器
docker-compose exec xiaoai-media bash

# 检查目录
ls -la /data/
ls -la /data/audiobooks/

# 运行调试脚本
python debug_volumes.py
```

## 调试工具

项目根目录下的 `debug_volumes.py` 脚本可以帮助诊断挂载问题：

```bash
# 在容器内运行
docker-compose exec xiaoai-media python debug_volumes.py
```

该脚本会检查：
- 当前用户和权限
- /data 目录结构
- 挂载点识别
- 子目录访问权限
- 音频文件搜索

## 常见问题

### Q1: 挂载后看不到文件

**可能原因**:
- 容器未重启
- 源目录为空
- 权限不足

**解决方法**:
```bash
# 重启容器
docker-compose restart

# 检查源目录
ls -la /mnt/NAS/audiobooks
```

### Q2: 权限被拒绝

**可能原因**:
- 目录权限过于严格
- SELinux 或 AppArmor 限制

**解决方法**:
```bash
# 调整权限
sudo chmod -R 755 /mnt/NAS/audiobooks

# 如果使用 SELinux
sudo chcon -Rt svirt_sandbox_file_t /mnt/NAS/audiobooks
```

### Q3: NAS 挂载在容器启动后断开

**解决方法**:
使用 systemd 或 fstab 确保 NAS 在系统启动时自动挂载：

```bash
# 编辑 /etc/fstab
nas-server:/audiobooks /mnt/NAS/audiobooks nfs defaults 0 0
```

## 最佳实践

1. **使用绝对路径**: volumes 配置中使用绝对路径避免歧义
2. **只读挂载**: 如果不需要写入，使用只读挂载提高安全性
   ```yaml
   - /mnt/NAS/audiobooks:/data/audiobooks:ro
   ```
3. **统一挂载点**: 所有媒体目录都挂载到 `/data` 下，便于管理
4. **备份配置**: 保存 docker-compose.yml 的备份
5. **监控日志**: 定期检查容器日志，及时发现问题

## 代码改进

已对 `playlist_service.py` 进行改进：

1. 添加目录排序，确保显示顺序一致
2. 添加目录访问验证，过滤无法访问的目录
3. 改进错误日志，便于调试

## 相关文档

- [Docker 部署指南](DOCKER_GUIDE.md)
- [批量导入指南](../playlist/BATCH_IMPORT_GUIDE.md)
- [配置文件说明](../config/USER_CONFIG_GUIDE.md)
