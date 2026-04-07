"""配置服务层

处理配置文件的读取、写入和验证逻辑。
"""

from __future__ import annotations

import re

from fastapi import HTTPException

from xiaoai_media import config
from xiaoai_media.config import reload_config

# 允许通过API修改的配置项
ALLOWED_KEYS = {
    "MI_USER",
    "MI_PASS",
    "MI_DID",
    "MI_REGION",
    "MUSIC_API_BASE_URL",
    "MUSIC_DEFAULT_PLATFORM",
    "SERVER_BASE_URL",
    "ENABLE_CONVERSATION_POLLING",
    "CONVERSATION_POLL_INTERVAL",
    "ENABLE_WAKE_WORD_FILTER",
    "WAKE_WORDS",
    "LOG_LEVEL",
    "TIMEZONE",
    "PROXY_SKIP_AUTH_FOR_LAN",
    "PROXY_LAN_NETWORKS",
}


class ConfigService:
    """配置服务类，封装配置文件操作的业务逻辑"""

    @staticmethod
    def read_user_config() -> dict[str, str | bool | int | float]:
        """读取 user_config.py 中的配置变量

        Returns:
            配置字典，键为配置项名称，值为配置值
        """
        result: dict[str, str | bool | int | float] = {}
        config_path = config.get_config_file_path(required=False)
        if not config_path or not config_path.exists():
            return result

        content = config_path.read_text(encoding="utf-8")

        # 只匹配简单的变量赋值（不包含列表、字典等复杂类型）
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            # 匹配: VAR_NAME = "value" 或 VAR_NAME = 123 或 VAR_NAME = True
            match = re.match(r"^([A-Z_]+)\s*=\s*(.+)$", line)
            if match:
                key = match.group(1)
                val_str = match.group(2).strip()

                # 只处理允许的配置项
                if key not in ALLOWED_KEYS:
                    continue

                # 解析值（字符串、数字、布尔）
                if val_str.startswith('"') or val_str.startswith("'"):
                    # 字符串值
                    result[key] = val_str.strip('"').strip("'")
                elif val_str == "True":
                    result[key] = True
                elif val_str == "False":
                    result[key] = False
                elif val_str.replace(".", "", 1).isdigit():
                    # 数字
                    if "." in val_str:
                        result[key] = float(val_str)
                    else:
                        result[key] = int(val_str)
                else:
                    # 其他情况当作字符串
                    result[key] = val_str

        return result

    @staticmethod
    def write_user_config(data: dict[str, str | bool | int | float | list]) -> None:
        """更新 user_config.py 中的配置变量

        Args:
            data: 要更新的配置字典

        Raises:
            HTTPException: 当配置文件路径无法确定时
        """
        config_path = config.get_config_file_path(required=True)
        if not config_path:
            raise HTTPException(
                status_code=500, detail="Cannot determine config file path"
            )

        # 如果配置文件不存在，创建默认配置文件
        if not config_path.exists():
            # 确保数据目录存在
            data_dir = config.get_data_dir()
            data_dir.mkdir(parents=True, exist_ok=True)

            # 创建空配置文件
            config_path.write_text("# XiaoAi Media 配置文件\n\n", encoding="utf-8")

        content = config_path.read_text(encoding="utf-8")

        for key, val in data.items():
            # 格式化值
            if isinstance(val, bool):
                val_str = "True" if val else "False"
            elif isinstance(val, (int, float)):
                val_str = str(val)
            elif isinstance(val, list):
                # 列表类型：需要处理多行列表
                # 格式化为多行格式，保持美观
                if not val:
                    val_str = "[]"
                elif len(val) <= 2:
                    # 短列表用单行
                    formatted_items = ", ".join(f'"{item}"' for item in val)
                    val_str = f"[{formatted_items}]"
                else:
                    # 长列表用多行
                    formatted_items = ",\n    ".join(f'"{item}"' for item in val)
                    val_str = f"[\n    {formatted_items},\n]"

                # 查找列表的开始行和结束行
                lines = content.splitlines()
                new_lines = []
                skip_until_bracket = False
                found = False

                for i, line in enumerate(lines):
                    if skip_until_bracket:
                        # 跳过列表内容行，直到找到结束括号
                        if "]" in line:
                            skip_until_bracket = False
                        continue

                    if re.match(rf"^(\s*){key}\s*=\s*\[", line):
                        # 找到列表开始
                        found = True
                        # 添加格式化后的完整列表
                        indent = len(line) - len(line.lstrip())

                        if "\n" in val_str:
                            # 多行列表
                            formatted_lines = val_str.split("\n")
                            new_lines.append(
                                " " * indent + f"{key} = {formatted_lines[0]}"
                            )
                            for fl in formatted_lines[1:]:
                                new_lines.append(" " * indent + fl)
                        else:
                            # 单行列表
                            new_lines.append(" " * indent + f"{key} = {val_str}")

                        # 如果当前行没有结束括号，标记跳过后续行
                        if "]" not in line:
                            skip_until_bracket = True
                    else:
                        new_lines.append(line)

                if found:
                    content = "\n".join(new_lines)
                continue
            else:
                val_str = f'"{val}"'

            # 替换配置项（保持原有的注释和格式）- 用于单行配置
            pattern = rf"^(\s*{key}\s*=\s*)(.+)$"

            new_content = []
            found = False
            for line in content.splitlines():
                if re.match(pattern, line):
                    # 替换值，保留前面的空格和等号格式
                    match = re.match(pattern, line)
                    if match:
                        new_content.append(f"{match.group(1)}{val_str}")
                        found = True
                    else:
                        new_content.append(line)
                else:
                    new_content.append(line)

            if found:
                content = "\n".join(new_content)
            else:
                # 如果配置项不存在，添加到文件末尾
                content += f"\n{key} = {val_str}\n"

        config_path.write_text(content, encoding="utf-8")

    @staticmethod
    def get_current_config() -> dict:
        """获取当前配置（敏感字段会被掩码）

        Returns:
            当前配置字典
        """
        return {
            "MI_USER": config.MI_USER,
            "MI_PASS": "***" if config.MI_PASS else "",
            "MI_DID": config.MI_DID,
            "MI_REGION": config.MI_REGION,
            "MUSIC_API_BASE_URL": config.MUSIC_API_BASE_URL,
            "MUSIC_DEFAULT_PLATFORM": config.MUSIC_DEFAULT_PLATFORM,
            "SERVER_BASE_URL": config.SERVER_BASE_URL,
            "ENABLE_CONVERSATION_POLLING": config.ENABLE_CONVERSATION_POLLING,
            "CONVERSATION_POLL_INTERVAL": config.CONVERSATION_POLL_INTERVAL,
            "ENABLE_WAKE_WORD_FILTER": config.ENABLE_WAKE_WORD_FILTER,
            "WAKE_WORDS": config.WAKE_WORDS,
            "LOG_LEVEL": getattr(config, "LOG_LEVEL", "INFO"),
            "TIMEZONE": getattr(config, "TIMEZONE", "Asia/Shanghai"),
            "PROXY_SKIP_AUTH_FOR_LAN": getattr(config, "PROXY_SKIP_AUTH_FOR_LAN", True),
            "PROXY_LAN_NETWORKS": getattr(
                config,
                "PROXY_LAN_NETWORKS",
                [
                    "192.168.0.0/16",
                    "10.0.0.0/8",
                    "172.16.0.0/12",
                    "127.0.0.0/8",
                ],
            ),
        }

    @staticmethod
    def validate_config_keys(updates: dict) -> None:
        """验证配置项键是否允许修改

        Args:
            updates: 要更新的配置字典

        Raises:
            HTTPException: 当包含不允许的配置项时
        """
        for key in updates.keys():
            if key not in ALLOWED_KEYS:
                raise HTTPException(
                    status_code=422, detail=f"Unknown config key: {key}"
                )

    @staticmethod
    def filter_sensitive_fields(updates: dict) -> dict:
        """过滤掉值为 "***" 的敏感字段（表示不更改）

        Args:
            updates: 原始更新字典

        Returns:
            过滤后的更新字典
        """
        filtered = updates.copy()
        # 如果密码是占位符，则不更新
        if "MI_PASS" in filtered and filtered["MI_PASS"] == "***":
            del filtered["MI_PASS"]
        return filtered

    @staticmethod
    def reload_config_module() -> None:
        """重新加载配置模块，使更改生效"""
        reload_config()
