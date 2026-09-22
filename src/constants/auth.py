"""认证与令牌相关常量。"""

from __future__ import annotations

# ── 令牌 ─────────────────────────────────────────
AUTH_SCHEME: str = "Bearer"
TOKEN_TYPE_ACCESS: str = "access"
TOKEN_TYPE_REFRESH: str = "refresh"
DEFAULT_JWT_ALGORITHM: str = "HS256"

# 令牌过期时间（分钟）
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天
DEFAULT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

# 令牌过期时间（秒），用于返回给客户端
DEFAULT_TOKEN_EXPIRES_IN_SECONDS: int = 604800  # 7 天

# ── 密码强度 ─────────────────────────────────────
PASSWORD_MIN_LENGTH: int = 8
PASSWORD_MAX_LENGTH: int = 128
