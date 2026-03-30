# 测试文件说明

XiaoAI Media 后端测试套件。

---

## 📋 测试文件列表

### 播单功能测试

#### test_playlist_sorting.py
测试播放列表排序功能
- 自然排序算法
- 章节命名格式识别
- 排序性能

#### test_artist_album_extraction.py
测试艺术家和专辑信息提取
- 从文件名提取元数据
- 多种命名格式支持
- 正则表达式匹配

#### test_directory_sort.py
测试目录排序功能
- 目录自然排序
- 文件名排序
- 批量导入排序

### 定时任务测试

#### test_scheduler.py
测试定时任务调度器
- 任务创建和删除
- Cron 表达式解析
- 任务执行

#### test_command_scheduler.py
测试命令调度功能
- 命令任务创建
- 延迟执行
- 任务状态管理

### 配置和状态测试

#### test_config_reload.py
测试配置热重载功能
- 配置文件监听
- 自动重载
- 回调机制

#### test_sse_state.py
测试 SSE 状态推送
- 状态变化通知
- SSE 连接管理
- 实时推送

### 用户认证测试

#### test_user_auth.py
测试用户认证系统
- 用户登录
- JWT Token 生成和验证
- 权限控制

#### test_user_login_enabled.py
测试用户登录功能
- 登录接口
- 用户管理
- 认证中间件

---

## 🚀 运行测试

### 运行所有测试

```bash
cd backend
pytest tests/
```

### 运行单个测试文件

```bash
pytest tests/test_playlist_sorting.py
```

### 运行特定测试

```bash
pytest tests/test_playlist_sorting.py::test_natural_sort
```

### 显示详细输出

```bash
pytest tests/ -v
```

### 显示打印输出

```bash
pytest tests/ -s
```

---

## 📊 测试覆盖率

查看测试覆盖率：

```bash
pytest tests/ --cov=xiaoai_media --cov-report=html
```

然后打开 `htmlcov/index.html` 查看详细报告。

---

## 🔧 测试配置

测试使用独立的配置，不会影响生产数据：

- 测试数据库：内存 SQLite
- 测试配置：`tests/conftest.py`
- 测试数据：`tests/fixtures/`

---

## 📝 编写测试

### 测试文件命名

- 文件名：`test_*.py`
- 测试函数：`test_*`
- 测试类：`Test*`

### 示例测试

```python
import pytest
from xiaoai_media.services.playlist_service import PlaylistService

def test_create_playlist():
    """测试创建播放列表"""
    service = PlaylistService()
    playlist = service.create_playlist(
        name="测试播单",
        type="music"
    )
    assert playlist.name == "测试播单"
    assert playlist.type == "music"

@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await some_async_function()
    assert result is not None
```

---

## 🐛 调试测试

### 使用 pdb 调试

```python
def test_something():
    import pdb; pdb.set_trace()
    # 你的测试代码
```

### 只运行失败的测试

```bash
pytest tests/ --lf
```

### 在第一个失败时停止

```bash
pytest tests/ -x
```

---

## 📚 相关文档

- [项目结构](../../docs/STRUCTURE.md) - 代码结构说明
- [贡献指南](../../docs/CONTRIBUTING.md) - 如何贡献代码
- [API 文档](../../docs/api/README.md) - API 参考

---

**最后更新**: 2026-03-30
