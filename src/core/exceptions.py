"""框架层异常。

这些是技术层面的异常，与领域异常（domain/shared/domain_exception.py）区分。
领域异常表示业务规则违反，框架异常表示技术问题。
"""

from __future__ import annotations


class FrameworkException(Exception):
    """框架层异常基类。"""

    def __init__(self, message: str, code: int = 500) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class DatabaseException(FrameworkException):
    """数据库操作异常。"""

    def __init__(self, message: str = "数据库操作失败") -> None:
        super().__init__(message=message, code=500)


class CacheException(FrameworkException):
    """缓存操作异常。"""

    def __init__(self, message: str = "缓存操作失败") -> None:
        super().__init__(message=message, code=500)


class ExternalServiceException(FrameworkException):
    """外部服务调用异常。"""

    def __init__(self, message: str = "外部服务调用失败") -> None:
        super().__init__(message=message, code=502)
