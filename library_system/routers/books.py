"""图书管理路由"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models.user import User
from models.book import Book
from schemas.book import BookCreate, BookUpdate, BookResponse, BookSearch
from utils.auth import get_current_active_user, require_role

router = APIRouter(prefix="/books", tags=["图书管理"])

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "covers")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 封面图片最大尺寸
MAX_WIDTH = 400
MAX_HEIGHT = 560  # 保持 1:1.4 的图书封面比例


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """添加新图书（管理员/图书管理员权限）"""
    # 检查ISBN是否已存在
    db_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN已存在")

    db_book = Book(**book.dict())
    db_book.available_copies = book.total_copies
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.post("/upload-cover")
def upload_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """上传图书封面图片，返回可访问的URL路径"""
    # 校验文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/gif/webp 格式的图片")

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # 读取图片并进行压缩优化
    try:
        from PIL import Image
        import io

        # 读取图片
        image_data = file.file.read()
        img = Image.open(io.BytesIO(image_data))

        # 获取原始尺寸
        width, height = img.size

        # 计算缩放比例，保持宽高比
        scale = min(MAX_WIDTH / width, MAX_HEIGHT / height)

        # 如果图片小于最大尺寸，不缩放
        if scale >= 1:
            img.save(filepath, quality=95)
        else:
            # 计算新尺寸
            new_width = int(width * scale)
            new_height = int(height * scale)

            # 使用高质量缩放算法
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # 保存压缩后的图片
            img.save(filepath, quality=90)

    except ImportError:
        # 如果没有安装PIL，直接保存原始文件
        import shutil
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")

    # 返回相对路径（前端通过 /api/v1/books/covers/{filename} 访问）
    return {"url": f"/api/v1/books/covers/{filename}"}


@router.get("/covers/{filename}")
def get_cover(filename: str):
    """获取图书封面图片"""
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(filepath)


@router.get("", response_model=List[BookResponse])
def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    available_only: bool = False,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取图书列表，支持搜索和筛选"""
    query = db.query(Book)

    if category:
        query = query.filter(Book.category == category)

    if available_only:
        query = query.filter(Book.available_copies > 0)

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            or_(
                Book.title.like(search),
                Book.author.like(search),
                Book.isbn.like(search)
            )
        )

    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/search", response_model=List[BookResponse])
def search_books(
    q: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = None,
    author: Optional[str] = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """高级图书搜索"""
    query = db.query(Book)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                Book.title.like(search),
                Book.author.like(search),
                Book.isbn.like(search),
                Book.description.like(search)
            )
        )

    if category:
        query = query.filter(Book.category == category)

    if author:
        query = query.filter(Book.author.like(f"%{author}%"))

    if available_only:
        query = query.filter(Book.available_copies > 0)

    return query.all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取图书详情"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """更新图书信息（管理员/图书管理员权限）"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    update_data = book_update.dict(exclude_unset=True)

    # 如果更新了总数量，需要同步更新可用数量
    if 'total_copies' in update_data:
        diff = update_data['total_copies'] - book.total_copies
        book.available_copies += diff

    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """删除图书（仅管理员）"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 检查是否有未归还的借阅记录
    active_borrows = [b for b in book.borrow_records if b.status.value in ['borrowed', 'overdue', 'renewed']]
    if active_borrows:
        raise HTTPException(status_code=400, detail="该图书有未归还记录，无法删除")

    # 删除封面图片
    if book.cover_image:
        cover_filename = os.path.basename(book.cover_image)
        cover_path = os.path.join(UPLOAD_DIR, cover_filename)
        if os.path.exists(cover_path):
            os.remove(cover_path)

    db.delete(book)
    db.commit()
    return None
