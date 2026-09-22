"""文件管理请求/响应 Schema。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """文件上传响应。

    Attributes:
        key: 存储键
        filename: 原始文件名
        size: 文件大小（字节）
    """

    key: str = Field(..., description="存储键")
    filename: str = Field(..., description="原始文件名")
    size: int = Field(..., description="文件大小（字节）")
