"""
图书馆管理系统 - FastAPI 主应用

功能模块：
- 用户认证与权限管理（auth）
- 图书信息管理（books）
- 借阅与归还管理（borrows）
- 用户管理（users）
- 逾期检查与罚款计算

技术栈：
- FastAPI: 高性能 Web 框架
- SQLAlchemy: ORM 数据库操作
- SQLite: 轻量级数据库
- OAuth2 + JWT: 身份认证
"""

# 导入 FastAPI 核心模块
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # 跨域中间件
from contextlib import asynccontextmanager  # 异步上下文管理器

# 导入数据库相关模块
from database import engine, Base
from routers import auth_router, users_router, books_router, borrows_router

# 导入认证工具和用户模型
from utils.auth import get_password_hash
from models.user import User, UserRole
from sqlalchemy.orm import Session
from database import SessionLocal


def init_db():
    """
    初始化数据库，创建表结构和默认管理员账号
    
    执行流程：
    1. 创建所有表（如果不存在）
    2. 检查是否已存在默认管理员
    3. 如果不存在，创建管理员、图书管理员、普通读者三个测试账号
    """
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 检查是否已存在管理员账号
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 创建系统管理员
            admin_user = User(
                username="admin",
                email="admin@library.com",
                hashed_password=get_password_hash("admin123"),  # 密码哈希加密
                full_name="系统管理员",
                role=UserRole.ADMIN,  # 管理员角色
                is_active=True
            )
            db.add(admin_user)

            # 创建图书管理员
            librarian = User(
                username="librarian",
                email="librarian@library.com",
                hashed_password=get_password_hash("lib123"),
                full_name="图书管理员",
                role=UserRole.LIBRARIAN,  # 图书管理员角色
                is_active=True
            )
            db.add(librarian)

            # 创建普通读者
            reader = User(
                username="reader",
                email="reader@library.com",
                hashed_password=get_password_hash("reader123"),
                full_name="普通读者",
                role=UserRole.READER,  # 普通读者角色
                is_active=True
            )
            db.add(reader)

            # 提交事务
            db.commit()
            print("✅ 默认用户创建成功！")
            print("   管理员: admin / admin123")
            print("   图书管理员: librarian / lib123")
            print("   读者: reader / reader123")
    finally:
        # 确保关闭数据库连接
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理函数
    
    FastAPI 0.100+ 引入的新特性，替代旧版的 @app.on_event("startup") 和 @app.on_event("shutdown")
    
    参数：
        app: FastAPI 应用实例
        
    执行流程：
        1. 启动时：调用 init_db() 初始化数据库
        2. yield：应用运行期间
        3. 关闭时：可以在这里添加资源清理逻辑
    """
    # 启动时执行
    init_db()
    yield
    # 关闭时执行（如需清理资源可在此添加）


# 创建 FastAPI 应用实例
app = FastAPI(
    title="图书馆管理系统 API",          # API 标题（显示在文档中）
    description="基于 FastAPI 的现代化图书馆管理系统",  # API 描述
    version="1.0.0",                    # API 版本
    lifespan=lifespan                   # 生命周期管理
)

# 配置 CORS（跨域资源共享）中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,             # 允许携带凭证（cookies等）
    allow_methods=["*"],                # 允许所有 HTTP 方法
    allow_headers=["*"],                # 允许所有请求头
)

# 注册路由（模块化管理）
app.include_router(auth_router, prefix="/api/v1")      # 认证路由
app.include_router(users_router, prefix="/api/v1")     # 用户管理路由
app.include_router(books_router, prefix="/api/v1")     # 图书管理路由
app.include_router(borrows_router, prefix="/api/v1")   # 借阅管理路由


@app.get("/")
def root():
    """
    根路径接口
    
    返回欢迎信息和文档链接
    """
    return {
        "message": "欢迎使用图书馆管理系统 API",
        "docs": "/docs",          # Swagger UI 文档地址
        "redoc": "/redoc",        # ReDoc 文档地址
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    健康检查接口
    
    用于监控系统状态，返回 {"status": "healthy"} 表示正常运行
    """
    return {"status": "healthy"}


# 开发环境运行入口
if __name__ == "__main__":
    import uvicorn
    # 启动 Uvicorn 服务器
    # host="0.0.0.0": 允许外部访问
    # port=8000: 监听端口
    # reload=True: 开发模式下自动重载
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
