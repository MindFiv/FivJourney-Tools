# mypy: disable-error-code="arg-type"
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.database import get_db
from apps.core.security import get_current_active_user
from apps.models.enums import ExpenseCategory
from apps.models.expense import Expense
from apps.models.travel_plan import TravelPlan
from apps.models.user import User
from apps.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=ExpenseResponse,
    summary="创建费用记录",
    operation_id="expenses_create",
)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的费用记录"""
    # 验证旅行计划存在且属于当前用户
    result = await db.execute(
        select(TravelPlan).where(
            and_(
                TravelPlan.id == expense_data.travel_plan_id,
                TravelPlan.owner_id == current_user.id,
            )
        )
    )
    travel_plan = result.scalar_one_or_none()
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="旅行计划不存在"
        )

    db_expense = Expense(**expense_data.model_dump(), user_id=current_user.id)

    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)

    return db_expense


@router.get(
    "/",
    response_model=List[ExpenseResponse],
    summary="获取费用记录列表",
    operation_id="expenses_list",
)
async def list_expenses(
    travel_plan_id: UUID = Query(..., description="旅行计划ID"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    category: Optional[ExpenseCategory] = Query(
        None, description="费用类别过滤"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的费用记录列表"""
    query = select(Expense).where(
        and_(
            Expense.user_id == current_user.id,
            Expense.travel_plan_id == travel_plan_id,
        )
    )

    if category:
        query = query.where(Expense.category == category)

    query = (
        query.offset(skip).limit(limit).order_by(Expense.expense_date.desc())
    )

    result = await db.execute(query)
    expenses = result.scalars().all()

    return expenses


@router.get(
    "/statistics", summary="获取费用统计", operation_id="expenses_statistics"
)
async def get_expense_statistics(
    travel_plan_id: UUID = Query(..., description="旅行计划ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取费用统计信息"""
    query = select(
        Expense.category,
        func.sum(Expense.amount).label("total_amount"),
        func.count(Expense.id).label("count"),
    ).where(
        and_(
            Expense.user_id == current_user.id,
            Expense.travel_plan_id == travel_plan_id,
        )
    )

    query = query.group_by(Expense.category)

    result = await db.execute(query)
    statistics = result.all()

    # 计算总金额
    total_query = select(func.sum(Expense.amount)).where(
        and_(
            Expense.user_id == current_user.id,
            Expense.travel_plan_id == travel_plan_id,
        )
    )

    total_result = await db.execute(total_query)
    total_amount = total_result.scalar() or Decimal("0")

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


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="获取费用记录详情",
    operation_id="expenses_get",
)
async def get_expense(
    expense_id: UUID = Path(..., description="费用记录ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定费用记录的详情"""
    result = await db.execute(
        select(Expense).where(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        )
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="费用记录不存在"
        )

    return expense


@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="更新费用记录",
    operation_id="expenses_update",
)
async def update_expense(
    expense_update: ExpenseUpdate,
    expense_id: UUID = Path(..., description="费用记录ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新费用记录"""
    result = await db.execute(
        select(Expense).where(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        )
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="费用记录不存在"
        )

    update_data = expense_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    await db.commit()
    await db.refresh(expense)

    return expense


@router.delete(
    "/{expense_id}", summary="删除费用记录", operation_id="expenses_delete"
)
async def delete_expense(
    expense_id: UUID = Path(..., description="费用记录ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除费用记录"""
    result = await db.execute(
        select(Expense).where(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        )
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="费用记录不存在"
        )

    await db.delete(expense)
    await db.commit()

    return {"message": "费用记录已删除"}
