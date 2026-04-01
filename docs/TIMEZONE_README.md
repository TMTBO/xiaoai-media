# 时区配置文档

本目录包含时区配置相关的所有文档。

## 📚 文档列表

### 用户文档

1. **[TIMEZONE_CONFIG.md](TIMEZONE_CONFIG.md)** - 时区配置说明
   - 配置方式（前端界面 / 配置文件 / API）
   - 常用时区列表
   - 影响范围
   - 注意事项
   - 故障排查

### 技术文档

2. **[TIMEZONE_HOT_RELOAD.md](TIMEZONE_HOT_RELOAD.md)** - 时区热重载技术文档
   - 热重载机制详解
   - 使用示例
   - 技术细节
   - 限制和注意事项
   - 故障排查

### 开发文档

3. **[TIMEZONE_IMPLEMENTATION_SUMMARY.md](TIMEZONE_IMPLEMENTATION_SUMMARY.md)** - 实现总结
   - 完整的实现内容列表
   - 功能特点
   - 热重载机制
   - 使用方式
   - 验证方式
   - 相关文件清单

4. **[TIMEZONE_VERIFICATION_CHECKLIST.md](TIMEZONE_VERIFICATION_CHECKLIST.md)** - 验证清单
   - 配置文件检查
   - 代码检查
   - 功能验证
   - 测试覆盖

## 🚀 快速开始

### 通过前端界面配置（推荐）

1. 访问前端管理界面
2. 进入"配置管理"页面
3. 在"日志配置"部分找到"时区"选项
4. 选择时区并保存

详见：[TIMEZONE_CONFIG.md](TIMEZONE_CONFIG.md)

### 通过配置文件配置

在 `user_config.py` 中添加：

```python
# 时区配置（IANA 时区标识符）
TIMEZONE = "Asia/Shanghai"  # 北京时间
```

## ✨ 主要特性

- ✅ **统一配置**：时区配置集中在 `user_config.py` 中
- ✅ **前端界面**：提供友好的下拉选择器
- ✅ **热重载支持**：修改后立即生效，无需重启
- ✅ **全局生效**：影响日志时间戳和定时任务
- ✅ **标准兼容**：使用 IANA 时区标识符

## 📖 推荐阅读顺序

1. 用户：[TIMEZONE_CONFIG.md](TIMEZONE_CONFIG.md) → 开始使用
2. 开发者：[TIMEZONE_HOT_RELOAD.md](TIMEZONE_HOT_RELOAD.md) → 了解实现
3. 贡献者：[TIMEZONE_IMPLEMENTATION_SUMMARY.md](TIMEZONE_IMPLEMENTATION_SUMMARY.md) → 完整实现

## 🔗 相关链接

- [配置文档索引](INDEX.md)
- [用户配置指南](config/USER_CONFIG_GUIDE.md)
- [定时任务文档](scheduler/README.md)
