# mypy: disable-error-code="arg-type"
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息", operation_id="users_me_get")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息", operation_id="users_me_put")
async def update_current_user(
    user_update: UserUpdate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    update_data = user_update.model_dump(exclude_unset=True)

    # 定义只读字段，防止被更新
    readonly_fields = {"id", "username", "email", "created_at", "updated_at", "is_active", "is_verified"}

    # 过滤掉只读字段
    filtered_data = {k: v for k, v in update_data.items() if k not in readonly_fields}

    for field, value in filtered_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户信息", operation_id="users_get")
async def get_user(
    user_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """获取指定用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return user
