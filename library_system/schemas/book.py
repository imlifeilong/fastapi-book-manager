"""
图书相关的数据验证模式（Pydantic 模型）

定义图书数据的请求和响应结构：
- BookBase: 图书基础字段（创建和响应共用）
- BookCreate: 创建图书时的请求结构
- BookUpdate: 更新图书时的请求结构（所有字段可选）
- BookResponse: 返回图书信息时的响应结构
- BookSearch: 图书搜索参数结构

技术要点：
- 使用 Pydantic 进行数据验证和序列化
- Field 用于定义字段约束和默认值
- from_attributes = True 支持从 ORM 模型自动转换
"""

# 导入 Pydantic 组件
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    """
    图书基础字段模型
    
    包含图书的基本信息字段，用于创建和响应的基础结构
    
    字段约束：
        isbn: 10-20字符
        title: 1-200字符
        author: 1-100字符
        publish_year: 1000-2100
        total_copies: 至少1本
    """
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
    """
    创建图书请求模型
    
    继承自 BookBase，无需额外字段
    """
    pass


class BookUpdate(BaseModel):
    """
    更新图书请求模型
    
    所有字段均为可选，用于部分更新
    
    注意：isbn 不允许更新（唯一标识）
    """
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
    """
    图书响应模型
    
    在 BookBase 基础上增加数据库生成的字段
    
    Config.from_attributes = True: 
        允许从 SQLAlchemy ORM 模型自动转换为 Pydantic 模型
    """
    id: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookSearch(BaseModel):
    """
    图书搜索参数模型
    
    用于构建搜索查询条件
    """
    keyword: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    available_only: Optional[bool] = False
