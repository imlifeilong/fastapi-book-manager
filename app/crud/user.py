from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
import bcrypt

from app.models.user import User
from app.schemas.user import UserCreate
from app.exceptions import DuplicateEntryException


def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email, User.is_active == True).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username, User.is_active == True).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    """创建新用户"""
    # 检查邮箱是否已存在
    if get_user_by_email(db, user_create.email):
        raise DuplicateEntryException("Email already registered")

    # 检查用户名是否已存在
    if get_user_by_username(db, user_create.username):
        raise DuplicateEntryException("Username already taken")

    # 哈希密码
    hashed_password = bcrypt.hashpw(
        user_create.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # 创建用户对象
    db_user = User(
        email=user_create.email,
        username=user_create.username,
        full_name=user_create.full_name,
        hashed_password=hashed_password
    )

    # 保存到数据库
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryException("User with this email or username already exists")


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户凭据"""
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return None

    return user