"""
用户模型模块

定义用户相关的数据库模型：
- UserRole: 用户角色枚举（管理员、图书管理员、读者）
- User: 用户表模型

表结构：
- users: 存储用户信息
"""

# 导入 SQLAlchemy 组件
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    """
    用户角色枚举类
    
    定义系统中的三种角色：
    - ADMIN: 系统管理员（最高权限）
    - LIBRARIAN: 图书管理员（管理图书和借阅）
    - READER: 普通读者（只能借阅图书）
    """
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    READER = "reader"


class User(Base):
    """
    用户表模型
    
    映射数据库中的 users 表，存储用户信息
    
    字段说明：
        id: 主键，自增
        username: 用户名（唯一）
        email: 邮箱（唯一）
        hashed_password: 密码哈希值
        full_name: 全名（可选）
        role: 用户角色（默认 READER）
        is_active: 是否活跃（默认 True，用于软删除）
        created_at: 创建时间
        updated_at: 更新时间
    
    关系：
        borrow_records: 关联借阅记录（一对多）
    """
    __tablename__ = "users"

    # 主键字段
    id = Column(Integer, primary_key=True, index=True)
    
    # 用户基本信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    
    # 权限相关
    role = Column(Enum(UserRole), default=UserRole.READER)
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系定义（一对多：一个用户可以有多个借阅记录）
    borrow_records = relationship("BorrowRecord", back_populates="user")
