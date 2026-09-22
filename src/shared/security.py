"""安全工具 — 密码哈希、JWT 等。

跨层共享的安全工具函数。
"""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """哈希密码。

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码字符串
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """验证密码。

    Args:
        password: 明文密码
        hashed: 哈希后的密码

    Returns:
        bool: 是否匹配
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
