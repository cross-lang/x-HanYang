"""邮件发送适配器。

提供邮件发送的抽象接口和具体实现。
SMTP 实现使用 asyncio.to_thread() 包装同步 smtplib，避免阻塞事件循环。
"""

from __future__ import annotations

import asyncio
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache

from src.shared.logger import logger


class EmailSender(ABC):
    """邮件发送接口。

    定义在基础设施层，业务层通过依赖注入使用。
    """

    @abstractmethod
    async def send(self, to_address: str, subject: str, body: str, html: bool = True) -> bool:
        """发送邮件。

        Args:
            to_address: 收件人地址
            subject: 邮件主题
            body: 邮件正文
            html: 是否为 HTML 格式（False 时为纯文本）

        Returns:
            bool: 是否发送成功
        """


class SmtpEmailSender(EmailSender):
    """SMTP 邮件发送实现。

    使用 asyncio.to_thread() 包装同步 smtplib，避免阻塞事件循环。
    支持 STARTTLS（端口 587）和 SMTPS（端口 465）。
    """

    def __init__(
        self,
        host: str,
        port: int = 587,
        username: str = "",
        password: str = "",
        from_name: str = "HanYang",
        from_address: str = "",
        use_tls: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_name = from_name
        self._from_address = from_address
        self._use_tls = use_tls

    async def send(self, to_address: str, subject: str, body: str, html: bool = True) -> bool:
        """发送邮件（异步）。

        Args:
            to_address: 收件人地址
            subject: 邮件主题
            body: 邮件正文
            html: 是否为 HTML 格式

        Returns:
            bool: 是否发送成功
        """
        try:
            return await asyncio.to_thread(self._send_sync, to_address, subject, body, html)
        except Exception as e:
            logger.error(f"邮件发送失败: {to_address} -> {e}")
            return False

    def _send_sync(self, to_address: str, subject: str, body: str, html: bool) -> bool:
        """同步发送邮件（在线程池中运行）。"""
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self._from_name} <{self._from_address}>"
        msg["To"] = to_address
        msg["Subject"] = subject

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        if self._use_tls:
            server = smtplib.SMTP(self._host, self._port, timeout=30)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(self._host, self._port, timeout=30)

        try:
            if self._username:
                server.login(self._username, self._password)
            server.send_message(msg)
        finally:
            server.quit()

        logger.info(f"邮件发送成功: {to_address} - {subject}")
        return True


class MockEmailSender(EmailSender):
    """Mock 邮件发送（测试/开发环境使用）。"""

    async def send(self, to_address: str, subject: str, body: str, html: bool = True) -> bool:
        """模拟发送邮件（仅记录日志）。

        Args:
            to_address: 收件人地址
            subject: 邮件主题
            body: 邮件正文
            html: 是否为 HTML 格式

        Returns:
            bool: 始终返回 True
        """
        logger.info(f"[Email/Mock] 发送邮件到 {to_address}: {subject}")
        return True


@lru_cache(maxsize=1)
def get_email_sender() -> EmailSender:
    """获取邮件发送实例（缓存）。

    根据配置自动选择 SMTP 或 Mock 实现。

    Returns:
        EmailSender: 邮件发送实例
    """
    from src.infrastructure.config.settings import get_settings

    settings = get_settings()
    if settings.smtp_host:
        return SmtpEmailSender(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_name=settings.smtp_from_name,
            from_address=settings.smtp_from_address,
            use_tls=settings.smtp_use_tls,
        )
    return MockEmailSender()
