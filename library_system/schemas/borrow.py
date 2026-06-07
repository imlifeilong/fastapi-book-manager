"""借阅记录相关的数据验证模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from models.borrow import BorrowStatus


class BorrowRecordBase(BaseModel):
    book_id: int
    user_id: int


class BorrowCreate(BaseModel):
    book_id: int
    days: int = Field(default=30, ge=1, le=90)  # 默认借阅30天


class BorrowReturn(BaseModel):
    record_id: int
    notes: Optional[str] = None


class BorrowRenew(BaseModel):
    record_id: int
    days: int = Field(default=15, ge=1, le=30)  # 续借天数


class BorrowRecordResponse(BaseModel):
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
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class BorrowStatistics(BaseModel):
    total_borrows: int
    active_borrows: int
    overdue_count: int
    total_fines: int
