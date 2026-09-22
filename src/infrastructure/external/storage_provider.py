"""文件存储提供者。

实现领域层 StorageProvider 接口。
"""

from __future__ import annotations

import os

from src.domain.file.storage_provider import StorageProvider
from src.shared.logger import logger


class LocalStorageProvider(StorageProvider):
    """本地文件存储实现。"""

    def __init__(self, base_path: str = "./uploads") -> None:
        self._base_path = base_path

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> str:
        import os

        path = os.path.join(self._base_path, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def download(self, key: str) -> bytes:
        import os

        path = os.path.join(self._base_path, key)
        with open(path, "rb") as f:
            return f.read()

    def delete(self, key: str) -> bool:
        import os

        path = os.path.join(self._base_path, key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False


class S3StorageProvider(StorageProvider):
    """S3 对象存储实现（桩）。"""

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> str:
        logger.info(f"[S3] 上传文件: {key}")
        # TODO: 实现 S3 上传逻辑
        return key

    def download(self, key: str) -> bytes:
        logger.info(f"[S3] 下载文件: {key}")
        # TODO: 实现 S3 下载逻辑
        return b""

    def delete(self, key: str) -> bool:
        logger.info(f"[S3] 删除文件: {key}")
        # TODO: 实现 S3 删除逻辑
        return True
