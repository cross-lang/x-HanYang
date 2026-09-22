"""安全工具 — 密码哈希。

跨层共享的密码哈希工具函数。JWT 令牌管理请使用 src.core.tokens。
"""

from __future__ import annotations

import secrets

import bcrypt

from src.core.tokens import create_access_token, create_refresh_token, decode_token  # noqa: F401


def generate_secret_key() -> str:
    """生成随机安全密钥（用于本地开发或密钥轮换）。

    Returns:
        str: 64 字符 URL-safe 随机字符串
    """
    return secrets.token_urlsafe(48)


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


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
