# mypy: disable-error-code="arg-type"
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    operation_id="users_me_get",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户信息"""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="更新当前用户信息",
    operation_id="users_me_put",
)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    update_data = user_update.model_dump(exclude_unset=True)

    # 定义只读字段，防止被更新
    readonly_fields = {
        "id",
        "username",
        "email",
        "created_at",
        "updated_at",
        "is_active",
        "is_verified",
    }

    # 过滤掉只读字段
    filtered_data = {
        k: v for k, v in update_data.items() if k not in readonly_fields
    }

    for field, value in filtered_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user
