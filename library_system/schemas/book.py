"""图书相关的数据验证模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    publish_year: Optional[int] = Field(None, ge=1000, le=2100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    total_copies: int = Field(default=1, ge=1)
    location: Optional[str] = Field(None, max_length=50)
    cover_image: Optional[str] = Field(None, max_length=255)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    publish_year: Optional[int] = Field(None, ge=1000, le=2100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    total_copies: Optional[int] = Field(None, ge=1)
    location: Optional[str] = Field(None, max_length=50)
    cover_image: Optional[str] = Field(None, max_length=255)


class BookResponse(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookSearch(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    available_only: Optional[bool] = False
