from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    """图书基础模型"""
    title: str = Field(..., min_length=1, max_length=200, example="Python编程：从入门到实践")
    author: str = Field(..., min_length=1, max_length=100, example="Eric Matthes")
    description: Optional[str] = Field(None, max_length=1000, example="一本很好的Python入门书籍")
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year, example=2016)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20, example="978-7-115-42802-8")
    image_url: Optional[str] = Field(None, max_length=500, example="https://example.com/images/book1.jpg")


class BookCreate(BookBase):
    """创建图书的请求模型"""
    pass


class BookUpdate(BaseModel):
    """更新图书的请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)


class BookInDB(BookBase):
    """数据库中的图书模型"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Book(BookInDB):
    """响应模型"""
    pass
