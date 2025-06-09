import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ActivityType(enum.Enum):
    TRANSPORTATION = "transportation"  # 交通
    ACCOMMODATION = "accommodation"  # 住宿
    SIGHTSEEING = "sightseeing"  # 观光
    DINING = "dining"  # 用餐
    SHOPPING = "shopping"  # 购物
    ENTERTAINMENT = "entertainment"  # 娱乐
    OTHER = "other"  # 其他


class ItineraryBase(BaseModel):
    day_number: int
    activity_type: ActivityType
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_cost: Optional[Decimal] = None
    booking_reference: Optional[str] = None
    notes: Optional[str] = None


class ItineraryCreate(ItineraryBase):
    travel_plan_id: int


class ItineraryUpdate(BaseModel):
    day_number: Optional[int] = None
    activity_type: Optional[ActivityType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_cost: Optional[Decimal] = None
    booking_reference: Optional[str] = None
    notes: Optional[str] = None


class ItineraryResponse(ItineraryBase):
    id: int
    travel_plan_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
