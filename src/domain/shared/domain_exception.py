"""领域异常。

领域层的业务规则违反时抛出，不依赖任何框架异常。
应用层或接口层捕获后转换为对应的 HTTP 状态码。
"""

from __future__ import annotations


class DomainException(Exception):
    """领域业务异常基类。

    Attributes:
        message: 人类可读的错误描述
        code: 业务错误码（可选，用于客户端识别）
    """

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class EntityNotFoundException(DomainException):
    """实体不存在。"""


class ConflictException(DomainException):
    """业务冲突（如唯一约束违反）。"""


class AuthenticationException(DomainException):
    """认证失败。"""


class AuthorizationException(DomainException):
    """授权失败（权限不足）。"""


class ValidationException(DomainException):
    """业务规则校验失败。"""
