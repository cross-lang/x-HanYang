"""文件应用层 — 命令、查询。"""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass

from src.domain.file.storage_provider import StorageProvider


# ══════════════════════════════════════════════════
#  上传 — Command + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class UploadFileCommand:
    """文件上传命令。"""

    filename: str
    content: bytes
    content_type: str | None = None


@dataclass(frozen=True)
class UploadFileResult:
    """文件上传结果。"""

    key: str
    filename: str
    size: int


class UploadFileHandler:
    """文件上传处理器。"""

    def __init__(self, storage_provider: StorageProvider) -> None:
        self._storage = storage_provider

    async def handle(self, command: UploadFileCommand) -> UploadFileResult:
        """执行文件上传。"""
        key = self._generate_key(command.filename)
        await asyncio.to_thread(self._storage.upload, key=key, data=command.content, content_type=command.content_type)
        return UploadFileResult(key=key, filename=command.filename, size=len(command.content))

    @staticmethod
    def _generate_key(filename: str) -> str:
        """生成唯一存储键。"""
        timestamp = int(time.time() * 1000)
        name_hash = hashlib.sha1(filename.encode()).hexdigest()[:8]
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        return f"{timestamp}_{name_hash}.{ext}"


# ══════════════════════════════════════════════════
#  下载 — Query + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class DownloadFileQuery:
    """文件下载查询。"""

    key: str


@dataclass(frozen=True)
class DownloadFileResult:
    """文件下载结果。"""

    content: bytes
    key: str


class DownloadFileHandler:
    """文件下载处理器。"""

    def __init__(self, storage_provider: StorageProvider) -> None:
        self._storage = storage_provider

    async def handle(self, query: DownloadFileQuery) -> DownloadFileResult:
        """执行文件下载。"""
        content = await asyncio.to_thread(self._storage.download, key=query.key)
        return DownloadFileResult(content=content, key=query.key)
