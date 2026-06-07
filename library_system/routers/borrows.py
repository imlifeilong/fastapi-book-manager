"""借阅管理路由"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User
from models.book import Book
from models.borrow import BorrowRecord, BorrowStatus
from schemas.borrow import (
    BorrowCreate, BorrowReturn, BorrowRenew,
    BorrowRecordResponse, BorrowRecordDetail, BorrowStatistics
)
from utils.auth import get_current_active_user, require_role

router = APIRouter(prefix="/borrows", tags=["借阅管理"])


def check_overdue(record: BorrowRecord) -> bool:
    """检查借阅是否逾期"""
    if record.status in [BorrowStatus.BORROWED, BorrowStatus.RENEWED]:
        if datetime.now() > record.due_date:
            return True
    return False


def calculate_fine(record: BorrowRecord) -> int:
    """计算逾期罚款（每天1元，单位：分）"""
    if record.status not in [BorrowStatus.BORROWED, BorrowStatus.RENEWED, BorrowStatus.OVERDUE]:
        return 0

    if datetime.now() <= record.due_date:
        return 0

    overdue_days = (datetime.now() - record.due_date).days
    return max(0, overdue_days * 100)  # 每天1元 = 100分


@router.post("/borrow", response_model=BorrowRecordResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(
    borrow_data: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """借阅图书"""
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 检查是否有可用副本
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="该图书暂无可用副本")

    # 检查用户是否有逾期未还图书
    overdue_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.RENEWED])
    ).all()

    for record in overdue_borrows:
        if check_overdue(record):
            raise HTTPException(status_code=400, detail="您有逾期未还的图书，请先归还")

    # 检查用户是否已借阅该图书
    existing = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.book_id == borrow_data.book_id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.RENEWED])
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="您已借阅该图书，请勿重复借阅")

    # 创建借阅记录
    due_date = datetime.now() + timedelta(days=borrow_data.days)
    borrow_record = BorrowRecord(
        user_id=current_user.id,
        book_id=borrow_data.book_id,
        due_date=due_date,
        status=BorrowStatus.BORROWED
    )

    # 减少可用副本
    book.available_copies -= 1

    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)
    return borrow_record


@router.post("/return", response_model=BorrowRecordResponse)
def return_book(
    return_data: BorrowReturn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """归还图书"""
    record = db.query(BorrowRecord).filter(BorrowRecord.id == return_data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")

    # 检查权限：只能归还自己的图书，管理员可以归还任何图书
    if record.user_id != current_user.id and current_user.role.value not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="无权操作此借阅记录")

    if record.status not in [BorrowStatus.BORROWED, BorrowStatus.RENEWED, BorrowStatus.OVERDUE]:
        raise HTTPException(status_code=400, detail="该图书已归还")

    # 更新借阅记录
    record.return_date = datetime.now()
    record.status = BorrowStatus.RETURNED
    record.notes = return_data.notes

    # 计算罚款
    record.fine_amount = calculate_fine(record)

    # 增加可用副本
    book = db.query(Book).filter(Book.id == record.book_id).first()
    book.available_copies += 1

    db.commit()
    db.refresh(record)
    return record


@router.post("/renew", response_model=BorrowRecordResponse)
def renew_book(
    renew_data: BorrowRenew,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """续借图书"""
    record = db.query(BorrowRecord).filter(BorrowRecord.id == renew_data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")

    # 检查权限
    if record.user_id != current_user.id and current_user.role.value not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="无权操作此借阅记录")

    if record.status not in [BorrowStatus.BORROWED, BorrowStatus.RENEWED]:
        raise HTTPException(status_code=400, detail="该图书无法续借")

    # 检查是否已逾期
    if check_overdue(record):
        raise HTTPException(status_code=400, detail="图书已逾期，请先归还")

    # 检查续借次数限制（最多续借2次）
    if record.renew_count >= 2:
        raise HTTPException(status_code=400, detail="已达到最大续借次数")

    # 更新截止日期
    record.due_date = record.due_date + timedelta(days=renew_data.days)
    record.renew_count += 1
    record.status = BorrowStatus.RENEWED

    db.commit()
    db.refresh(record)
    return record


@router.get("/my-borrows", response_model=List[BorrowRecordDetail])
def get_my_borrows(
    status: Optional[BorrowStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的借阅记录"""
    query = db.query(BorrowRecord).filter(BorrowRecord.user_id == current_user.id)

    if status:
        query = query.filter(BorrowRecord.status == status)

    records = query.order_by(BorrowRecord.borrow_date.desc()).all()

    # 补充图书和用户信息
    result = []
    for record in records:
        book = db.query(Book).filter(Book.id == record.book_id).first()
        detail = BorrowRecordDetail(
            id=record.id,
            user_id=record.user_id,
            book_id=record.book_id,
            borrow_date=record.borrow_date,
            due_date=record.due_date,
            return_date=record.return_date,
            status=record.status,
            renew_count=record.renew_count,
            fine_amount=calculate_fine(record),
            notes=record.notes,
            book_title=book.title if book else None,
            book_author=book.author if book else None,
            user_name=current_user.username,
            user_email=current_user.email
        )
        result.append(detail)

    return result


@router.get("/all", response_model=List[BorrowRecordDetail])
def get_all_borrows(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[BorrowStatus] = None,
    user_id: Optional[int] = None,
    book_id: Optional[int] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """获取所有借阅记录（管理员/图书管理员权限）"""
    query = db.query(BorrowRecord)

    if status:
        query = query.filter(BorrowRecord.status == status)
    if user_id:
        query = query.filter(BorrowRecord.user_id == user_id)
    if book_id:
        query = query.filter(BorrowRecord.book_id == book_id)

    # SQLAlchemy 要求必须先排序（order_by()），再分页（offset()/limit()），否则会引发 InvalidRequestError。
    records = query.order_by(BorrowRecord.borrow_date.desc()).offset(skip).limit(limit).all()

    result = []
    for record in records:
        book = db.query(Book).filter(Book.id == record.book_id).first()
        user = db.query(User).filter(User.id == record.user_id).first()

        # 逾期检查
        if overdue_only and not check_overdue(record):
            continue

        detail = BorrowRecordDetail(
            id=record.id,
            user_id=record.user_id,
            book_id=record.book_id,
            borrow_date=record.borrow_date,
            due_date=record.due_date,
            return_date=record.return_date,
            status=BorrowStatus.OVERDUE if check_overdue(record) else record.status,
            renew_count=record.renew_count,
            fine_amount=calculate_fine(record),
            notes=record.notes,
            book_title=book.title if book else None,
            book_author=book.author if book else None,
            user_name=user.username if user else None,
            user_email=user.email if user else None
        )
        result.append(detail)

    return result


@router.get("/statistics", response_model=BorrowStatistics)
def get_borrow_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """获取借阅统计信息"""
    total = db.query(BorrowRecord).count()
    active = db.query(BorrowRecord).filter(
        BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.RENEWED])
    ).count()

    # 计算逾期数量
    all_active = db.query(BorrowRecord).filter(
        BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.RENEWED])
    ).all()
    overdue_count = sum(1 for r in all_active if check_overdue(r))

    # 计算总罚款
    total_fines = sum(calculate_fine(r) for r in db.query(BorrowRecord).all())

    return BorrowStatistics(
        total_borrows=total,
        active_borrows=active,
        overdue_count=overdue_count,
        total_fines=total_fines
    )


@router.post("/check-overdue")
def check_all_overdue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """检查所有借阅记录，标记逾期状态"""
    active_records = db.query(BorrowRecord).filter(
        BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.RENEWED])
    ).all()

    updated_count = 0
    for record in active_records:
        if check_overdue(record):
            record.status = BorrowStatus.OVERDUE
            updated_count += 1

    db.commit()
    return {"message": f"已更新 {updated_count} 条逾期记录"}
