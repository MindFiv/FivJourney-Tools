from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TravelLog(Base):
    __tablename__ = "travel_logs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    log_date = Column(DateTime, nullable=False)
    location = Column(String(200))
    latitude = Column(Numeric(10, 8))  # 纬度
    longitude = Column(Numeric(11, 8))  # 经度
    weather = Column(String(100))  # 天气情况
    mood = Column(String(50))  # 心情
    images = Column(JSON)  # 图片列表，JSON格式
    tags = Column(String(500))  # 标签，逗号分隔
    is_public = Column(String(10), default="private")  # 是否公开：public/private/friends

    # 外键关联
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"))

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关联关系
    author = relationship("User", back_populates="travel_logs")
    travel_plan = relationship("TravelPlan", back_populates="travel_logs")
