"""领域事件基类。

领域事件（Domain Event）表示聚合中发生的有意义的事情，
用于实现聚合间的最终一致性解耦。
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent(ABC):
    """领域事件基类。

    所有领域事件必须继承此类，使用 frozen=True 保证不可变。

    Attributes:
        event_id: 事件唯一标识（用于幂等去重）
        occurred_at: 事件发生时间（UTC）
    """

    event_id: str = field(default_factory=lambda: uuid4().hex)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
