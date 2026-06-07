"""
用户管理路由模块

提供用户的 CRUD 操作：
- GET /api/v1/users/me: 获取当前登录用户信息
- GET /api/v1/users: 获取用户列表（管理员/图书管理员）
- GET /api/v1/users/{user_id}: 获取指定用户信息（管理员/图书管理员）
- PUT /api/v1/users/{user_id}: 更新用户信息（仅管理员）
- DELETE /api/v1/users/{user_id}: 删除用户（仅管理员，软删除）

技术要点：
- 支持按角色和活跃状态筛选
- 删除采用软删除（标记 is_active=False）
"""

# 导入标准库
from typing import List, Optional

# 导入 FastAPI 组件
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

# 导入项目模块
from database import get_db
from models.user import User, UserRole
from schemas.user import UserCreate, UserUpdate, UserResponse
from utils.auth import get_current_active_user, require_role, get_password_hash

# 创建 APIRouter 实例
router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    
    无需额外参数，自动从 JWT 令牌获取用户信息
    
    返回：
        UserResponse: 当前用户信息
    """
    return current_user


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """
    获取用户列表（管理员/图书管理员权限）
    
    查询参数：
        skip: 跳过条数（默认 0）
        limit: 每页条数（默认 10，范围 1-100）
        role: 按角色筛选（可选）
        is_active: 按活跃状态筛选（可选）
    
    返回：
        List[UserResponse]: 用户列表
    
    异常：
        HTTPException(403): 权限不足
    """
    # 构建查询对象
    query = db.query(User)
    
    # 按角色筛选
    if role:
        query = query.filter(User.role == role)
    
    # 按活跃状态筛选
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # 分页查询
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "librarian"))
):
    """
    获取指定用户信息（管理员/图书管理员权限）
    
    路径参数：
        user_id: 用户 ID
    
    返回：
        UserResponse: 用户详细信息
    
    异常：
        HTTPException(404): 用户不存在
        HTTPException(403): 权限不足
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    更新用户信息（仅管理员）
    
    路径参数：
        user_id: 用户 ID
    
    请求体：
        可选字段：email, full_name, role, is_active
    
    返回：
        UserResponse: 更新后的用户信息
    
    异常：
        HTTPException(404): 用户不存在
        HTTPException(403): 权限不足
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取更新数据（只包含传入的字段）
    update_data = user_update.dict(exclude_unset=True)
    
    # 应用更新
    for field, value in update_data.items():
        setattr(user, field, value)

    # 提交事务
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    删除用户（仅管理员，软删除）
    
    注意：这里采用软删除策略，将用户标记为不活跃状态，而非物理删除
    
    路径参数：
        user_id: 用户 ID
    
    返回：
        204 No Content
    
    异常：
        HTTPException(404): 用户不存在
        HTTPException(403): 权限不足
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 软删除：将用户标记为不活跃
    user.is_active = False
    db.commit()
    
    return None
