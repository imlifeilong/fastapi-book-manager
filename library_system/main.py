"""
图书馆管理系统 - FastAPI 主应用

功能模块：
- 用户认证与权限管理
- 图书信息管理
- 借阅与归还管理
- 逾期检查与罚款计算
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base
from routers import auth_router, users_router, books_router, borrows_router
from utils.auth import get_password_hash
from models.user import User, UserRole
from sqlalchemy.orm import Session
from database import SessionLocal


def init_db():
    """初始化数据库，创建默认管理员账号"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@library.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)

            # 创建示例图书管理员
            librarian = User(
                username="librarian",
                email="librarian@library.com",
                hashed_password=get_password_hash("lib123"),
                full_name="图书管理员",
                role=UserRole.LIBRARIAN,
                is_active=True
            )
            db.add(librarian)

            # 创建示例读者
            reader = User(
                username="reader",
                email="reader@library.com",
                hashed_password=get_password_hash("reader123"),
                full_name="普通读者",
                role=UserRole.READER,
                is_active=True
            )
            db.add(reader)

            db.commit()
            print("✅ 默认用户创建成功！")
            print("   管理员: admin / admin123")
            print("   图书管理员: librarian / lib123")
            print("   读者: reader / reader123")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    init_db()
    yield
    # 关闭时执行（如需清理资源可在此添加）


app = FastAPI(
    title="图书馆管理系统 API",
    description="基于 FastAPI 的现代化图书馆管理系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(books_router, prefix="/api/v1")
app.include_router(borrows_router, prefix="/api/v1")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "欢迎使用图书馆管理系统 API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
