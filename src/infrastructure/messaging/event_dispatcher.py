"""异步内存事件总线实现。

初期使用内存事件总线，后期可替换为 MQ（如 RabbitMQ、Kafka）。
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable

from src.application.shared.event_bus import EventBus, EventHandler
from src.domain.shared.domain_event import DomainEvent
from src.core.logger import logger

import inspect


class InMemoryEventBus(EventBus):
    """内存异步事件总线。

    适用于单体应用。事件在当前协程异步处理，
    失败时记录日志但不阻断主流程。
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        """发布单个领域事件。

        Args:
            event: 领域事件
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                logger.warning(f"事件处理失败: {event_type.__name__} -> {e}")

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """批量发布领域事件。

        Args:
            events: 领域事件列表
        """
        for event in events:
            await self.publish(event)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """订阅指定类型的领域事件。

        Args:
            event_type: 事件类型
            handler: 事件处理函数（同步或异步均可）
        """
        self._handlers[event_type].append(handler)
