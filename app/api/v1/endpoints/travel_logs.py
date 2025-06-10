# mypy: disable-error-code="arg-type"
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.travel_log import TravelLog
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.travel_log import TravelLogCreate, TravelLogResponse, TravelLogUpdate

router = APIRouter()


@router.post("/", response_model=TravelLogResponse, summary="创建旅行日志")
async def create_travel_log(
    log_data: TravelLogCreate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """创建新的旅行日志"""
    # 如果指定了旅行计划，验证其存在且属于当前用户
    if log_data.travel_plan_id:
        result = await db.execute(
            select(TravelPlan).where(
                and_(TravelPlan.id == log_data.travel_plan_id, TravelPlan.owner_id == current_user.id)
            )
        )
        travel_plan = result.scalar_one_or_none()
        if not travel_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在")

    # 创建旅行日志
    db_log = TravelLog(**log_data.model_dump(), author_id=current_user.id)

    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)

    return db_log


@router.get("/", response_model=List[TravelLogResponse], summary="获取旅行日志列表")
async def get_travel_logs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    travel_plan_id: Optional[UUID] = Query(None, description="旅行计划ID"),
    is_public: Optional[str] = Query(None, description="隐私级别"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取旅行日志列表（包含公开的和自己的）"""
    query = select(TravelLog).where((TravelLog.is_public == "public") | (TravelLog.author_id == current_user.id))

    if travel_plan_id is not None:
        query = query.where(TravelLog.travel_plan_id == travel_plan_id)

    if is_public:
        query = query.where(TravelLog.is_public == is_public)

    query = query.order_by(desc(TravelLog.log_date)).offset(skip).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs


@router.get("/my", response_model=List[TravelLogResponse], summary="获取我的旅行日志")
async def get_my_travel_logs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    travel_plan_id: Optional[UUID] = Query(None, description="旅行计划ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的旅行日志"""
    query = select(TravelLog).where(TravelLog.author_id == current_user.id)

    if travel_plan_id is not None:
        query = query.where(TravelLog.travel_plan_id == travel_plan_id)

    query = query.order_by(desc(TravelLog.log_date)).offset(skip).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs


@router.get("/{log_id}", response_model=TravelLogResponse, summary="获取旅行日志详情")
async def get_travel_log(
    log_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """获取旅行日志详情"""
    result = await db.execute(select(TravelLog).where(TravelLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在")

    # 检查访问权限
    if log.is_public != "public" and log.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此日志")

    return log


@router.put("/{log_id}", response_model=TravelLogResponse, summary="更新旅行日志")
async def update_travel_log(
    log_id: UUID,
    log_update: TravelLogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新旅行日志"""
    result = await db.execute(
        select(TravelLog).where(and_(TravelLog.id == log_id, TravelLog.author_id == current_user.id))
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在")

    # 更新字段
    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    await db.commit()
    await db.refresh(log)

    return log


@router.delete("/{log_id}", summary="删除旅行日志")
async def delete_travel_log(
    log_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """删除旅行日志"""
    result = await db.execute(
        select(TravelLog).where(and_(TravelLog.id == log_id, TravelLog.author_id == current_user.id))
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在")

    await db.delete(log)
    await db.commit()

    return {"message": "旅行日志已删除"}


@router.get("/public/latest", response_model=List[TravelLogResponse], summary="获取最新公开日志")
async def get_latest_public_logs(
    limit: int = Query(10, ge=1, le=50, description="返回的记录数"), db: AsyncSession = Depends(get_db)
):
    """获取最新的公开旅行日志"""
    result = await db.execute(
        select(TravelLog).where(TravelLog.is_public == "public").order_by(desc(TravelLog.log_date)).limit(limit)
    )
    logs = result.scalars().all()

    return logs
