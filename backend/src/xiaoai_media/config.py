from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 从项目根目录加载 .env 文件 (backend/../.env)
_root_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_root_env, override=True)


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip() or default


MI_USER: str = _optional("MI_USER")
MI_PASS: str = _optional("MI_PASS")
MI_PASS_TOKEN: str = _optional("MI_PASS_TOKEN")
MI_DID: str = _optional("MI_DID", "")
MI_REGION: str = _optional("MI_REGION", "cn")
