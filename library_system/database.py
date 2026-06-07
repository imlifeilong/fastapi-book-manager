"""
数据库配置模块

负责配置 SQLAlchemy 数据库连接和会话管理

技术要点：
- 使用 SQLite 作为开发数据库（轻量级，无需额外服务）
- SQLAlchemy ORM 进行数据库操作
- 依赖注入模式提供数据库会话
"""

# 导入 SQLAlchemy 核心组件
from sqlalchemy import create_engine           # 数据库引擎
from sqlalchemy.ext.declarative import declarative_base  # 模型基类
from sqlalchemy.orm import sessionmaker        # 会话工厂

# 数据库连接 URL
# SQLite 数据库文件路径，./library.db 表示当前目录下的 library.db 文件
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"

# 创建数据库引擎
# connect_args={"check_same_thread": False}: SQLite 特有配置，允许多线程访问
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit=False: 禁用自动提交，需要手动 commit
# autoflush=False: 禁用自动刷新，提高性能
# bind=engine: 绑定到上面创建的数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类
# 所有 SQLAlchemy 模型都需要继承这个基类
Base = declarative_base()


def get_db():
    """
    数据库会话依赖函数
    
    使用生成器模式（yield）提供数据库会话，确保连接正确释放
    
    使用方式：
    def some_route(db: Session = Depends(get_db)):
        # 使用 db 进行数据库操作
    
    执行流程：
    1. 创建新的数据库会话
    2. yield 返回会话给调用者
    3. 调用者使用完毕后，finally 块确保关闭连接
    """
    db = SessionLocal()
    try:
        yield db  # 将会话提供给依赖注入的函数使用
    finally:
        db.close()  # 确保会话关闭，释放数据库连接
