"""
用户配置模板文件

将此文件复制为 user_config.py 并根据需要修改配置。

参考: xiaomusic 的配置方式

使用方式：
1. 复制此文件：cp user_config_template.py user_config.py
2. 修改配置项
3. 启动服务：make dev
"""

# ============================================
# 小米账号配置
# ============================================

# 小米账号
MI_USER = "your_xiaomi_account@example.com"

# 小米密码
MI_PASS = "your_password"

# 小米密码令牌（可选，如果已有 token 可直接使用）
MI_PASS_TOKEN = ""

# 设备 ID 或设备名称（选填，不填则自动使用第一个设备）
# 可通过 make list-devices 查看设备列表
MI_DID = ""

# 区域（选填，默认 cn）
# 可选值: cn, de, i2, ru, sg, us
MI_REGION = "cn"


# ============================================
# 音乐服务配置
# ============================================

# 音乐搜索服务地址
# 指向本地 music_download 服务
# ⚠️ 重要：如果音箱播放失败，请将 localhost 改为本机局域网IP
# 例如：MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
MUSIC_API_BASE_URL = "http://localhost:5050"

# 默认音乐平台
# 可选值: tx（腾讯）, kw（酷我）, kg（酷狗）, wy（网易云）, mg（咪咕）
MUSIC_DEFAULT_PLATFORM = "tx"


# ============================================
# 本服务配置
# ============================================

# 本服务的基础 URL，用于生成代理链接
# ⚠️ 重要：必须使用音箱可访问的局域网 IP，不能使用 localhost
# 例如：SERVER_BASE_URL = "http://192.168.1.100:8000"
SERVER_BASE_URL = "http://localhost:8000"


# ============================================
# 对话监听配置
# ============================================

# 启用对话监听
# 设置为 True 时，会持续监听音箱的对话记录，自动拦截播放指令并调用本服务获取音乐 URL
ENABLE_CONVERSATION_POLLING = True

# 对话轮询间隔（秒）
CONVERSATION_POLL_INTERVAL = 2.0


# ============================================
# 唤醒词配置
# ============================================

# 唤醒词列表
# 只有包含这些唤醒词的指令才会被处理
# 如果为空列表，则处理所有指令
WAKE_WORDS = [
    "小爱同学",
    "小爱",
]

# 是否启用唤醒词过滤
# 如果为 False，则忽略 WAKE_WORDS 配置，处理所有指令
ENABLE_WAKE_WORD_FILTER = True


# ============================================
# 自定义指令处理函数（高级功能）
# ============================================


def should_handle_command(query: str) -> bool:
    """
    判断是否应该处理该指令

    Args:
        query: 用户的语音指令文本

    Returns:
        True 表示应该处理，False 表示忽略

    示例:
        def should_handle_command(query: str) -> bool:
            # 只处理包含"播放"的指令
            return "播放" in query
    """
    # 默认实现：检查唤醒词
    if not ENABLE_WAKE_WORD_FILTER:
        return True

    if not WAKE_WORDS:
        return True

    # 检查是否包含任何唤醒词
    for wake_word in WAKE_WORDS:
        if wake_word in query:
            return True

    return False


def preprocess_command(query: str) -> str:
    """
    预处理指令文本

    在指令被解析之前调用，可以用于：
    - 移除唤醒词
    - 标准化文本
    - 替换同义词

    Args:
        query: 原始指令文本

    Returns:
        处理后的指令文本

    示例:
        def preprocess_command(query: str) -> str:
            # 移除唤醒词
            for wake_word in WAKE_WORDS:
                query = query.replace(wake_word, "")
            return query.strip()
    """
    # 默认实现：移除唤醒词
    processed = query
    for wake_word in WAKE_WORDS:
        processed = processed.replace(wake_word, "")

    return processed.strip()


# ============================================
# 日志配置
# ============================================

# 日志级别
# 可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# 是否显示详细的播放日志
VERBOSE_PLAYBACK_LOG = False
