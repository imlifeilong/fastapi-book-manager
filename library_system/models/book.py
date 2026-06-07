"""
图书模型模块

定义图书相关的数据库模型：
- Book: 图书表模型

表结构：
- books: 存储图书信息
"""

# 导入 SQLAlchemy 组件
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Book(Base):
    """
    图书表模型
    
    映射数据库中的 books 表，存储图书信息
    
    字段说明：
        id: 主键，自增
        isbn: ISBN 号（唯一）
        title: 书名
        author: 作者
        publisher: 出版社（可选）
        publish_year: 出版年份（可选）
        category: 分类（可选）
        description: 简介（可选，长文本）
        total_copies: 总数量（默认 1）
        available_copies: 可用数量（默认 1）
        location: 书架位置（可选）
        cover_image: 封面图片路径（可选）
        created_at: 创建时间
        updated_at: 更新时间
    
    关系：
        borrow_records: 关联借阅记录（一对多）
    
    索引：
        idx_book_title_author: 书名和作者联合索引（优化搜索性能）
    """
    __tablename__ = "books"

    # 主键字段
    id = Column(Integer, primary_key=True, index=True)
    
    # 图书基本信息
    isbn = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    publisher = Column(String(100))
    publish_year = Column(Integer)
    category = Column(String(50), index=True)
    description = Column(Text)
    
    # 库存管理
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    
    # 其他信息
    location = Column(String(50))  # 书架位置，如 "A区-01排-05号"
    cover_image = Column(String(255))  # 封面图片相对路径
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系定义（一对多：一本图书可以有多个借阅记录）
    borrow_records = relationship("BorrowRecord", back_populates="book")

    # 联合索引：优化按书名和作者的搜索
    __table_args__ = (
        Index('idx_book_title_author', 'title', 'author'),
    )
