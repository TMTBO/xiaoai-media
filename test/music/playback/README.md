# 播放功能测试

本目录包含播放功能的测试脚本和诊断工具。

## 🧪 测试文件

### 1. diagnose_playback.py
**诊断播放问题的工具**

**功能：**
- 检查配置是否正确（是否使用localhost）
- 测试音乐API连接
- 测试代理端点是否可用

**运行：**
```bash
python test/music/playback/diagnose_playback.py
```

**预期输出：**
```
✅ 配置检查
✅ 代理端点
```

### 2. test_proxy_function.py
**测试代理URL函数**

**功能：**
- 测试 `_make_proxy_url` 函数的正确性
- 验证URL转换格式
- 确保URL编码正确

**运行：**
```bash
python test/music/playback/test_proxy_function.py
```

**测试用例：**
- 腾讯音乐URL
- 网易云音乐URL
- 带参数的URL
- 特殊字符URL

### 3. test_proxy_playback.py
**测试代理播放功能**

**功能：**
- 测试通过代理URL播放音乐
- 验证停止和播放流程
- 检查播放结果

**运行：**
```bash
python test/music/playback/test_proxy_playback.py
```

**注意：** 需要修改脚本中的测试URL为实际的音乐URL。

## 🚀 快速开始

### 运行所有测试

```bash
# 1. 诊断配置和环境
python test/music/playback/diagnose_playback.py

# 2. 测试代理函数
python test/music/playback/test_proxy_function.py

# 3. 测试实际播放（可选）
python test/music/playback/test_proxy_playback.py
```

### 预期结果

**diagnose_playback.py:**
```
============================================================
配置检查
============================================================
音乐API地址: http://10.184.62.160:5050
✅ 使用了局域网IP地址

============================================================
代理端点测试
============================================================
✅ 代理端点工作正常

============================================================
诊断总结
============================================================
✅ 配置检查
✅ 代理端点
```

**test_proxy_function.py:**
```
============================================================
测试代理URL函数
============================================================
配置的音乐API地址: http://10.184.62.160:5050

测试用例：
1. 原始URL: https://music.qq.com/song.mp3
   代理URL: http://10.184.62.160:5050/main/proxy?url=https%3A//music.qq.com/song.mp3
   ✅ 格式正确

============================================================
所有测试通过！
============================================================
```

## 🔍 测试场景

### 场景1：配置检查
验证 `.env` 配置是否正确：
- 是否使用localhost（应该使用局域网IP）
- 音乐API地址是否可访问

### 场景2：代理功能
验证代理URL转换：
- URL编码是否正确
- 代理路径是否正确
- 特殊字符处理

### 场景3：实际播放
验证完整播放流程：
- 获取音乐URL
- 转换为代理URL
- 停止当前播放
- 播放新URL

## 🐛 故障排查

### 问题1：配置检查失败

**错误：**
```
⚠️ 警告: 使用了localhost地址
```

**解决：**
修改 `.env` 文件：
```env
MUSIC_API_BASE_URL=http://10.184.62.160:5050
```

### 问题2：代理端点不可用

**错误：**
```
❌ 无法访问代理端点
```

**解决：**
1. 检查 music_download 服务是否运行
2. 检查端口是否正确
3. 检查防火墙设置

### 问题3：URL转换错误

**错误：**
```
AssertionError: 代理URL格式不正确
```

**解决：**
1. 检查 `_make_proxy_url` 函数实现
2. 验证 `config.MUSIC_API_BASE_URL` 配置
3. 查看详细错误信息

## 📝 添加新测试

### 测试模板

```python
#!/usr/bin/env python3
"""测试描述"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from xiaoai_media.client import XiaoAiClient
from xiaoai_media import config


async def test_your_feature():
    """测试你的功能"""
    print("测试开始...")
    
    async with XiaoAiClient() as client:
        # 你的测试代码
        pass
    
    print("✅ 测试通过")


if __name__ == "__main__":
    asyncio.run(test_your_feature())
```

## 🔗 相关文档

- [播放功能文档](../../../docs/playback/) - 播放功能的详细文档
- [代理URL使用指南](../../../docs/playback/代理URL使用指南.md) - 如何使用代理
- [故障排查指南](../../../docs/playback/PLAYBACK_TROUBLESHOOTING.md) - 解决播放问题

## 💡 最佳实践

1. **运行诊断** - 在测试播放前先运行诊断工具
2. **检查日志** - 查看后端日志了解详细错误
3. **逐步测试** - 从简单到复杂逐步测试
4. **记录结果** - 记录测试结果便于问题排查

## 📊 测试覆盖

| 功能 | 测试文件 | 状态 |
|------|---------|------|
| 配置检查 | diagnose_playback.py | ✅ |
| 代理端点 | diagnose_playback.py | ✅ |
| URL转换 | test_proxy_function.py | ✅ |
| 实际播放 | test_proxy_playback.py | ⚠️ 需要实际URL |

## 🚧 待完善

- [ ] 添加更多URL格式测试
- [ ] 添加错误处理测试
- [ ] 添加性能测试
- [ ] 添加集成测试
