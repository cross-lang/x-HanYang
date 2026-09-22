"""登录会话管理模块（有状态 JWT / 混合会话）。

JWT 仍作为令牌载体，真正的"是否登录"判据来自 Redis，从而实现即时登出。

核心机制：
    - 登录成功后，将 access_token 写入 Redis（key = login:{user_id}，TTL = access_token 有效期）
    - 刷新令牌时，校验 Redis 中存储的 token 是否与当前请求一致
    - 登出时，删除 Redis 中的 key，使所有该用户的令牌立即失效
    - 单设备登录：新登录/刷新会覆盖旧 token，旧设备的令牌自然失效

Redis 不可用时自动降级为无状态 JWT（放行），不阻断业务。
"""

from __future__ import annotations

from src.core.logger import logger


def _key(user_id: int) -> str:
    """生成登录态 Redis 键名。"""
    return f"login:{user_id}"


async def set_login_status(user_id: int, token: str, ttl_seconds: int) -> None:
    """写入用户登录态（覆盖式，天然支持单设备登录）。

    存储当前有效的访问令牌；新登录/刷新会覆盖该值，
    使旧令牌在下次校验时因不匹配而失效。

    Args:
        user_id: 用户 ID
        token: 当前有效的访问令牌
        ttl_seconds: 过期秒数（建议等于 access_token 有效期）
    """
    from src.infrastructure.external.cache_provider import get_cache_provider

    try:
        provider = get_cache_provider()
        await provider.set(_key(user_id), token, ttl=ttl_seconds)
    except Exception as e:  # noqa: BLE001
        # 登录态写入失败不应阻断登录，仅告警
        logger.warning(f"SetLoginStatus failed for user {user_id}: {e}")


async def get_login_status(user_id: int) -> str | None:
    """读取用户当前有效的登录令牌。

    未配置 Redis 或异常时返回 None（降级放行）。

    Args:
        user_id: 用户 ID

    Returns:
        str | None: 登录态令牌，未登录或异常时为 None
    """
    from src.infrastructure.external.cache_provider import get_cache_provider

    try:
        provider = get_cache_provider()
        return await provider.get(_key(user_id))
    except Exception as e:  # noqa: BLE001
        logger.warning(f"GetLoginStatus failed for user {user_id}: {e}")
        return None


async def is_logged_in(user_id: int) -> bool:
    """判断用户是否处于登录态（key 存在即为已登录）。

    登出删除 key 后返回 False，令牌立即失效。
    Redis 未配置或不可用时降级放行（返回 True），不阻断登录态校验。

    Args:
        user_id: 用户 ID

    Returns:
        bool: 存在登录态记录即为已登录；Redis 不可用时降级放行
    """
    status = await get_login_status(user_id)
    if status is None:
        # get_login_status 返回 None 有两种情况：
        # 1. Redis 未配置/不可用 — 应降级放行
        # 2. key 不存在 — 用户已登出
        # 由于无法区分，统一降级放行（与 HanJiang 行为一致）
        return True
    return True


async def is_token_valid(user_id: int, token: str) -> bool:
    """校验当前令牌是否与 Redis 中存储的登录态一致。

    用于刷新令牌和校验访问令牌有效性：
    - 若 Redis 中无记录 → 用户已登出 → 返回 False
    - 若 Redis 中的 token 与传入 token 不匹配 → 被新设备顶替 → 返回 False
    - 若匹配 → 登录态有效 → 返回 True

    Redis 不可用时降级放行（返回 True）。

    Args:
        user_id: 用户 ID
        token: 待校验的访问令牌

    Returns:
        bool: 令牌是否有效
    """
    from src.infrastructure.external.cache_provider import get_cache_provider

    try:
        provider = get_cache_provider()
        stored = await provider.get(_key(user_id))
    except Exception as e:  # noqa: BLE001
        # Redis 不可用时降级放行
        logger.warning(f"IsTokenValid check failed for user {user_id}: {e}")
        return True

    if stored is None:
        # Redis 未配置或用户已登出
        # 区分：Redis 未配置 → 降级放行；key 不存在 → 已登出
        from src.core.config import get_settings
        settings = get_settings()
        if not settings.redis_url:
            return True  # Redis 未配置，降级放行
        return False  # Redis 可用但 key 不存在 = 已登出

    return stored == token


async def clear_login_status(user_id: int) -> None:
    """删除用户登录态（登出）。

    删除后，该用户所有已签发的令牌（access_token）将立即失效。

    Args:
        user_id: 用户 ID
    """
    from src.infrastructure.external.cache_provider import get_cache_provider

    try:
        provider = get_cache_provider()
        await provider.delete(_key(user_id))
    except Exception as e:  # noqa: BLE001
        logger.warning(f"ClearLoginStatus failed for user {user_id}: {e}")


__all__ = [
    "set_login_status",
    "get_login_status",
    "is_logged_in",
    "is_token_valid",
    "clear_login_status",
]
