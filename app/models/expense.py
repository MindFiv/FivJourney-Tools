import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExpenseCategory(enum.Enum):
    TRANSPORTATION = "transportation"  # 交通费
    ACCOMMODATION = "accommodation"  # 住宿费
    FOOD = "food"  # 餐饮费
    SIGHTSEEING = "sightseeing"  # 门票费
    SHOPPING = "shopping"  # 购物费
    ENTERTAINMENT = "entertainment"  # 娱乐费
    INSURANCE = "insurance"  # 保险费
    VISA = "visa"  # 签证费
    OTHER = "other"  # 其他费用


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="CNY")  # 货币代码
    category = Column(Enum(ExpenseCategory), nullable=False)  # type: ignore
    expense_date = Column(DateTime, nullable=False)
    location = Column(String(200))
    receipt_image = Column(String(200))  # 收据图片
    notes = Column(Text)

    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"))

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="expenses")
    travel_plan = relationship("TravelPlan", back_populates="expenses")
