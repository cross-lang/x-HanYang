"""安全工具 — 密码哈希、JWT 等。

跨层共享的安全工具函数。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt


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


def create_access_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 10080,
    extra_claims: dict | None = None,
) -> str:
    """创建访问令牌。

    Args:
        subject: 令牌主体（通常是用户 ID 的字符串形式）
        secret_key: 签名密钥
        algorithm: 签名算法
        expires_minutes: 过期时间（分钟）
        extra_claims: 额外载荷

    Returns:
        str: JWT 令牌字符串
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_refresh_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 10080,
) -> str:
    """创建刷新令牌。

    Args:
        subject: 令牌主体
        secret_key: 签名密钥
        algorithm: 签名算法
        expires_minutes: 过期时间（分钟，默认 7 天）

    Returns:
        str: JWT 刷新令牌字符串
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "refresh",
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict:
    """解码并验证 JWT 令牌。

    Args:
        token: JWT 令牌字符串
        secret_key: 签名密钥
        algorithm: 签名算法

    Returns:
        dict: 令牌载荷

    Raises:
        jwt.ExpiredSignatureError: 令牌已过期
        jwt.InvalidTokenError: 令牌无效
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])
