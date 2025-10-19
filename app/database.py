from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import asyncio

# 异步 SQLite 数据库 URL (使用 aiosqlite)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./bookstore.db"

# 创建异步数据库引擎
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # 生产环境应设为 False
    future=True
)

# 创建异步会话本地类
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# 声明基类
Base = declarative_base()


async def get_db():
    """
    获取数据库会话的异步依赖函数
    使用 async with 确保会话正确关闭
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def create_tables():
    """异步创建所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully")


async def drop_tables():
    """异步删除所有数据库表（用于测试）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Database tables dropped successfully")
