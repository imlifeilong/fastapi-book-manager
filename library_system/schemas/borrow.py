"""
借阅记录相关的数据验证模式（Pydantic 模型）

定义借阅数据的请求和响应结构：
- BorrowRecordBase: 借阅记录基础字段
- BorrowCreate: 借阅请求结构
- BorrowReturn: 归还请求结构
- BorrowRenew: 续借请求结构
- BorrowRecordResponse: 借阅记录响应结构
- BorrowRecordDetail: 借阅记录详情响应结构（含图书和用户信息）
- BorrowStatistics: 借阅统计响应结构

技术要点：
- 使用 Pydantic 进行数据验证
- 支持嵌套模型和枚举类型
"""

# 导入 Pydantic 组件
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

# 导入枚举类型
from models.borrow import BorrowStatus


class BorrowRecordBase(BaseModel):
    """
    借阅记录基础字段模型
    
    包含借阅记录的核心关联字段
    """
    book_id: int
    user_id: int


class BorrowCreate(BaseModel):
    """
    借阅请求模型
    
    用户借阅图书时提交的数据
    
    字段约束：
        book_id: 必须提供
        days: 借阅天数（1-90天，默认30天）
    """
    book_id: int
    days: int = Field(default=30, ge=1, le=90)  # 默认借阅30天


class BorrowReturn(BaseModel):
    """
    归还请求模型
    
    用户归还图书时提交的数据
    
    字段：
        record_id: 借阅记录 ID
        notes: 备注（可选，如图书损坏情况）
    """
    record_id: int
    notes: Optional[str] = None


class BorrowRenew(BaseModel):
    """
    续借请求模型
    
    用户续借图书时提交的数据
    
    字段约束：
        record_id: 借阅记录 ID
        days: 续借天数（1-30天，默认15天）
    """
    record_id: int
    days: int = Field(default=15, ge=1, le=30)  # 续借天数


class BorrowRecordResponse(BaseModel):
    """
    借阅记录响应模型
    
    返回借阅记录的基本信息
    
    Config.from_attributes = True: 
        允许从 SQLAlchemy ORM 模型自动转换
    """
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: BorrowStatus
    renew_count: int
    fine_amount: int
    notes: Optional[str]

    class Config:
        from_attributes = True


class BorrowRecordDetail(BorrowRecordResponse):
    """
    借阅记录详情响应模型
    
    在 BorrowRecordResponse 基础上增加图书和用户信息
    
    用于返回更详细的借阅记录，包含关联的图书和用户数据
    """
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class BorrowStatistics(BaseModel):
    """
    借阅统计响应模型
    
    返回借阅系统的统计数据
    
    字段说明：
        total_borrows: 总借阅次数
        active_borrows: 当前活跃借阅数
        overdue_count: 逾期借阅数
        total_fines: 总罚款金额（单位：分）
    """
    total_borrows: int
    active_borrows: int
    overdue_count: int
    total_fines: int
