"""
用户配置示例文件

这是一个简化的配置示例，包含最常用的配置项。
完整的配置选项请查看 user_config_template.py

使用方法：
1. 复制此文件为 user_config.py
2. 修改配置项
3. 启动服务
"""

# ============================================
# 必填配置
# ============================================

# 小米账号
MI_USER = "your_account@example.com"

# 小米密码
MI_PASS = "your_password"


# ============================================
# 音乐服务配置
# ============================================

# 音乐搜索服务地址
# ⚠️ 重要：如果音箱播放失败，请将 localhost 改为本机局域网IP
# 例如：MUSIC_API_BASE_URL = "http://192.168.1.100:5050"
MUSIC_API_BASE_URL = "http://localhost:5050"

# 默认音乐平台：tx=腾讯, wy=网易云, kg=酷狗, kw=酷我, mg=咪咕
MUSIC_DEFAULT_PLATFORM = "tx"


# ============================================
# 本服务配置
# ============================================

# 本服务的基础 URL，用于生成代理链接
# ⚠️ 重要：必须使用音箱可访问的局域网 IP，不能使用 localhost
# 例如：SERVER_BASE_URL = "http://192.168.1.100:8000"
SERVER_BASE_URL = "http://localhost:8000"


# ============================================
# 唤醒词配置
# ============================================

# 唤醒词列表（只处理包含这些词的指令）
WAKE_WORDS = [
    "小爱同学",
    "小爱",
]

# 是否启用唤醒词过滤（False 则处理所有指令）
ENABLE_WAKE_WORD_FILTER = True


# ============================================
# 可选配置
# ============================================

# 设备 ID（不填则使用第一个设备）
MI_DID = ""

# 区域（默认 cn）
MI_REGION = "cn"

# 启用对话监听
ENABLE_CONVERSATION_POLLING = True

# 对话轮询间隔（秒）
CONVERSATION_POLL_INTERVAL = 2.0

# 启用播放监控（自动播放下一曲）
ENABLE_PLAYBACK_MONITOR = True

# 播放监控轮询间隔（秒）
PLAYBACK_MONITOR_INTERVAL = 3.0


# ============================================
# 音乐提供者模块导入
# ============================================

# 导入音乐 URL 提供者模块
# 注意：需要将 music_provider_template.py 复制为 music_provider.py
try:
    from music_provider import get_music_url
except ImportError as e:
    import sys
    from pathlib import Path
    raise ImportError(
        "无法导入 music_provider 模块。\n"
        f"请确保 music_provider.py 与 user_config.py 在同一目录下。\n"
        f"提示：将 music_provider_template.py 复制为 music_provider.py\n"
        f"当前目录：{Path(__file__).parent}\n"
        f"原始错误：{e}"
    ) from e


# ============================================
# 音频 URL 获取函数
# ============================================


async def get_audio_url(custom_params: dict) -> str:
    """
    根据音频信息获取播放 URL
    
    用于播单管理功能，当播单项没有 URL 时，会调用此函数获取 URL。

    Args:
        custom_params: 包含音频相关信息的字典

    Returns:
        播放 URL（原始 URL，系统会自动处理代理）

    Raises:
        ValueError: 不支持的音频类型或获取 URL 失败
    """
    audio_type = custom_params.get("type", "")

    if audio_type == "music":
        # 音乐类型：调用音乐 URL 获取函数
        return await get_music_url(custom_params, MUSIC_API_BASE_URL)

    elif audio_type == "audiobook":
        # 有声书类型：根据您的数据源实现
        book_id = custom_params.get("book_id", "")
        chapter = custom_params.get("chapter", "1")
        # TODO: 实现您的有声书 URL 获取逻辑
        return f"https://example.com/audiobook/{book_id}/{chapter}.mp3"

    elif audio_type == "podcast":
        # 播客类型：根据您的数据源实现
        podcast_id = custom_params.get("podcast_id", "")
        episode = custom_params.get("episode", "")
        # TODO: 实现您的播客 URL 获取逻辑
        return f"https://example.com/podcast/{podcast_id}/{episode}.mp3"

    else:
        raise ValueError(f"Unsupported audio type: {audio_type}")

