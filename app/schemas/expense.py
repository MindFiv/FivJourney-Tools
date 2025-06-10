from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import ExpenseCategory


class ExpenseBase(BaseModel):
    title: str
    description: Optional[str] = None
    amount: Decimal
    currency: str = "CNY"
    category: ExpenseCategory
    expense_date: datetime
    location: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("金额必须大于0")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("标题不能为空")
        return v.strip()


class ExpenseCreate(ExpenseBase):
    travel_plan_id: Optional[UUID] = None


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

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("金额必须大于0")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("标题不能为空")
        return v.strip() if v else v


class ExpenseResponse(ExpenseBase):
    id: UUID
    receipt_image: Optional[str] = None
    user_id: UUID
    travel_plan_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
