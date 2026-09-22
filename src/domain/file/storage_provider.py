"""文件存储领域端口。

定义在领域层的存储接口，实现在基础设施层。
应用层通过此接口进行文件操作，不直接依赖具体存储实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """文件存储端口接口。"""

    @abstractmethod
    def upload(self, key: str, data: bytes, content_type: str | None = None) -> str:
        """上传文件，返回访问 URL。"""

    @abstractmethod
    def download(self, key: str) -> bytes:
        """下载文件。"""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除文件。"""
