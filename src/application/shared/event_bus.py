"""事件总线接口。

应用层定义事件总线抽象，基础设施层提供实现。
支持领域事件的同步/异步分发。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from src.domain.shared.domain_event import DomainEvent


class EventBus(ABC):
    """事件总线接口。"""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """发布单个领域事件。

        Args:
            event: 领域事件
        """

    @abstractmethod
    def publish_all(self, events: list[DomainEvent]) -> None:
        """批量发布领域事件。

        Args:
            events: 领域事件列表
        """

    @abstractmethod
    def subscribe(self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """订阅指定类型的领域事件。

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
