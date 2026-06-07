"""
图书管理路由模块

提供图书的 CRUD 操作和封面上传功能：
- POST /api/v1/books: 添加图书（管理员/图书管理员）
- POST /api/v1/books/upload-cover: 上传封面图片
- GET /api/v1/books/covers/{filename}: 获取封面图片
- GET /api/v1/books: 获取图书列表（支持筛选和搜索）
- GET /api/v1/books/search: 高级搜索
- GET /api/v1/books/{book_id}: 获取图书详情
- PUT /api/v1/books/{book_id}: 更新图书信息（管理员/图书管理员）
- DELETE /api/v1/books/{book_id}: 删除图书（仅管理员）

技术要点：
- 文件上传使用 UploadFile
- 图片处理使用 PIL 进行压缩
- SQLAlchemy 查询支持复杂条件筛选
"""

# 导入标准库
import os
import uuid
from typing import List, Optional

# 导入 FastAPI 组件
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

# 导入项目模块
from database import get_db
from models.user import User
from models.book import Book
from schemas.book import BookCreate, BookUpdate, BookResponse, BookSearch
from utils.auth import get_current_active_user, require_role

# 创建 APIRouter 实例
router = APIRouter(prefix="/books", tags=["图书管理"])

# 配置上传目录
# 计算上传目录路径：项目根目录 /uploads/covers
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "covers")
# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 封面图片最大尺寸配置
MAX_WIDTH = 400
MAX_HEIGHT = 560  # 保持 1:1.4 的图书封面比例


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """
    添加新图书（管理员/图书管理员权限）
    
    请求体：
        isbn: ISBN 号（唯一）
        title: 书名
        author: 作者
        publisher: 出版社（可选）
        publish_year: 出版年份（可选）
        category: 分类（可选）
        description: 简介（可选）
        total_copies: 总数量（默认 1）
        location: 书架位置（可选）
        cover_image: 封面图片路径（可选）
    
    返回：
        BookResponse: 创建的图书信息
    
    异常：
        HTTPException(400): ISBN 已存在
        HTTPException(403): 权限不足
    """
    # 检查 ISBN 是否已存在
    db_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN已存在")

    # 创建图书对象
    db_book = Book(**book.dict())
    # 初始化可用数量等于总数量
    db_book.available_copies = book.total_copies
    
    # 添加到数据库
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return db_book


@router.post("/upload-cover")
def upload_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """
    上传图书封面图片，返回可访问的 URL 路径
    
    请求体：
        file: 图片文件（支持 jpg/png/gif/webp）
    
    返回：
        {"url": "/api/v1/books/covers/{filename}"}
    
    异常：
        HTTPException(400): 不支持的文件格式
        HTTPException(500): 图片处理失败
    """
    # 校验文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/gif/webp 格式的图片")

    # 生成唯一文件名（使用 UUID 避免冲突）
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext:
        ext = ".jpg"  # 默认使用 jpg 格式
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # 读取图片并进行压缩优化
    try:
        from PIL import Image
        import io

        # 读取图片数据
        image_data = file.file.read()
        img = Image.open(io.BytesIO(image_data))

        # 获取原始尺寸
        width, height = img.size

        # 计算缩放比例（保持宽高比）
        scale = min(MAX_WIDTH / width, MAX_HEIGHT / height)

        # 如果图片小于最大尺寸，直接保存
        if scale >= 1:
            img.save(filepath, quality=95)
        else:
            # 计算新尺寸
            new_width = int(width * scale)
            new_height = int(height * scale)

            # 使用高质量缩放算法（LANCZOS）
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # 保存压缩后的图片
            img.save(filepath, quality=90)

    except ImportError:
        # 如果没有安装 PIL，直接保存原始文件
        import shutil
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")

    # 返回相对路径（前端通过此 URL 访问图片）
    return {"url": f"/api/v1/books/covers/{filename}"}


@router.get("/covers/{filename}")
def get_cover(filename: str):
    """
    获取图书封面图片
    
    路径参数：
        filename: 图片文件名
    
    返回：
        FileResponse: 图片文件
    
    异常：
        HTTPException(404): 图片不存在
    """
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
    """
    获取图书列表，支持搜索和筛选
    
    查询参数：
        skip: 跳过条数（默认 0）
        limit: 每页条数（默认 10，范围 1-100）
        category: 按分类筛选（可选）
        available_only: 是否只显示有库存的图书（默认 False）
        keyword: 搜索关键词（匹配书名、作者、ISBN）
    
    返回：
        List[BookResponse]: 图书列表
    """
    # 构建查询对象
    query = db.query(Book)

    # 按分类筛选
    if category:
        query = query.filter(Book.category == category)

    # 只显示有库存的图书
    if available_only:
        query = query.filter(Book.available_copies > 0)

    # 关键词搜索（模糊匹配书名、作者、ISBN）
    if keyword:
        search = f"%{keyword}%"  # SQL LIKE 通配符
        query = query.filter(
            or_(
                Book.title.like(search),
                Book.author.like(search),
                Book.isbn.like(search)
            )
        )

    # 分页查询
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
    """
    高级图书搜索
    
    查询参数：
        q: 综合搜索关键词（匹配书名、作者、ISBN、简介）
        category: 按分类筛选
        author: 按作者筛选
        available_only: 是否只显示有库存的图书
    
    返回：
        List[BookResponse]: 匹配的图书列表
    """
    query = db.query(Book)

    # 综合搜索
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

    # 按分类筛选
    if category:
        query = query.filter(Book.category == category)

    # 按作者筛选（模糊匹配）
    if author:
        query = query.filter(Book.author.like(f"%{author}%"))

    # 只显示有库存的图书
    if available_only:
        query = query.filter(Book.available_copies > 0)

    return query.all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取图书详情
    
    路径参数：
        book_id: 图书 ID
    
    返回：
        BookResponse: 图书详细信息
    
    异常：
        HTTPException(404): 图书不存在
    """
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
    """
    更新图书信息（管理员/图书管理员权限）
    
    路径参数：
        book_id: 图书 ID
    
    请求体：
        可选字段：title, author, publisher, publish_year, category, 
                  description, total_copies, location, cover_image
    
    返回：
        BookResponse: 更新后的图书信息
    
    异常：
        HTTPException(404): 图书不存在
        HTTPException(403): 权限不足
    """
    # 查询图书
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 获取更新数据（只包含传入的字段）
    update_data = book_update.dict(exclude_unset=True)

    # 如果更新了总数量，同步更新可用数量
    if 'total_copies' in update_data:
        diff = update_data['total_copies'] - book.total_copies
        book.available_copies += diff

    # 应用更新
    for field, value in update_data.items():
        setattr(book, field, value)

    # 提交事务
    db.commit()
    db.refresh(book)
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    删除图书（仅管理员）
    
    路径参数：
        book_id: 图书 ID
    
    返回：
        204 No Content
    
    异常：
        HTTPException(404): 图书不存在
        HTTPException(400): 该图书有未归还记录
        HTTPException(403): 权限不足
    """
    # 查询图书
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 检查是否有未归还的借阅记录
    active_borrows = [b for b in book.borrow_records if b.status.value in ['borrowed', 'overdue', 'renewed']]
    if active_borrows:
        raise HTTPException(status_code=400, detail="该图书有未归还记录，无法删除")

    # 删除封面图片（如果存在）
    if book.cover_image:
        cover_filename = os.path.basename(book.cover_image)
        cover_path = os.path.join(UPLOAD_DIR, cover_filename)
        if os.path.exists(cover_path):
            os.remove(cover_path)

    # 删除图书记录
    db.delete(book)
    db.commit()
    
    # 返回 None，状态码 204
    return None
