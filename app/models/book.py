from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Book(Base):
    """
    图书模型
    """
    __tablename__ = "books"
    __table_args__ = {'extend_existing': True}

    bid = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    author = Column(String(100), index=True, nullable=False)
    image_url = Column(String(500), nullable=True)  # 图片URL字段
    description = Column(Text, default="")
    publication_year = Column(Integer)
    isbn = Column(String(20), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 外键关联用户
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # 定义与用户的关系
    owner = relationship("User", back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
