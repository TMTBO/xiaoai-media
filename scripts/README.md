# 脚本工具

本目录包含用于管理和维护 XiaoAI Media 的实用脚本。

## 播单管理脚本

### migrate_playlists.py

将旧的单文件播单格式迁移到新的多文件格式。

**使用场景：**
- 从旧版本升级到 v1.0+
- 已有 `playlists.json` 文件需要迁移

**使用方法：**
```bash
python scripts/migrate_playlists.py
```

**功能：**
1. 读取旧的 `playlists.json` 文件
2. 创建新的 `playlists/` 目录
3. 生成索引文件 `playlists/index.json`
4. 为每个播单创建独立的数据文件
5. 备份旧文件为 `playlists.json.backup`

**注意事项：**
- 如果新目录已存在，脚本会跳过迁移
- 旧文件会被备份，不会丢失数据
- 建议在迁移前手动备份数据

### verify_playlist_storage.py

验证播单存储结构是否正常。

**使用场景：**
- 迁移后验证数据完整性
- 排查播单相关问题
- 检查数据结构是否正确

**使用方法：**
```bash
python scripts/verify_playlist_storage.py
```

**检查内容：**
1. 播单目录是否存在
2. 索引文件是否存在且格式正确
3. 每个播单的数据文件是否存在
4. 数据结构是否符合要求
5. 项目数是否匹配
6. 是否有旧字段需要清理

**输出示例：**
```
INFO: 数据目录: /home/user
INFO: 播单目录: /home/user/playlists
INFO: ✓ 播单目录存在
INFO: ✓ 索引文件存在
INFO: ✓ 索引文件格式正确
INFO: 播单数量: 2

INFO: 播单: 我的音乐
INFO:   ID: music_1234567890
INFO:   类型: music
INFO:   项目数: 10
INFO:   语音关键词: 音乐, 歌单
INFO:   ✓ 数据文件存在
INFO:   ✓ 数据文件格式正确
INFO:   实际项目数: 10
INFO:   ✓ 数据结构正确
```

## Docker 相关脚本

### diagnose_docker_storage.sh

诊断 Docker 环境中的存储问题。

**使用方法：**
```bash
bash scripts/diagnose_docker_storage.sh
```

### verify_config.sh

验证配置文件是否正确。

**使用方法：**
```bash
bash scripts/verify_config.sh
```

## 开发建议

### 添加新脚本

1. 在 `scripts/` 目录创建脚本文件
2. 添加 shebang 行（Python: `#!/usr/bin/env python3`, Bash: `#!/bin/bash`）
3. 添加文档字符串说明脚本用途
4. 添加可执行权限：`chmod +x scripts/your_script.py`
5. 更新本 README 文档

### 脚本规范

- Python 脚本使用 `#!/usr/bin/env python3`
- Bash 脚本使用 `#!/bin/bash`
- 添加详细的日志输出
- 处理错误情况
- 提供清晰的使用说明

## 相关文档

- [播单存储结构重构](../docs/playlist/PLAYLIST_STORAGE_REFACTOR.md)
- [配置指南](../docs/config/USER_CONFIG_GUIDE.md)
- [Docker 部署指南](../docs/deployment/DOCKER_GUIDE.md)
