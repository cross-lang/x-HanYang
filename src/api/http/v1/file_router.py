"""文件管理 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import Response

from src.application.auth.dto.auth_dto import CurrentUserDTO
from src.application.file.commands.upload_file import UploadFileCommand, UploadFileHandler
from src.application.file.queries.download_file import DownloadFileQuery, DownloadFileHandler
from src.api.http.dependencies import get_current_user_dep
from src.api.http.schemas.file import FileUploadResponse
from src.api.shared.response import success_response
from src.domain.file.storage_provider import StorageProvider
from src.infrastructure.external.storage_provider import LocalStorageProvider
from src.infrastructure.config.settings import get_settings

router = APIRouter(prefix="/files", tags=["文件管理"])


def _get_storage_provider() -> StorageProvider:
    """获取存储提供者。"""
    settings = get_settings()
    return LocalStorageProvider(base_path=settings.storage_local_path)


def _get_upload_handler(
    storage: StorageProvider = Depends(_get_storage_provider),
) -> UploadFileHandler:
    """获取文件上传处理器。"""
    return UploadFileHandler(storage_provider=storage)


def _get_download_handler(
    storage: StorageProvider = Depends(_get_storage_provider),
) -> DownloadFileHandler:
    """获取文件下载处理器。"""
    return DownloadFileHandler(storage_provider=storage)


@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile,
    request: Request,
    handler: UploadFileHandler = Depends(_get_upload_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """上传文件接口。

    Args:
        file: 上传的文件
        request: HTTP 请求
        handler: 文件上传处理器
        current_user: 当前用户

    Returns:
        dict: 上传结果（key, filename, size）
    """
    content = await file.read()
    command = UploadFileCommand(
        filename=file.filename or "unknown",
        content=content,
        content_type=file.content_type,
    )
    result = await handler.handle(command)
    return success_response(
        FileUploadResponse(key=result.key, filename=result.filename, size=result.size).model_dump(),
        request,
    )


@router.get("/{file_key:path}", summary="下载文件")
async def download_file(
    file_key: str,
    handler: DownloadFileHandler = Depends(_get_download_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> Response:
    """下载文件接口。

    Args:
        file_key: 文件存储键
        handler: 文件下载处理器
        current_user: 当前用户

    Returns:
        Response: 文件内容
    """
    result = await handler.handle(DownloadFileQuery(key=file_key))
    return Response(content=result.content, media_type="application/octet-stream")
