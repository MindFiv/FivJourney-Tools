from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.itinerary import Itinerary
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.itinerary import ItineraryCreate, ItineraryResponse, ItineraryUpdate

router = APIRouter()


@router.post("/", response_model=ItineraryResponse, summary="创建行程安排")
async def create_itinerary(
    itinerary_data: ItineraryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的行程安排"""
    # 验证旅行计划是否属于当前用户
    result = await db.execute(
        select(TravelPlan).where(
            and_(TravelPlan.id == itinerary_data.travel_plan_id, TravelPlan.owner_id == current_user.id)
        )
    )
    travel_plan = result.scalar_one_or_none()

    if not travel_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在或无权限访问")

    db_itinerary = Itinerary(**itinerary_data.dict())

    db.add(db_itinerary)
    await db.commit()
    await db.refresh(db_itinerary)

    return db_itinerary


@router.get("/travel-plan/{plan_id}", response_model=List[ItineraryResponse], summary="获取旅行计划的行程列表")
async def get_itineraries_by_plan(
    plan_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """获取指定旅行计划的行程安排列表"""
    # 验证旅行计划是否属于当前用户
    result = await db.execute(
        select(TravelPlan).where(and_(TravelPlan.id == plan_id, TravelPlan.owner_id == current_user.id))
    )
    travel_plan = result.scalar_one_or_none()

    if not travel_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在或无权限访问")

    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.travel_plan_id == plan_id)
        .order_by(Itinerary.day_number, Itinerary.start_time)
    )
    itineraries = result.scalars().all()

    return itineraries


@router.get("/{itinerary_id}", response_model=ItineraryResponse, summary="获取行程详情")
async def get_itinerary(
    itinerary_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """获取指定行程的详情"""
    result = await db.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")

    # 验证权限
    result = await db.execute(
        select(TravelPlan).where(
            and_(TravelPlan.id == itinerary.travel_plan_id, TravelPlan.owner_id == current_user.id)
        )
    )
    travel_plan = result.scalar_one_or_none()

    if not travel_plan:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此行程")

    return itinerary


@router.put("/{itinerary_id}", response_model=ItineraryResponse, summary="更新行程安排")
async def update_itinerary(
    itinerary_id: int,
    itinerary_update: ItineraryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新行程安排"""
    result = await db.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")

    # 验证权限
    result = await db.execute(
        select(TravelPlan).where(
            and_(TravelPlan.id == itinerary.travel_plan_id, TravelPlan.owner_id == current_user.id)
        )
    )
    travel_plan = result.scalar_one_or_none()

    if not travel_plan:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改此行程")

    update_data = itinerary_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(itinerary, field, value)

    await db.commit()
    await db.refresh(itinerary)

    return itinerary


@router.delete("/{itinerary_id}", summary="删除行程安排")
async def delete_itinerary(
    itinerary_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """删除行程安排"""
    result = await db.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")

    # 验证权限
    result = await db.execute(
        select(TravelPlan).where(
            and_(TravelPlan.id == itinerary.travel_plan_id, TravelPlan.owner_id == current_user.id)
        )
    )
    travel_plan = result.scalar_one_or_none()

    if not travel_plan:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除此行程")

    await db.delete(itinerary)
    await db.commit()

    return {"message": "行程安排已删除"}
