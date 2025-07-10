# mypy: disable-error-code="arg-type"
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.travel_log import TravelLog
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.travel_log import (
    TravelLogCreate,
    TravelLogResponse,
    TravelLogUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=TravelLogResponse,
    summary="创建旅行日志",
    operation_id="travel_logs_create",
)
async def create_travel_log(
    log_data: TravelLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的旅行日志"""
    # 验证旅行计划存在且属于当前用户
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == log_data.travel_plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    travel_plan = result.scalar_one_or_none()
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    # 创建旅行日志
    db_log = TravelLog(**log_data.model_dump(), author_id=current_user.id)

    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)

    return db_log


@router.get(
    "/",
    response_model=List[TravelLogResponse],
    summary="获取旅行日志列表",
    operation_id="travel_logs_list",
)
async def list_travel_logs(
    travel_plan_id: UUID = Query(..., description="旅行计划ID"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定旅行计划的日志列表"""
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

    query = select(TravelLog).where(
        and_(
            TravelLog.author_id == current_user.id,
            TravelLog.travel_plan_id == travel_plan_id,
        )
    )

    query = query.order_by(desc(TravelLog.log_date)).offset(skip).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs


@router.get(
    "/{log_id}",
    response_model=TravelLogResponse,
    summary="获取旅行日志详情",
    operation_id="travel_logs_get",
)
async def get_travel_log(
    log_id: UUID = Path(..., description="旅行日志ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取旅行日志详情"""
    result = await db.execute(
        select(TravelLog).where(
            and_(
                TravelLog.id == log_id, TravelLog.author_id == current_user.id
            )
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在"
        )

    return log


@router.put(
    "/{log_id}",
    response_model=TravelLogResponse,
    summary="更新旅行日志",
    operation_id="travel_logs_update",
)
async def update_travel_log(
    log_update: TravelLogUpdate,
    log_id: UUID = Path(..., description="旅行日志ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新旅行日志"""
    result = await db.execute(
        select(TravelLog).where(
            and_(
                TravelLog.id == log_id, TravelLog.author_id == current_user.id
            )
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在"
        )

    # 更新字段
    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    await db.commit()
    await db.refresh(log)

    return log


@router.delete(
    "/{log_id}", summary="删除旅行日志", operation_id="travel_logs_delete"
)
async def delete_travel_log(
    log_id: UUID = Path(..., description="旅行日志ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除旅行日志"""
    result = await db.execute(
        select(TravelLog).where(
            and_(
                TravelLog.id == log_id, TravelLog.author_id == current_user.id
            )
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在"
        )

    await db.delete(log)
    await db.commit()

    return {"message": "旅行日志已删除"}
