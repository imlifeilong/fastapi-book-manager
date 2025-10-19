from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token载荷模型"""
    sub: Optional[int] = None  # 用户ID
