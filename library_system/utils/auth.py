"""
认证相关工具函数模块

包含以下功能：
- 密码哈希与验证
- JWT 令牌生成与解析
- OAuth2 认证流程
- 角色权限检查

技术要点：
- 使用 passlib 进行密码加密（bcrypt 算法）
- 使用 jose 进行 JWT 令牌操作
- 使用 FastAPI 依赖注入实现认证中间件
"""

# 导入标准库
from datetime import datetime, timedelta
from typing import Optional

# 导入第三方库
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 导入项目模块
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import TokenData

# ==================== 配置常量 ====================

# JWT 密钥（生产环境应从环境变量获取）
SECRET_KEY = "your-secret-key-here-change-in-production"

# JWT 算法（HS256: HMAC SHA-256）
ALGORITHM = "HS256"

# 访问令牌过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==================== 密码处理 ====================

# 创建密码上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    参数：
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的哈希密码
    
    返回：
        bool: 密码匹配返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码的哈希值
    
    参数：
        password: 明文密码
    
    返回：
        str: 哈希后的密码字符串
    """
    return pwd_context.hash(password)

# ==================== JWT 令牌操作 ====================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建 JWT 访问令牌
    
    参数：
        data: 要编码到令牌中的数据（如用户名）
        expires_delta: 过期时间间隔（可选）
    
    返回：
        str: 编码后的 JWT 令牌字符串
    """
    # 复制数据以避免修改原字典
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加过期时间到数据中
    to_encode.update({"exp": expire})
    
    # 编码生成 JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==================== OAuth2 认证流程 ====================

# 创建 OAuth2 密码流的令牌 URL
# 用户通过 POST /api/v1/auth/login 获取令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    
    作为依赖函数，自动从请求头中提取并验证 JWT 令牌，然后查询用户
    
    参数：
        token: 从 Authorization 头获取的 Bearer 令牌
        db: 数据库会话
    
    返回：
        User: 当前登录用户对象
    
    异常：
        HTTPException(401): 令牌无效或用户不存在
    """
    # 定义凭据验证失败的异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码 JWT 令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 从 payload 中获取用户名
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # 创建 TokenData 对象
        token_data = TokenData(username=username)
    except JWTError:
        # JWT 解码失败（签名无效、过期等）
        raise credentials_exception
    
    # 根据用户名查询用户
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    
    在 get_current_user 的基础上，额外检查用户是否被禁用
    
    参数：
        current_user: 通过 get_current_user 获取的用户对象
    
    返回：
        User: 活跃用户对象
    
    异常：
        HTTPException(400): 用户已被禁用
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

# ==================== 角色权限检查 ====================


def require_role(*roles):
    """
    角色权限检查装饰器工厂函数
    
    用于限制接口只能被特定角色的用户访问
    
    使用方式：
        @router.get("/admin-only")
        def admin_function(current_user: User = Depends(require_role("admin"))):
            pass
    
    参数：
        *roles: 允许访问的角色列表（如 "admin", "librarian"）
    
    返回：
        依赖函数，检查用户角色是否在允许列表中
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        # 检查用户角色是否在允许的角色列表中
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker
