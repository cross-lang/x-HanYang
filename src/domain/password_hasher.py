"""密码哈希领域接口。

定义在领域层的密码哈希协议，实现在基础设施层。
领域层通过此接口进行密码哈希和验证，不直接依赖 bcrypt 等外部库。
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """密码哈希接口。"""

    @abstractmethod
    def hash(self, password: str) -> str:
        """哈希密码。

        Args:
            password: 明文密码

        Returns:
            str: 哈希后的密码字符串
        """

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """验证密码。

        Args:
            password: 明文密码
            hashed: 哈希后的密码

        Returns:
            bool: 是否匹配
        """
