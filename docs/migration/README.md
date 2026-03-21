# 迁移指南

版本升级和数据迁移说明。

---

## 最新迁移

### HOME 目录迁移（2026-03）

从使用 `.xiaoai-media` 子目录改为直接使用 HOME 目录。

**详见**：[HOME 目录迁移说明](HOME_DIR_MIGRATION.md)

**快速迁移**：

```bash
# 开发环境
mv .xiaoai-media/* ./
rm -rf .xiaoai-media

# Docker 环境
# 更新 docker-compose.yml
# volumes:
#   - ./data:/data  # 新配置
```

---

## 历史迁移

### 用户配置迁移

从环境变量配置改为 `user_config.py` 文件配置。

**详见**：[用户配置迁移](MIGRATION_TO_USER_CONFIG.md)

### miservice 依赖迁移

从 miservice 包迁移到内置实现。

**详见**：[miservice 迁移](MISERVICE_MIGRATION.md)

---

## 迁移文档索引

- [HOME_DIR_MIGRATION.md](HOME_DIR_MIGRATION.md) - HOME 目录迁移（最新）
- [MIGRATION_TO_USER_CONFIG.md](MIGRATION_TO_USER_CONFIG.md) - 用户配置迁移
- [MISERVICE_MIGRATION.md](MISERVICE_MIGRATION.md) - miservice 依赖迁移
- [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) - 迁移完成报告
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - 最终总结

---

## 版本兼容性

| 版本 | 配置方式 | 数据目录 | 兼容性 |
|------|---------|---------|--------|
| v1.0 | 环境变量 | `~/.xiaoai-media` | ❌ 已废弃 |
| v2.0 | user_config.py | `~/.xiaoai-media` | ⚠️ 需迁移 |
| v3.0 | user_config.py | `$HOME/` | ✅ 当前版本 |

---

## 需要帮助？

如果在迁移过程中遇到问题：

1. 查看具体的迁移文档
2. 检查 [配置 FAQ](../config/CONFIG_FAQ.md)
3. 提交 [Issue](https://github.com/tmtbo/xiaoai-media/issues)
