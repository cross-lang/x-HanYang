"""业务固定错误/提示消息常量。"""

from __future__ import annotations

# ── 认证 ─────────────────────────────────────
MSG_INVALID_CREDENTIALS: str = "账号或密码错误"
MSG_ACCOUNT_LOCKED: str = "账号已被锁定"
MSG_USER_NOT_FOUND: str = "用户不存在"
MSG_ACCESS_TOKEN_EXPIRED: str = "令牌已过期"
MSG_REFRESH_TOKEN_EXPIRED: str = "刷新令牌已过期"
MSG_INVALID_TOKEN: str = "无效的令牌"
MSG_INVALID_ACCESS_TOKEN: str = "无效的访问令牌"
MSG_INVALID_REFRESH_TOKEN: str = "无效的刷新令牌"
MSG_MISSING_TOKEN: str = "缺少认证令牌"
MSG_INVALID_OR_EXPIRED_TOKEN: str = "无效或过期的令牌"

# ── 通用 ─────────────────────────────────────
MSG_INTERNAL_SERVER_ERROR: str = "服务器内部错误"
MSG_LOGOUT_SUCCESS: str = "退出成功"
MSG_USER_DELETED: str = "用户删除成功"

# ── 角色 ─────────────────────────────────────
MSG_ROLE_DELETED: str = "角色删除成功"
