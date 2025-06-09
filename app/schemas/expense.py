import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ExpenseCategory(enum.Enum):
    TRANSPORTATION = "transportation"  # 交通费
    ACCOMMODATION = "accommodation"  # 住宿费
    FOOD = "food"  # 餐饮费
    SIGHTSEEING = "sightseeing"  # 门票费
    SHOPPING = "shopping"  # 购物费
    ENTERTAINMENT = "entertainment"  # 娱乐费
    INSURANCE = "insurance"  # 保险费
    VISA = "visa"  # 签证费
    OTHER = "other"  # 其他费用


class ExpenseBase(BaseModel):
    title: str
    description: Optional[str] = None
    amount: Decimal
    currency: str = "CNY"
    category: ExpenseCategory
    expense_date: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    travel_plan_id: Optional[int] = None


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    expense_date: Optional[datetime] = None
    location: Optional[str] = None
    receipt_image: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int
    receipt_image: Optional[str] = None
    user_id: int
    travel_plan_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
