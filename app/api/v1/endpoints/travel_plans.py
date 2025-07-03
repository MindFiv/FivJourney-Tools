# mypy: disable-error-code="arg-type"
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.expense import Expense
from app.models.travel_plan import TravelPlan
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.schemas.travel_plan import (
    TravelPlanCreate,
    TravelPlanResponse,
    TravelPlanUpdate,
)

# from sqlalchemy.future import select


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
async def get_travel_plans(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="计划状态"),
    destination: Optional[str] = Query(None, description="目的地"),
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
    plan_id: UUID,
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
    plan_id: UUID,
    plan_update: TravelPlanUpdate,
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
    plan_id: UUID,
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


# 费用相关的子路由
@router.post(
    "/{plan_id}/expenses/",
    response_model=ExpenseResponse,
    summary="创建费用记录",
    operation_id="travel_plans_create_expense",
)
async def create_expense_for_plan(
    plan_id: UUID,
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """为指定旅行计划创建费用记录"""
    # 验证旅行计划是否存在且属于当前用户
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

    # 创建费用记录
    expense_dict = expense_data.model_dump()
    expense_dict["travel_plan_id"] = plan_id
    expense_dict["user_id"] = current_user.id

    db_expense = Expense(**expense_dict)
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)

    return db_expense


@router.get(
    "/{plan_id}/expenses/",
    response_model=List[ExpenseResponse],
    summary="获取旅行计划的费用记录",
    operation_id="travel_plans_expenses_list",
)
async def get_expenses_for_plan(
    plan_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定旅行计划的费用记录"""
    # 验证旅行计划是否存在且属于当前用户
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

    # 获取费用记录
    query = (
        select(Expense)
        .where(
            and_(
                Expense.travel_plan_id == plan_id,
                Expense.user_id == current_user.id,
            )
        )
        .offset(skip)
        .limit(limit)
        .order_by(Expense.expense_date.desc())
    )

    result = await db.execute(query)
    expenses = result.scalars().all()

    return expenses


@router.get(
    "/{plan_id}/expenses/statistics",
    summary="获取旅行计划的费用统计",
    operation_id="travel_plans_expenses_statistics",
)
async def get_expense_statistics_for_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定旅行计划的费用统计"""
    # 验证旅行计划是否存在且属于当前用户
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

    # 获取统计数据
    query = (
        select(
            Expense.category,
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count"),
        )
        .where(
            and_(
                Expense.travel_plan_id == plan_id,
                Expense.user_id == current_user.id,
            )
        )
        .group_by(Expense.category)
    )

    result = await db.execute(query)
    statistics = result.all()

    # 计算总金额
    total_query = select(func.sum(Expense.amount)).where(
        and_(
            Expense.travel_plan_id == plan_id,
            Expense.user_id == current_user.id,
        )
    )
    total_result = await db.execute(total_query)
    total_amount = total_result.scalar() or 0

    return {
        "total_amount": total_amount,
        "by_category": [
            {
                "category": stat.category,
                "amount": stat.total_amount,
                "count": stat.count,
            }
            for stat in statistics
        ],
    }
