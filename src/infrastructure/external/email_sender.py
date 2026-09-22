"""邮件发送适配器。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.shared.logger import logger


class EmailSender(ABC):
    """邮件发送接口（定义在基础设施层，可被领域服务依赖）。"""

    @abstractmethod
    def send(self, to_address: str, subject: str, body: str) -> bool:
        """发送邮件。"""


class SmtpEmailSender(EmailSender):
    """SMTP 邮件发送实现。"""

    def send(self, to_address: str, subject: str, body: str) -> bool:
        logger.info(f"[Email] 发送邮件到 {to_address}: {subject}")
        # TODO: 实现 SMTP 发送逻辑
        return True


class MockEmailSender(EmailSender):
    """Mock 邮件发送（测试/开发环境使用）。"""

    def send(self, to_address: str, subject: str, body: str) -> bool:
        logger.info(f"[Email/Mock] 发送邮件到 {to_address}: {subject}")
        return True
