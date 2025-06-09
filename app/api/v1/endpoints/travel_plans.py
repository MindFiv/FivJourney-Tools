from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.travel_plan import TravelPlanCreate, TravelPlanResponse, TravelPlanUpdate

router = APIRouter()


@router.post("/", response_model=TravelPlanResponse, summary="创建旅行计划")
async def create_travel_plan(
    plan_data: TravelPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的旅行计划"""
    db_plan = TravelPlan(**plan_data.dict(), owner_id=current_user.id)

    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)

    return db_plan


@router.get("/", response_model=List[TravelPlanResponse], summary="获取旅行计划列表")
async def get_travel_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的旅行计划列表"""
    result = await db.execute(
        select(TravelPlan)
        .where(TravelPlan.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(TravelPlan.created_at.desc())
    )
    plans = result.scalars().all()

    return plans


@router.get("/{plan_id}", response_model=TravelPlanResponse, summary="获取旅行计划详情")
async def get_travel_plan(
    plan_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """获取指定旅行计划的详情"""
    result = await db.execute(
        select(TravelPlan).where(and_(TravelPlan.id == plan_id, TravelPlan.owner_id == current_user.id))
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在")

    return plan


@router.put("/{plan_id}", response_model=TravelPlanResponse, summary="更新旅行计划")
async def update_travel_plan(
    plan_id: int,
    plan_update: TravelPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新旅行计划"""
    result = await db.execute(
        select(TravelPlan).where(and_(TravelPlan.id == plan_id, TravelPlan.owner_id == current_user.id))
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在")

    update_data = plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)

    return plan


@router.delete("/{plan_id}", summary="删除旅行计划")
async def delete_travel_plan(
    plan_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """删除旅行计划"""
    result = await db.execute(
        select(TravelPlan).where(and_(TravelPlan.id == plan_id, TravelPlan.owner_id == current_user.id))
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在")

    await db.delete(plan)
    await db.commit()

    return {"message": "旅行计划已删除"}
