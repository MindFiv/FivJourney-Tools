import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ActivityType(enum.Enum):
    TRANSPORTATION = "transportation"  # 交通
    ACCOMMODATION = "accommodation"  # 住宿
    SIGHTSEEING = "sightseeing"  # 观光
    DINING = "dining"  # 用餐
    SHOPPING = "shopping"  # 购物
    ENTERTAINMENT = "entertainment"  # 娱乐
    OTHER = "other"  # 其他


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    day_number = Column(Integer, nullable=False)  # 第几天
    activity_type = Column(Enum(ActivityType), nullable=False)  # type: ignore
    title = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    address = Column(String(300))
    latitude = Column(Numeric(10, 8))  # 纬度
    longitude = Column(Numeric(11, 8))  # 经度
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    estimated_cost = Column(Numeric(10, 2))
    booking_reference = Column(String(100))  # 预订参考号
    notes = Column(Text)  # 备注

    # 外键关联
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关联关系
    travel_plan = relationship("TravelPlan", back_populates="itineraries")
