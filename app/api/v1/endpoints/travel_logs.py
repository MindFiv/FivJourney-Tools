from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.travel_log import TravelLog
from app.models.user import User
from app.schemas.travel_log import TravelLogCreate, TravelLogResponse, TravelLogUpdate

router = APIRouter()


@router.post("/", response_model=TravelLogResponse, summary="创建旅行日志")
async def create_travel_log(
    log_data: TravelLogCreate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """创建新的旅行日志"""
    db_log = TravelLog(**log_data.dict(), author_id=current_user.id)

    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)

    return db_log


@router.get("/", response_model=List[TravelLogResponse], summary="获取旅行日志列表")
async def get_travel_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    travel_plan_id: Optional[int] = None,
    is_public: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取旅行日志列表"""
    # 基础查询：获取当前用户的日志或公开的日志
    query = select(TravelLog).where(or_(TravelLog.author_id == current_user.id, TravelLog.is_public == "public"))

    if travel_plan_id:
        query = query.where(TravelLog.travel_plan_id == travel_plan_id)

    if is_public:
        query = query.where(TravelLog.is_public == is_public)

    query = query.offset(skip).limit(limit).order_by(TravelLog.log_date.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs


@router.get("/my", response_model=List[TravelLogResponse], summary="获取我的旅行日志")
async def get_my_travel_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    travel_plan_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的旅行日志"""
    query = select(TravelLog).where(TravelLog.author_id == current_user.id)

    if travel_plan_id:
        query = query.where(TravelLog.travel_plan_id == travel_plan_id)

    query = query.offset(skip).limit(limit).order_by(TravelLog.log_date.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs


@router.get("/{log_id}", response_model=TravelLogResponse, summary="获取旅行日志详情")
async def get_travel_log(
    log_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """获取指定旅行日志的详情"""
    result = await db.execute(select(TravelLog).where(TravelLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在")

    # 检查访问权限
    if log.author_id != current_user.id and log.is_public != "public":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此日志")

    return log


@router.put("/{log_id}", response_model=TravelLogResponse, summary="更新旅行日志")
async def update_travel_log(
    log_id: int,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在或无权限修改")

    update_data = log_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    await db.commit()
    await db.refresh(log)

    return log


@router.delete("/{log_id}", summary="删除旅行日志")
async def delete_travel_log(
    log_id: int, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """删除旅行日志"""
    result = await db.execute(
        select(TravelLog).where(and_(TravelLog.id == log_id, TravelLog.author_id == current_user.id))
    )
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="旅行日志不存在或无权限删除")

    await db.delete(log)
    await db.commit()

    return {"message": "旅行日志已删除"}


@router.get("/public/latest", response_model=List[TravelLogResponse], summary="获取最新公开日志")
async def get_latest_public_logs(limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    """获取最新的公开旅行日志"""
    result = await db.execute(
        select(TravelLog).where(TravelLog.is_public == "public").order_by(TravelLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()

    return logs
