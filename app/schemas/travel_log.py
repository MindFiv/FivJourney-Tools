from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


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


class TravelLogCreate(TravelLogBase):
    travel_plan_id: Optional[int] = None
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


class TravelLogResponse(TravelLogBase):
    id: int
    images: Optional[List[str]] = None
    author_id: int
    travel_plan_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
