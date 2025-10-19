from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    full_name: Optional[str] = Field(None, max_length=100, example="John Doe")


class UserCreate(UserBase):
    """创建用户的请求模型"""
    password: str = Field(..., min_length=6, max_length=100, example="securepassword123")


class UserUpdate(BaseModel):
    """更新用户的请求模型"""
    email: Optional[EmailStr] = Field(None, example="new_email@example.com")
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="new_username")
    full_name: Optional[str] = Field(None, max_length=100, example="New Name")
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """响应模型（不包含密码哈希）"""
    pass
