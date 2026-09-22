"""令牌管理模块。

基于 PyJWT 实现访问/刷新令牌的签发与校验。

Functions:
    create_access_token: 签发访问令牌
    create_refresh_token: 签发刷新令牌
    decode_token: 解码并校验令牌
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


def create_access_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 10080,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """签发访问令牌。

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
    payload: dict[str, Any] = {
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
    """签发刷新令牌。

    Args:
        subject: 令牌主体
        secret_key: 签名密钥
        algorithm: 签名算法
        expires_minutes: 过期时间（分钟，默认 7 天）

    Returns:
        str: JWT 刷新令牌字符串
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "refresh",
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict[str, Any]:
    """解码并校验令牌。

    Args:
        token: JWT 令牌字符串
        secret_key: 签名密钥
        algorithm: 签名算法

    Returns:
        dict[str, Any]: 令牌载荷

    Raises:
        jwt.ExpiredSignatureError: 令牌已过期
        jwt.InvalidTokenError: 令牌无效
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
