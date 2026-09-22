"""领域事件日志处理器。

记录所有领域事件到日志系统。
后续可扩展为推送到钉钉、飞书、邮件等外部平台。
"""

from src.core.logger import logger
from src.domain.user.events import (
    UserCreated,
    EmailChanged,
    PasswordChanged,
    UserLocked,
    UserDeleted,
)


async def on_user_created(event: UserCreated) -> None:
    """用户创建事件处理。"""
    logger.info(f"[Event] 用户创建: user_id={event.user_id}, username={event.username}")


async def on_email_changed(event: EmailChanged) -> None:
    """邮箱变更事件处理。"""
    logger.info(
        f"[Event] 邮箱变更: user_id={event.user_id}, "
        f"{event.old_email} -> {event.new_email}"
    )


async def on_password_changed(event: PasswordChanged) -> None:
    """密码变更事件处理。"""
    logger.info(f"[Event] 密码变更: user_id={event.user_id}")


async def on_user_locked(event: UserLocked) -> None:
    """用户锁定事件处理。"""
    logger.info(f"[Event] 用户锁定: user_id={event.user_id}")


async def on_user_deleted(event: UserDeleted) -> None:
    """用户删除事件处理。"""
    logger.info(f"[Event] 用户删除: user_id={event.user_id}, username={event.username}")
