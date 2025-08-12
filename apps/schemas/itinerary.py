from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from apps.models.enums import ActivityType


class ItineraryBase(BaseModel):
    day_number: int
    date: date
    location: str
    activity: str
    activity_type: Optional[ActivityType] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    notes: Optional[str] = None

    # 新字段（保持向前兼容）
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    estimated_cost: Optional[Decimal] = None
    booking_reference: Optional[str] = None

    @field_validator("day_number")
    @classmethod
    def validate_day_number(cls, v):
        if v <= 0:
            raise ValueError("天数必须大于0")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if not v or not v.strip():
            raise ValueError("地点不能为空")
        return v.strip()

    @field_validator("activity")
    @classmethod
    def validate_activity(cls, v):
        if not v or not v.strip():
            raise ValueError("活动不能为空")
        return v.strip()

    @field_validator("end_time")
    @classmethod
    def validate_time_order(cls, v, info):
        if v and info.data.get("start_time") and v <= info.data["start_time"]:
            raise ValueError("结束时间必须晚于开始时间")
        return v


class ItineraryCreate(ItineraryBase):
    travel_plan_id: UUID


class ItineraryUpdate(BaseModel):
    day_number: Optional[int] = None
    date: Optional[date] = None
    location: Optional[str] = None
    activity: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    notes: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    estimated_cost: Optional[Decimal] = None
    booking_reference: Optional[str] = None

    @field_validator("day_number")
    @classmethod
    def validate_day_number(cls, v):
        if v is not None and v <= 0:
            raise ValueError("天数必须大于0")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("地点不能为空")
        return v.strip() if v else v

    @field_validator("activity")
    @classmethod
    def validate_activity(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("活动不能为空")
        return v.strip() if v else v


class ItineraryResponse(ItineraryBase):
    id: UUID
    travel_plan_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
