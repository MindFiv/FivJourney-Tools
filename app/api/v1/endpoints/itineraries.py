# mypy: disable-error-code="arg-type"
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.enums import ActivityType
from app.models.itinerary import Itinerary
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.itinerary import (
    ItineraryCreate,
    ItineraryResponse,
    ItineraryUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ItineraryResponse,
    summary="创建行程",
    operation_id="itineraries_create",
)
async def create_itinerary(
    itinerary_data: ItineraryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的行程安排"""
    # 验证旅行计划存在且属于当前用户
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == itinerary_data.travel_plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    travel_plan = result.scalar_one_or_none()
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    # 创建行程
    db_itinerary = Itinerary(**itinerary_data.model_dump())

    db.add(db_itinerary)
    await db.commit()
    await db.refresh(db_itinerary)

    return db_itinerary


@router.get(
    "/",
    response_model=List[ItineraryResponse],
    summary="获取行程列表",
    operation_id="itineraries_list",
)
async def list_itineraries(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    travel_plan_id: UUID = Query(..., description="旅行计划ID"),
    day_number: Optional[int] = Query(None, description="筛选特定天数"),
    activity_type: Optional[str] = Query(None, description="活动类型"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取行程列表，可选择性筛选特定旅行计划"""

    # 构建基础查询，通过 JOIN 确保只返回用户拥有的旅行计划的行程
    query = (
        select(Itinerary)
        .join(TravelPlan)
        .where(TravelPlan.owner_id == current_user.id)
    )

    # 验证旅行计划存在且属于当前用户
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == travel_plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    travel_plan = result.scalar_one_or_none()
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    query = query.where(Itinerary.travel_plan_id == travel_plan_id)

    if day_number is not None:
        query = query.where(Itinerary.day_number == day_number)

    if activity_type:
        try:
            activity_enum = ActivityType(activity_type)
            query = query.where(Itinerary.activity_type == activity_enum)
        except ValueError:
            # 无效的活动类型，返回空结果
            return []

    query = (
        query.order_by(asc(Itinerary.day_number), asc(Itinerary.start_time))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    itineraries = result.scalars().all()

    return itineraries


@router.get(
    "/{itinerary_id}",
    response_model=ItineraryResponse,
    summary="获取行程详情",
    operation_id="itineraries_get",
)
async def get_itinerary(
    itinerary_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取行程详情"""
    result = await db.execute(
        select(Itinerary)
        .join(TravelPlan)
        .where(
            and_(
                Itinerary.id == itinerary_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在"
        )

    return itinerary


@router.put(
    "/{itinerary_id}",
    response_model=ItineraryResponse,
    summary="更新行程",
    operation_id="itineraries_update",
)
async def update_itinerary(
    itinerary_id: UUID,
    itinerary_update: ItineraryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新行程信息"""
    result = await db.execute(
        select(Itinerary)
        .join(TravelPlan)
        .where(
            and_(
                Itinerary.id == itinerary_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在"
        )

    # 更新字段
    update_data = itinerary_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(itinerary, field, value)

    await db.commit()
    await db.refresh(itinerary)

    return itinerary


@router.delete(
    "/{itinerary_id}", summary="删除行程", operation_id="itineraries_delete"
)
async def delete_itinerary(
    itinerary_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除行程"""
    result = await db.execute(
        select(Itinerary)
        .join(TravelPlan)
        .where(
            and_(
                Itinerary.id == itinerary_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在"
        )

    await db.delete(itinerary)
    await db.commit()

    return {"message": "行程已删除"}
