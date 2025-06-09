import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, validator


class TravelStatus(enum.Enum):
    PLANNING = "planning"  # 计划中
    CONFIRMED = "confirmed"  # 已确认
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class TravelPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    destination: str
    start_date: date
    end_date: date
    budget: Optional[Decimal] = None
    tags: Optional[str] = None

    @validator("end_date")
    def validate_dates(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("结束日期不能早于开始日期")
        return v


class TravelPlanCreate(TravelPlanBase):
    pass


class TravelPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    status: Optional[TravelStatus] = None
    cover_image: Optional[str] = None
    tags: Optional[str] = None


class TravelPlanResponse(TravelPlanBase):
    id: int
    status: TravelStatus
    cover_image: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
