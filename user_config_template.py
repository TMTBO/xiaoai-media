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
# 播单管理配置
# ============================================

# 播单数据存储目录
# 开发环境：HOME=. 设置后，数据存储在项目根目录
# Docker 环境：HOME=/data，数据存储在 /data 目录（挂载卷）
# 注意：播单数据会自动存储在 $HOME/playlists/ 目录中，无需单独配置


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
    
    此函数支持异步并发调用，可以同时处理多个音频 URL 获取请求。
    用于播单管理功能，当播单项没有 URL 时，会调用此函数获取 URL。

    Args:
        custom_params: 自定义参数字典，包含音频相关信息
            通用字段（来自 PlaylistItem）：
            - title: 歌曲名/标题
            - artist: 艺术家/歌手
            - album: 专辑名
            - audio_id: 音频ID
            - interval: 播放间隔（秒）或时长
            - pic_url: 封面图片URL
            
            音乐类型特定字段（来自 custom_params）：
            - type: 类型（music, audiobook, podcast 等）
            - platform: 平台（tx, wy, kg 等）
            - id/song_id: 歌曲ID
            - name: 歌曲名称（可能与 title 重复）
            - singer: 歌手名称（可能与 artist 重复）
            - qualities: 音质列表
            - meta: 元数据

    Returns:
        播放 URL（原始 URL，不需要包装为代理 URL，系统会自动处理）

    Raises:
        ValueError: 不支持的音频类型或获取 URL 失败

    示例实现：
        >>> await get_audio_url({"type": "music", "platform": "tx", "id": "001ABC"})
        'https://music.qq.com/song/001ABC.mp3'
    """
    audio_type = custom_params.get("type", "")

    if audio_type == "music":
        # 音乐类型：调用专门的音乐 URL 获取函数
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
        # 默认：返回空字符串或抛出异常
        raise ValueError(f"Unsupported audio type: {audio_type}")

