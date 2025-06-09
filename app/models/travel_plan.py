import enum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TravelStatus(enum.Enum):
    PLANNING = "planning"  # 计划中
    CONFIRMED = "confirmed"  # 已确认
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class TravelPlan(Base):
    __tablename__ = "travel_plans"

    id = Column(Integer, primary_key=True, index=True)
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
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关联关系
    owner = relationship("User", back_populates="travel_plans")
    itineraries = relationship("Itinerary", back_populates="travel_plan", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="travel_plan")
    travel_logs = relationship("TravelLog", back_populates="travel_plan")
