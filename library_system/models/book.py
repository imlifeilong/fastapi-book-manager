from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    publisher = Column(String(100))
    publish_year = Column(Integer)
    category = Column(String(50), index=True)
    description = Column(Text)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    location = Column(String(50))  # 书架位置
    cover_image = Column(String(255))  # 图书封面图片路径
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    borrow_records = relationship("BorrowRecord", back_populates="book")

    __table_args__ = (
        Index('idx_book_title_author', 'title', 'author'),
    )
