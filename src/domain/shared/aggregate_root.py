"""聚合根基类。

聚合根（Aggregate Root）是聚合的入口点，负责：
- 维护聚合内部的一致性边界
- 收集领域事件，由应用层在事务提交后统一分发
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.shared.entity import Entity
from src.domain.shared.domain_event import DomainEvent


@dataclass
class AggregateRoot(Entity):
    """聚合根基类。

    所有聚合必须通过聚合根访问。聚合根收集领域事件，
    应用层在持久化完成后调用 collect_and_clear_events() 获取并清空。

    Attributes:
        _domain_events: 待发布的领域事件列表（不应暴露给外部直接操作）
    """

    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def _add_event(self, event: DomainEvent) -> None:
        """添加领域事件（仅子类调用）。"""
        self._domain_events.append(event)

    @property
    def domain_events(self) -> list[DomainEvent]:
        """获取待发布的领域事件（只读副本）。"""
        return list(self._domain_events)

    def collect_and_clear_events(self) -> list[DomainEvent]:
        """收集并清空领域事件（应用层调用）。

        Returns:
            list[DomainEvent]: 本次收集到的领域事件
        """
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
