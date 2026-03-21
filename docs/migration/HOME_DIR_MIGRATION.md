# HOME 目录迁移说明

## 变更概述

从使用 `.xiaoai-media` 子目录改为直接使用 HOME 目录作为数据存储根目录。

### 变更前

```
开发环境：./.xiaoai-media/
Docker 环境：/data/.xiaoai-media/
```

### 变更后

```
开发环境：./（通过 HOME=. 设置）
Docker 环境：/data/（通过 HOME=/data 设置）
```

---

## 优势

1. **简化逻辑**：不需要额外的子目录层级
2. **统一路径**：所有环境都直接使用 `Path.home()`
3. **更灵活**：可以通过 HOME 环境变量轻松切换数据目录

---

## 迁移步骤

### 开发环境

如果你之前有 `.xiaoai-media` 目录：

```bash
# 移动数据文件到项目根目录
mv .xiaoai-media/user_config.py ./
mv .xiaoai-media/conversation.db ./
mv .xiaoai-media/playlists ./

# 删除旧目录
rm -rf .xiaoai-media
```

### Docker 环境

更新 docker-compose.yml 或运行命令：

**旧配置**：
```yaml
volumes:
  - ~/.xiaoai-media:/data/.xiaoai-media
```

**新配置**：
```yaml
volumes:
  - ./data:/data
```

**迁移数据**：
```bash
# 如果你之前使用 ~/.xiaoai-media
mkdir -p ./data
cp -r ~/.xiaoai-media/* ./data/
```

---

## 代码变更

### config.py

**变更前**：
```python
def get_data_dir() -> Path:
    # 检查项目根目录
    project_data_dir = Path(__file__).resolve().parents[3] / ".xiaoai-media"
    if project_data_dir.exists():
        return project_data_dir
    
    # 使用用户主目录
    return Path.home() / ".xiaoai-media"
```

**变更后**：
```python
def get_data_dir() -> Path:
    """直接使用 HOME 目录"""
    return Path.home()
```

### Makefile

**变更前**：
```makefile
backend:
	PYTHONPATH=backend/src $(UVICORN) xiaoai_media.api.main:app
```

**变更后**：
```makefile
backend:
	HOME=. PYTHONPATH=backend/src $(UVICORN) xiaoai_media.api.main:app
```

---

## 注意事项

1. **开发环境数据文件**：现在直接存储在项目根目录，已添加到 `.gitignore`
2. **Docker 挂载点**：从 `/data/.xiaoai-media` 改为 `/data`
3. **环境变量**：开发环境必须设置 `HOME=.`，Makefile 已自动配置

---

## 验证迁移

### 开发环境

```bash
# 启动服务
make dev

# 检查数据目录
ls -la user_config.py conversation.db playlists/
```

### Docker 环境

```bash
# 启动容器
docker-compose up -d

# 检查容器内数据目录
docker exec xiaoai-media ls -la /data/

# 运行诊断脚本
bash scripts/diagnose_docker_storage.sh
```

---

## 回滚方案

如果需要回滚到旧版本：

```bash
# 开发环境
mkdir -p .xiaoai-media
mv user_config.py .xiaoai-media/
mv conversation.db .xiaoai-media/
mv playlists .xiaoai-media/

# Docker 环境
# 修改 docker-compose.yml 挂载点为：
# - ./data:/data/.xiaoai-media
```
