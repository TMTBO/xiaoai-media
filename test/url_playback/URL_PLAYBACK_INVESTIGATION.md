# 小爱音箱URL播放调查报告

## 问题描述
虽然可以通过音乐API获取到歌曲的播放URL，但小爱音箱无法直接播放这些URL。

## 测试结果

### 测试的方法
1. `player_play_url` with `type=1` - 返回 True，但音箱无播放
2. `player_play_url` without type - 返回 True，但音箱无播放  
3. `player_play_music` - 返回 True，但音箱无播放
4. `player_play_operation` - 返回 True，但音箱无播放

### 结论
所有 ubus 方法都返回成功（True），但实际上音箱并没有播放音频。这表明：
- API调用本身是成功的
- 但小爱音箱可能不支持直接播放外部HTTP URL
- 或者需要特定格式的URL/协议

## 为什么不能直接播放URL？

### 可能的原因

1. **网络限制**
   - 小爱音箱可能只能访问小米白名单内的域名
   - 第三方音乐URL可能被防火墙阻止

2. **协议限制**
   - 可能只支持特定的流媒体协议（如DLNA、AirPlay）
   - HTTP直链可能不被支持

3. **DRM/版权保护**
   - 小米可能限制了直接URL播放以保护版权
   - 强制通过语音命令使用官方音乐源

4. **URL格式要求**
   - 可能需要特定的URL格式或参数
   - 可能需要本地网络内的URL

## xiaomusic 的解决方案

xiaomusic 项目通过以下方式解决：
1. 在本地运行HTTP服务器
2. 将音乐文件通过本地服务器提供
3. 小爱音箱访问本地网络内的URL
4. 这样可以绕过外部URL的限制

参考：https://github.com/hanxi/xiaomusic

## 当前实现方案

由于直接URL播放不可行，我们采用**语音命令方式**：

```python
# 不使用URL播放
# result = await client.play_url(url, device_id)  # 不工作

# 使用语音命令
command = f"播放{singer}的{song_name}"
result = await client.send_command(command, device_id)  # 工作正常
```

### 优点
- ✓ 可靠工作
- ✓ 使用小爱的官方音乐源
- ✓ 支持所有小爱支持的音乐平台

### 缺点
- ✗ 不能播放指定的URL
- ✗ 依赖小爱的搜索结果
- ✗ 可能播放的不是完全相同的版本

## 未来改进方向

如果要实现真正的URL播放，需要：

1. **本地代理服务器**
   - 在后端添加HTTP音频代理
   - 将外部URL转换为本地URL
   - 小爱访问本地代理获取音频

2. **DLNA支持**
   - 实现DLNA协议
   - 将音频推送到小爱音箱
   - 需要研究小爱的DLNA兼容性

3. **研究官方API**
   - 查找小米官方文档
   - 寻找正确的URL播放方法
   - 可能需要特殊的认证或格式

## 参考资料

- [xiaomusic - 使用小爱音箱播放本地音乐](https://github.com/hanxi/xiaomusic)
- [MiService - 小米云服务Python库](https://github.com/Yonsm/MiService)
- [python-miio - 小米设备控制库](https://github.com/rytilahti/python-miio)
