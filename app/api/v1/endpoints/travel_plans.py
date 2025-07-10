# mypy: disable-error-code="arg-type"
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.travel_plan import (
    TravelPlanCreate,
    TravelPlanResponse,
    TravelPlanUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=TravelPlanResponse,
    summary="创建旅行计划",
    operation_id="travel_plans_create",
)
async def create_travel_plan(
    plan_data: TravelPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的旅行计划"""
    db_plan = TravelPlan(**plan_data.model_dump(), owner_id=current_user.id)

    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)

    return db_plan


@router.get(
    "/",
    response_model=List[TravelPlanResponse],
    summary="获取旅行计划列表",
    operation_id="travel_plans_list",
)
async def list_travel_plans(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="计划状态过滤"),
    destination: Optional[str] = Query(None, description="目的地过滤"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的旅行计划列表"""
    query = select(TravelPlan).where(TravelPlan.owner_id == current_user.id)

    if status:
        query = query.where(TravelPlan.status == status)

    if destination:
        query = query.where(TravelPlan.destination.ilike(f"%{destination}%"))

    query = (
        query.order_by(desc(TravelPlan.created_at)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    plans = result.scalars().all()

    return plans


@router.get(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="获取旅行计划详情",
    operation_id="travel_plans_get",
)
async def get_travel_plan(
    plan_id: UUID = Path(..., description="旅行计划ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取旅行计划详情"""
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    return plan


@router.put(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="更新旅行计划",
    operation_id="travel_plans_update",
)
async def update_travel_plan(
    plan_update: TravelPlanUpdate,
    plan_id: UUID = Path(..., description="旅行计划ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新旅行计划"""
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    # 更新字段
    update_data = plan_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)

    return plan


@router.delete(
    "/{plan_id}", summary="删除旅行计划", operation_id="travel_plans_delete"
)
async def delete_travel_plan(
    plan_id: UUID = Path(..., description="旅行计划ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除旅行计划"""
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    await db.delete(plan)
    await db.commit()

    return {"message": "旅行计划已删除"}
