"""
借阅管理路由模块

提供图书借阅、归还、续借等功能：
- POST /api/v1/borrows/borrow: 借阅图书
- POST /api/v1/borrows/return: 归还图书
- POST /api/v1/borrows/renew: 续借图书
- GET /api/v1/borrows/my-borrows: 获取当前用户的借阅记录
- GET /api/v1/borrows/all: 获取所有借阅记录（管理员/图书管理员）
- GET /api/v1/borrows/statistics: 获取借阅统计信息（管理员/图书管理员）
- POST /api/v1/borrows/check-overdue: 检查并标记逾期记录（管理员/图书管理员）

技术要点：
- 逾期检查和罚款计算逻辑
- 续借次数限制（最多2次）
- 权限验证（管理员可操作所有记录）
"""

# 导入标准库
from typing import List, Optional
from datetime import datetime, timedelta

# 导入 FastAPI 组件
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

# 导入项目模块
from database import get_db
from models.user import User
from models.book import Book
from models.borrow import BorrowRecord, BorrowStatus
from schemas.borrow import (
    BorrowCreate, BorrowReturn, BorrowRenew,
    BorrowRecordResponse, BorrowRecordDetail, BorrowStatistics
)
from utils.auth import get_current_active_user, require_role

# 创建 APIRouter 实例
router = APIRouter(prefix="/borrows", tags=["借阅管理"])


def check_overdue(record: BorrowRecord) -> bool:
    """
    检查借阅是否逾期
    
    参数：
        record: 借阅记录对象
    
    返回：
        bool: 逾期返回 True，否则返回 False
    """
    if record.status in [BorrowStatus.BORROWED, BorrowStatus.RENEWED]:
        if datetime.now() > record.due_date:
            return True
    return False


def calculate_fine(record: BorrowRecord) -> int:
    """
    计算逾期罚款（每天1元，单位：分）
    
    参数：
        record: 借阅记录对象
    
    返回：
        int: 罚款金额（单位：分，1元 = 100分）
    """
    # 如果不是借阅中或续借状态，罚款为0
    if record.status not in [BorrowStatus.BORROWED, BorrowStatus.RENEWED, BorrowStatus.OVERDUE]:
        return 0

    # 如果未逾期，罚款为0
    if datetime.now() <= record.due_date:
        return 0

    # 计算逾期天数并计算罚款
    overdue_days = (datetime.now() - record.due_date).days
    return max(0, overdue_days * 100)  # 每天1元 = 100分


@router.post("/borrow", response_model=BorrowRecordResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(
    borrow_data: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    借阅图书
    
    请求体：
        book_id: 图书 ID
        days: 借阅天数
    
    返回：
        BorrowRecordResponse: 借阅记录
    
    异常：
        HTTPException(404): 图书不存在
        HTTPException(400): 图书无可用副本/有逾期图书/已借阅该图书
    """
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

    # 保存到数据库
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
    """
    归还图书
    
    请求体：
        record_id: 借阅记录 ID
        notes: 备注（可选）
    
    返回：
        BorrowRecordResponse: 更新后的借阅记录
    
    异常：
        HTTPException(404): 借阅记录不存在
        HTTPException(403): 无权操作此记录
        HTTPException(400): 图书已归还
    """
    # 查询借阅记录
    record = db.query(BorrowRecord).filter(BorrowRecord.id == return_data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")

    # 检查权限：只能归还自己的图书，管理员可以归还任何图书
    if record.user_id != current_user.id and current_user.role.value not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="无权操作此借阅记录")

    # 检查借阅状态
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

    # 提交事务
    db.commit()
    db.refresh(record)
    
    return record


@router.post("/renew", response_model=BorrowRecordResponse)
def renew_book(
    renew_data: BorrowRenew,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    续借图书
    
    请求体：
        record_id: 借阅记录 ID
        days: 续借天数
    
    返回：
        BorrowRecordResponse: 更新后的借阅记录
    
    异常：
        HTTPException(404): 借阅记录不存在
        HTTPException(403): 无权操作此记录
        HTTPException(400): 无法续借/已逾期/达到最大续借次数
    """
    # 查询借阅记录
    record = db.query(BorrowRecord).filter(BorrowRecord.id == renew_data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")

    # 检查权限
    if record.user_id != current_user.id and current_user.role.value not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="无权操作此借阅记录")

    # 检查借阅状态
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

    # 提交事务
    db.commit()
    db.refresh(record)
    
    return record


@router.get("/my-borrows", response_model=List[BorrowRecordDetail])
def get_my_borrows(
    status: Optional[BorrowStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的借阅记录
    
    查询参数：
        status: 按状态筛选（可选）
    
    返回：
        List[BorrowRecordDetail]: 借阅记录列表（含图书和用户信息）
    """
    # 查询当前用户的借阅记录
    query = db.query(BorrowRecord).filter(BorrowRecord.user_id == current_user.id)

    if status:
        query = query.filter(BorrowRecord.status == status)

    # 按借阅日期倒序排列
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
    """
    获取所有借阅记录（管理员/图书管理员权限）
    
    查询参数：
        skip: 跳过条数（默认 0）
        limit: 每页条数（默认 10，范围 1-100）
        status: 按状态筛选（可选）
        user_id: 按用户 ID 筛选（可选）
        book_id: 按图书 ID 筛选（可选）
        overdue_only: 是否只显示逾期记录（默认 False）
    
    返回：
        List[BorrowRecordDetail]: 借阅记录列表
    
    异常：
        HTTPException(403): 权限不足
    """
    # 构建查询对象
    query = db.query(BorrowRecord)

    # 按状态筛选
    if status:
        query = query.filter(BorrowRecord.status == status)
    
    # 按用户 ID 筛选
    if user_id:
        query = query.filter(BorrowRecord.user_id == user_id)
    
    # 按图书 ID 筛选
    if book_id:
        query = query.filter(BorrowRecord.book_id == book_id)

    # SQLAlchemy 要求必须先排序（order_by()），再分页（offset()/limit()）
    records = query.order_by(BorrowRecord.borrow_date.desc()).offset(skip).limit(limit).all()

    # 构建返回结果
    result = []
    for record in records:
        book = db.query(Book).filter(Book.id == record.book_id).first()
        user = db.query(User).filter(User.id == record.user_id).first()

        # 如果只显示逾期记录，跳过非逾期的
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
    """
    获取借阅统计信息（管理员/图书管理员权限）
    
    返回：
        BorrowStatistics: 统计数据（总借阅数、活跃借阅数、逾期数、总罚款）
    
    异常：
        HTTPException(403): 权限不足
    """
    # 总借阅记录数
    total = db.query(BorrowRecord).count()
    
    # 活跃借阅数（借阅中或续借状态）
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
    """
    检查所有借阅记录，标记逾期状态（管理员/图书管理员权限）
    
    返回：
        {"message": "已更新 X 条逾期记录"}
    
    异常：
        HTTPException(403): 权限不足
    """
    # 查询所有活跃的借阅记录
    active_records = db.query(BorrowRecord).filter(
        BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.RENEWED])
    ).all()

    # 检查并更新逾期状态
    updated_count = 0
    for record in active_records:
        if check_overdue(record):
            record.status = BorrowStatus.OVERDUE
            updated_count += 1

    # 提交事务
    db.commit()
    
    return {"message": f"已更新 {updated_count} 条逾期记录"}
