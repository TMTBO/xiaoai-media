# 测试文件

本目录包含 XiaoAI Media 的测试脚本和工具。

## 测试脚本

### test_auth.py

测试小米账号认证功能。

**使用场景：**
- 验证小米账号配置是否正确
- 测试设备连接
- 排查认证问题

**使用方法：**
```bash
python tests/test_auth.py
```

**功能：**
1. 连接小米账号
2. 获取设备列表
3. 显示设备信息
4. 验证认证状态

**输出示例：**
```
Testing Xiaomi account authentication...
============================================================
✓ Client connected successfully

Fetching device list...
✓ Found 2 device(s):
  1. 小米智能音箱 Pro (LX06) - 123456789
  2. 小爱音箱 (LX01) - 987654321

============================================================
✓ Authentication test completed
```

**故障排除：**
- 如果认证失败，检查 `user_config.py` 中的账号密码
- 确保网络连接正常
- 查看详细错误信息进行排查

## 单元测试

单元测试位于 `test/` 目录（注意是 `test` 不是 `tests`），按模块组织：

```
test/
├── command/          # 命令处理测试
├── config/           # 配置相关测试
├── conversation/     # 对话监听测试
├── music/            # 音乐功能测试
├── playback/         # 播放控制测试
├── playlist/         # 播单管理测试
├── tts/              # TTS功能测试
├── url_playback/     # URL播放测试
└── wake_word/        # 唤醒词测试
```

**运行单元测试：**
```bash
# 运行所有测试
pytest test/

# 运行特定模块测试
pytest test/playlist/

# 运行特定测试文件
pytest test/playlist/test_playlist_service.py
```

## 集成测试

### 批量导入测试

使用 `scripts/test_batch_import.sh` 进行批量导入功能的集成测试。

详见：[scripts/README.md](../scripts/README.md)

## 测试规范

### 添加新测试

1. **单元测试**：放在 `test/` 目录对应的模块子目录
2. **集成测试**：放在 `tests/` 目录
3. **测试脚本**：放在 `scripts/` 目录

### 命名规范

- 单元测试文件：`test_*.py`
- 集成测试文件：`test_*.py`
- 测试脚本：`test_*.sh` 或 `test_*.py`

### 测试编写建议

- 使用 pytest 框架
- 添加清晰的测试文档
- 包含正常和异常情况
- 使用 mock 隔离外部依赖
- 添加必要的断言

## 相关文档

- [开发环境配置](../docs/config/DEV_ENVIRONMENT.md)
- [API 测试指南](../docs/api/API_REFERENCE.md)
- [故障排除](../docs/playlist/troubleshooting/QUICK_FIX.md)

## 持续集成

项目使用 GitHub Actions 进行持续集成测试。

配置文件：`.github/workflows/test.yml`

**本地运行 CI 测试：**
```bash
# 安装依赖
make install

# 运行测试
make test

# 运行代码检查
make lint
```

## 测试覆盖率

查看测试覆盖率：
```bash
pytest --cov=backend/src/xiaoai_media test/
```

生成HTML报告：
```bash
pytest --cov=backend/src/xiaoai_media --cov-report=html test/
```

## 贡献指南

添加新功能时，请：
1. 编写对应的单元测试
2. 确保所有测试通过
3. 更新相关文档
4. 提交 Pull Request

---

**保持测试覆盖率，确保代码质量！** ✅
