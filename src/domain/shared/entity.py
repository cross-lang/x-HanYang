"""实体基类。

实体（Entity）拥有唯一标识，通过 ID 判等而非属性值。
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field


@dataclass
class Entity(ABC):
    """实体基类。

    所有领域实体必须继承此类。
    提供基于 ID 的相等性判断和哈希。

    Attributes:
        id: 实体唯一标识符
    """

    id: int = field(default=0)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id and self.id != 0

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
