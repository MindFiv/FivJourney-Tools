import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import GUID, Base


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)  # type: ignore[var-annotated]
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    avatar = Column(String(200))  # 头像URL
    bio = Column(Text)  # 个人简介
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # 关联关系
    travel_plans = relationship("TravelPlan", back_populates="owner")
    travel_logs = relationship("TravelLog", back_populates="author")
    expenses = relationship("Expense", back_populates="user")
