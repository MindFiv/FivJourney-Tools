import uuid

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import GUID, Base
from app.models.enums import ActivityType


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)  # type: ignore[var-annotated]
    day_number = Column(Integer, nullable=False)  # 第几天
    date = Column(Date, nullable=False)  # 日期
    location = Column(String(200), nullable=False)  # 地点
    activity = Column(String(200), nullable=False)  # 活动
    activity_type = Column(Enum(ActivityType), nullable=True)  # type: ignore  # 活动类型（可选）
    start_time = Column(Time)  # 开始时间
    end_time = Column(Time)  # 结束时间
    notes = Column(Text)  # 备注

    # 新字段（保持向前兼容）
    title = Column(String(200))  # 可选标题
    description = Column(Text)  # 描述
    address = Column(String(500))  # 详细地址
    latitude = Column(Numeric(10, 8))  # 纬度
    longitude = Column(Numeric(11, 8))  # 经度
    estimated_cost = Column(Numeric(12, 2))  # 预估费用
    booking_reference = Column(String(100))  # 预订参考号

    # 外键关联
    travel_plan_id = Column(GUID(), ForeignKey("travel_plans.id"), nullable=False)  # type: ignore[var-annotated]

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # 关联关系
    travel_plan = relationship("TravelPlan", back_populates="itineraries")
