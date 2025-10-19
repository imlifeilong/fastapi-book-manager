from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.exc import IntegrityError


class ItemNotFound(Exception):
    def __init__(self, name: str):
        self.name = name


async def item_not_found_handler(request: Request, exc: ItemNotFound):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": f"{exc.name} not found"})


class DuplicateEntryException(HTTPException):
    """重复条目异常"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """数据库完整性错误处理"""
    # 检查是否是唯一约束违反
    if "UNIQUE constraint failed" in str(exc.orig) or "duplicate key" in str(exc.orig):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Duplicate entry found"}
        )

    # 其他完整性错误
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error"}
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
