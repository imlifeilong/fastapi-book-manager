"""
认证相关路由模块

提供用户注册和登录功能：
- POST /api/v1/auth/register: 用户注册
- POST /api/v1/auth/login: 用户登录，获取 JWT 令牌

技术要点：
- 使用 OAuth2 密码流进行认证
- JWT 令牌用于后续请求的身份验证
- 密码使用 bcrypt 算法加密存储
"""

# 导入标准库
from datetime import timedelta

# 导入 FastAPI 组件
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# 导入项目模块
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token
from utils.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# 创建 APIRouter 实例
# prefix="/auth": 路由前缀，所有接口都以 /auth 开头
# tags=["认证"]: 用于文档分组显示
router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    创建新用户账号，密码会被加密存储
    
    请求体：
        username: 用户名（3-50字符）
        email: 邮箱地址（需有效格式）
        full_name: 全名（可选）
        password: 密码（6-100字符）
        role: 用户角色（可选，默认为 reader）
    
    返回：
        UserResponse: 新创建的用户信息（不含密码）
    
    异常：
        HTTPException(400): 用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已注册
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已注册")

    # 创建新用户
    # 对密码进行哈希加密
    hashed_password = get_password_hash(user.password)
    
    # 创建用户对象
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    
    # 添加到数据库会话
    db.add(db_user)
    
    # 提交事务
    db.commit()
    
    # 刷新对象，获取数据库生成的 ID 等字段
    db.refresh(db_user)
    
    # 返回用户信息（response_model 会自动过滤敏感字段）
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    
    验证用户凭据并返回 JWT 访问令牌
    
    请求体（OAuth2 标准格式）：
        username: 用户名
        password: 密码
    
    返回：
        Token: 包含 access_token 和 token_type
    
    异常：
        HTTPException(401): 用户名或密码错误
        HTTPException(400): 用户已被禁用
    """
    # 根据用户名查询用户
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 验证用户是否存在且密码正确
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},  # OAuth2 标准响应头
        )

    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")

    # 设置令牌过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 创建 JWT 访问令牌
    # 令牌中包含用户名（sub 是 JWT 标准声明）
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 返回令牌
    return {"access_token": access_token, "token_type": "bearer"}
