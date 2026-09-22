"""文件下载查询及处理器。"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from src.domain.file.storage_provider import StorageProvider


@dataclass(frozen=True)
class DownloadFileQuery:
    """文件下载查询。

    Attributes:
        key: 存储键
    """

    key: str


@dataclass(frozen=True)
class DownloadFileResult:
    """文件下载结果。

    Attributes:
        content: 文件内容（字节）
        key: 存储键
    """

    content: bytes
    key: str


class DownloadFileHandler:
    """文件下载处理器。"""

    def __init__(self, storage_provider: StorageProvider) -> None:
        self._storage = storage_provider

    async def handle(self, query: DownloadFileQuery) -> DownloadFileResult:
        """执行文件下载。

        Args:
            query: 文件下载查询

        Returns:
            DownloadFileResult: 下载结果
        """
        content = await asyncio.to_thread(self._storage.download, key=query.key)
        return DownloadFileResult(content=content, key=query.key)
