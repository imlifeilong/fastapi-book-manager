from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional

from models.book import Book
from schemas.book import BookCreate, BookUpdate


def get_book(db: Session, book_id: int, owner_id: int) -> Optional[Book]:
    """根据ID获取用户的图书"""
    return db.query(Book).filter(Book.id == book_id, Book.owner_id == owner_id).first()


def get_books(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Book]:
    """获取用户的所有图书（分页）"""
    return db.query(Book).filter(Book.owner_id == owner_id).offset(skip).limit(limit).all()


def create_book(db: Session, book_create: BookCreate, owner_id: int) -> Book:
    """创建新图书"""
    # 检查ISBN是否已存在（如果提供了ISBN）
    if book_create.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book_create.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )

    # 创建图书对象
    db_book = Book(**book_create.model_dump(), owner_id=owner_id)

    # 保存到数据库
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book_update: BookUpdate, owner_id: int) -> Optional[Book]:
    """更新图书信息"""
    db_book = get_book(db, book_id, owner_id)
    if not db_book:
        return None

    # 更新字段
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)

    # 保存更改
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int, owner_id: int) -> bool:
    """删除图书"""
    db_book = get_book(db, book_id, owner_id)
    if not db_book:
        return False

    db.delete(db_book)
    db.commit()
    return True


def search_books(db: Session, owner_id: int, query: str, skip: int = 0, limit: int = 100) -> List[Book]:
    """搜索图书（按标题或作者）"""
    search_pattern = f"%{query}%"
    return db.query(Book).filter(
        Book.owner_id == owner_id,
        or_(
            Book.title.ilike(search_pattern),
            Book.author.ilike(search_pattern)
        )
    ).offset(skip).limit(limit).all()
