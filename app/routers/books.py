from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.book import Book, BookCreate, BookUpdate
from app.schemas.user import User
from app.crud.book import get_book, get_books, create_book, update_book, delete_book, search_books
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[Book])
def read_books(
        skip: int = Query(0, ge=0, description="跳过的记录数"),
        limit: int = Query(100, ge=1, le=1000, description="返回的最大记录数"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的所有图书（分页）"""
    books = get_books(db, owner_id=current_user.id, skip=skip, limit=limit)
    return books


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_new_book(
        book: BookCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """创建新图书"""
    return create_book(db, book, current_user.id)


@router.get("/{book_id}", response_model=Book)
def read_book(
        book_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """根据ID获取图书详情"""
    db_book = get_book(db, book_id, current_user.id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return db_book


@router.put("/{book_id}", response_model=Book)
def update_book_info(
        book_id: int,
        book_update: BookUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """更新图书信息"""
    db_book = update_book(db, book_id, book_update, current_user.id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(
        book_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """删除图书"""
    if not delete_book(db, book_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )


@router.get("/search/", response_model=List[Book])
def search_books_by_query(
        query: str = Query(..., min_length=1, max_length=100, description="搜索关键词（标题或作者）"),
        skip: int = Query(0, ge=0, description="跳过的记录数"),
        limit: int = Query(100, ge=1, le=1000, description="返回的最大记录数"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """搜索图书（按标题或作者）"""
    books = search_books(db, current_user.id, query, skip, limit)
    return books
