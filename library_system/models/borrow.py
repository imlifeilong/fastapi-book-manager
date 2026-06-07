"""
借阅模型模块

定义借阅相关的数据库模型：
- BorrowStatus: 借阅状态枚举
- BorrowRecord: 借阅记录表模型

表结构：
- borrow_records: 存储借阅记录信息
"""

# 导入 SQLAlchemy 组件
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class BorrowStatus(str, enum.Enum):
    """
    借阅状态枚举类
    
    定义借阅记录的四种状态：
    - BORROWED: 借阅中（初始状态）
    - RETURNED: 已归还（用户归还后）
    - OVERDUE: 逾期（超过归还日期未归还）
    - RENEWED: 已续借（用户续借后）
    """
    BORROWED = "borrowed"       # 借阅中
    RETURNED = "returned"       # 已归还
    OVERDUE = "overdue"         # 逾期
    RENEWED = "renewed"         # 已续借


class BorrowRecord(Base):
    """
    借阅记录表模型
    
    映射数据库中的 borrow_records 表，存储借阅记录信息
    
    字段说明：
        id: 主键，自增
        user_id: 用户 ID（外键，关联 users 表）
        book_id: 图书 ID（外键，关联 books 表）
        borrow_date: 借阅日期（默认当前时间）
        due_date: 应还日期（必填）
        return_date: 实际归还日期（可选，归还后填充）
        status: 借阅状态（默认 BORROWED）
        renew_count: 续借次数（默认 0，最多 2 次）
        fine_amount: 罚款金额（单位：分，默认 0）
        notes: 备注（可选，归还时填写）
    
    关系：
        user: 关联用户（多对一）
        book: 关联图书（多对一）
    """
    __tablename__ = "borrow_records"

    # 主键字段
    id = Column(Integer, primary_key=True, index=True)
    
    # 外键字段
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    # 日期字段
    borrow_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    
    # 状态和计数
    status = Column(Enum(BorrowStatus), default=BorrowStatus.BORROWED)
    renew_count = Column(Integer, default=0)  # 续借次数
    
    # 罚款和备注
    fine_amount = Column(Integer, default=0)  # 罚款金额（分）
    notes = Column(Text)

    # 关系定义（多对一）
    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")
