from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class TravelLogBase(BaseModel):
    title: str
    content: str
    log_date: datetime
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    weather: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[str] = None
    is_public: str = "private"

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("标题不能为空")
        if len(v.strip()) > 200:
            raise ValueError("标题长度不能超过200个字符")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("内容不能为空")
        return v.strip()

    @field_validator("is_public")
    @classmethod
    def validate_privacy(cls, v):
        if v not in ["public", "private", "friends"]:
            raise ValueError("隐私级别必须是 public, private 或 friends")
        return v


class TravelLogCreate(TravelLogBase):
    travel_plan_id: Optional[UUID] = None
    images: Optional[List[str]] = None


class TravelLogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    log_date: Optional[datetime] = None
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    weather: Optional[str] = None
    mood: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[str] = None
    is_public: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("标题不能为空")
        if v is not None and len(v.strip()) > 200:
            raise ValueError("标题长度不能超过200个字符")
        return v.strip() if v else v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("内容不能为空")
        return v.strip() if v else v

    @field_validator("is_public")
    @classmethod
    def validate_privacy(cls, v):
        if v is not None and v not in ["public", "private", "friends"]:
            raise ValueError("隐私级别必须是 public, private 或 friends")
        return v


class TravelLogResponse(TravelLogBase):
    id: UUID
    images: Optional[List[str]] = None
    author_id: UUID
    travel_plan_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
