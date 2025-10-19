from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from database import create_tables
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.users import router as users_router
from exceptions import (
    DuplicateEntryException,
    integrity_error_handler,
    http_exception_handler,
    global_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    create_tables()
    print("Database tables created successfully")
    yield
    # 关闭时清理资源
    print("Shutting down application")


# 创建FastAPI应用
app = FastAPI(
    title="图书管理系统 API",
    description="一个基于FastAPI的图书管理系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义异常处理器
app.add_exception_handler(DuplicateEntryException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(RequestValidationError, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 添加路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router)


@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "欢迎使用图书管理系统API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
