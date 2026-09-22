"""文件上传命令及处理器。"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from src.domain.file.storage_provider import StorageProvider


@dataclass(frozen=True)
class UploadFileCommand:
    """文件上传命令。

    Attributes:
        filename: 原始文件名
        content: 文件内容（字节）
        content_type: MIME 类型
    """

    filename: str
    content: bytes
    content_type: str | None = None


@dataclass(frozen=True)
class UploadFileResult:
    """文件上传结果。

    Attributes:
        key: 存储键
        filename: 原始文件名
        size: 文件大小（字节）
    """

    key: str
    filename: str
    size: int


class UploadFileHandler:
    """文件上传处理器。"""

    def __init__(self, storage_provider: StorageProvider) -> None:
        self._storage = storage_provider

    async def handle(self, command: UploadFileCommand) -> UploadFileResult:
        """执行文件上传。

        Args:
            command: 文件上传命令

        Returns:
            UploadFileResult: 上传结果
        """
        import asyncio

        key = self._generate_key(command.filename)
        await asyncio.to_thread(
            self._storage.upload,
            key=key,
            data=command.content,
            content_type=command.content_type,
        )
        return UploadFileResult(
            key=key,
            filename=command.filename,
            size=len(command.content),
        )

    @staticmethod
    def _generate_key(filename: str) -> str:
        """生成唯一存储键。

        Args:
            filename: 原始文件名

        Returns:
            str: 唯一存储键（格式: timestamp_hash.ext）
        """
        timestamp = int(time.time() * 1000)
        name_hash = hashlib.sha1(filename.encode()).hexdigest()[:8]
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        return f"{timestamp}_{name_hash}.{ext}"
