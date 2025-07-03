import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import GUID, Base
from app.models.enums import ExpenseCategory


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)  # type: ignore[var-annotated]
    title = Column(String(200), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(12, 2), nullable=False)  # 金额
    currency = Column(String(3), default="CNY")  # 货币代码
    category = Column(Enum(ExpenseCategory), nullable=False)  # type: ignore
    expense_date = Column(DateTime(timezone=True), nullable=False)  # 消费日期
    location = Column(String(200))  # 消费地点
    receipt_image = Column(String(200))  # 收据图片
    notes = Column(Text)  # 备注

    # 外键关联
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)  # type: ignore[var-annotated]
    travel_plan_id = Column(GUID(), ForeignKey("travel_plans.id"))  # type: ignore[var-annotated]

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # 关联关系
    user = relationship("User", back_populates="expenses")
    travel_plan = relationship("TravelPlan", back_populates="expenses")
