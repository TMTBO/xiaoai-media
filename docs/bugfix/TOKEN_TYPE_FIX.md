# Token 类型检查修复

## 问题描述

在使用 `token_store` 自动管理 token 后，`get_latest_ask` 方法报错：

```
ERROR xiaoai_media.client — No valid serviceToken or userId in MiAccount.token for conversation API.
```

但 API 实际上返回了 200 OK，说明功能正常。

## 根本原因

### Token 结构

miservice 在内存中使用 tuple 存储 token：

```python
# 内存中的结构
self.token[sid] = (resp["ssecurity"], serviceToken)
# 例如：
{
    "micoapi": ("ssecurity_value", "serviceToken_value")
}
```

### JSON 序列化问题

当 token 保存到 `.mi.token` 文件时，JSON 序列化会将 tuple 转换为 list：

```json
{
    "micoapi": ["ssecurity_value", "serviceToken_value"]
}
```

### 类型检查失败

原来的代码只检查 tuple：

```python
if (
    micoapi_data
    and isinstance(micoapi_data, tuple)  # ❌ 从文件加载后是 list
    and len(micoapi_data) >= 2
):
    service_token = micoapi_data[1]
```

从文件加载的 token 是 list，导致类型检查失败。

## 解决方案

修改类型检查，同时支持 tuple 和 list：

```python
if (
    micoapi_data
    and isinstance(micoapi_data, (tuple, list))  # ✅ 同时支持 tuple 和 list
    and len(micoapi_data) >= 2
):
    service_token = micoapi_data[1]
```

## 技术细节

### JSON 序列化行为

Python 的 `json.dump()` 会将 tuple 转换为 list：

```python
import json

data = {"key": ("value1", "value2")}
json_str = json.dumps(data)
print(json_str)  # {"key": ["value1", "value2"]}

loaded = json.loads(json_str)
print(type(loaded["key"]))  # <class 'list'>
```

### 为什么之前没有发现

1. **首次登录**：token 在内存中是 tuple，类型检查通过
2. **重启后**：从文件加载，token 变成 list，类型检查失败
3. **但功能正常**：因为 miservice 内部会重新登录并更新 token

### 影响范围

只影响 `get_latest_ask` 方法（获取对话记录）。其他功能不受影响，因为它们使用 miservice 的标准 API，不直接访问 token 结构。

## 修复验证

### 测试代码

```python
# 测试 tuple 和 list 的类型检查
micoapi_tuple = ("ssecurity", "serviceToken")
micoapi_list = ["ssecurity", "serviceToken"]

# 新的检查（同时支持 tuple 和 list）
assert isinstance(micoapi_tuple, (tuple, list))
assert isinstance(micoapi_list, (tuple, list))

# 提取 serviceToken
assert micoapi_tuple[1] == "serviceToken"
assert micoapi_list[1] == "serviceToken"
```

### 验证步骤

1. 删除 `.mi.token` 文件
2. 启动服务（首次登录，token 是 tuple）
3. 调用 `/api/command/conversation` API（应该成功）
4. 重启服务（从文件加载，token 是 list）
5. 再次调用 API（应该仍然成功，不再报错）

## 相关文件

- `backend/src/xiaoai_media/client.py` - 修复类型检查

## 相关问题

- Token 自动管理机制：`docs/migration/REMOVE_MI_PASS_TOKEN.md`
- MiIO 认证修复：`docs/migration/MIIO_AUTH_FIX.md`

## 总结

这是一个典型的 JSON 序列化类型转换问题。修复方法很简单，只需要在类型检查时同时支持 tuple 和 list。这个问题只在使用 `token_store` 自动管理 token 后才会出现，因为之前手动配置的 token 不涉及序列化。
