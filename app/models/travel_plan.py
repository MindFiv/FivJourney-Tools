import uuid

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import GUID, Base
from app.models.enums import TravelStatus


class TravelPlan(Base):
    __tablename__ = "travel_plans"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)  # type: ignore[var-annotated]
    title = Column(String(200), nullable=False)
    description = Column(Text)
    destination = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Numeric(12, 2))  # 预算
    status = Column(Enum(TravelStatus), default=TravelStatus.PLANNING)  # type: ignore
    cover_image = Column(String(200))  # 封面图片
    tags = Column(String(500))  # 标签，逗号分隔

    # 外键关联
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=False)  # type: ignore[var-annotated]

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关联关系
    owner = relationship("User", back_populates="travel_plans")
    itineraries = relationship("Itinerary", back_populates="travel_plan", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="travel_plan")
    travel_logs = relationship("TravelLog", back_populates="travel_plan")
