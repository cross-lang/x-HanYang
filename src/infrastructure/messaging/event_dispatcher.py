"""同步事件总线实现。

初期使用同步内存事件总线，后期可替换为 MQ（如 RabbitMQ、Kafka）。
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from src.application.shared.event_bus import EventBus
from src.domain.shared.domain_event import DomainEvent
from src.shared.logger import logger


class InMemoryEventBus(EventBus):
    """内存同步事件总线。

    适用于单体应用。事件在当前线程同步处理，
    失败时记录日志但不阻断主流程。
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[DomainEvent], None]]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning(f"事件处理失败: {event_type.__name__} -> {e}")

    def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.publish(event)

    def subscribe(self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        self._handlers[event_type].append(handler)
