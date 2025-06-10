from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import TravelStatus


class TravelPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    destination: str
    start_date: date
    end_date: date
    budget: Optional[Decimal] = None
    tags: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("标题不能为空")
        if len(v.strip()) > 200:
            raise ValueError("标题长度不能超过200个字符")
        return v.strip()

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, v):
        if not v or not v.strip():
            raise ValueError("目的地不能为空")
        return v.strip()

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError("预算不能为负数")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        if info.data and "start_date" in info.data and v < info.data["start_date"]:
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

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("标题不能为空")
        if v is not None and len(v.strip()) > 200:
            raise ValueError("标题长度不能超过200个字符")
        return v.strip() if v else v

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("目的地不能为空")
        return v.strip() if v else v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError("预算不能为负数")
        return v


class TravelPlanResponse(TravelPlanBase):
    id: int
    status: TravelStatus
    cover_image: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
