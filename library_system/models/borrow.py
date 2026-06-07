from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class BorrowStatus(str, enum.Enum):
    BORROWED = "borrowed"       # 借阅中
    RETURNED = "returned"       # 已归还
    OVERDUE = "overdue"         # 逾期
    RENEWED = "renewed"         # 已续借


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    borrow_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    status = Column(Enum(BorrowStatus), default=BorrowStatus.BORROWED)
    renew_count = Column(Integer, default=0)  # 续借次数
    fine_amount = Column(Integer, default=0)  # 罚款金额（分）
    notes = Column(Text)

    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")
