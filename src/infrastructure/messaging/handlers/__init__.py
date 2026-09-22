"""事件处理器注册。

所有领域事件处理器在此统一注册到 EventBus。
"""

from src.application.shared.event_bus import EventBus
from src.domain.user.events import (
    UserCreated,
    EmailChanged,
    PasswordChanged,
    UserLocked,
    UserDeleted,
)
from src.infrastructure.messaging.handlers.logging import (
    on_user_created,
    on_email_changed,
    on_password_changed,
    on_user_locked,
    on_user_deleted,
)


def register_event_handlers(event_bus: EventBus) -> None:
    """注册所有领域事件处理器。

    在应用启动时调用一次，将事件处理函数订阅到 EventBus。

    Args:
        event_bus: 事件总线实例
    """
    event_bus.subscribe(UserCreated, on_user_created)
    event_bus.subscribe(EmailChanged, on_email_changed)
    event_bus.subscribe(PasswordChanged, on_password_changed)
    event_bus.subscribe(UserLocked, on_user_locked)
    event_bus.subscribe(UserDeleted, on_user_deleted)
