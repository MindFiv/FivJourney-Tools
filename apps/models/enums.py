import enum


class TravelStatus(enum.Enum):
    PLANNING = "planning"  # 计划中
    CONFIRMED = "confirmed"  # 已确认
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


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


class ActivityType(enum.Enum):
    TRANSPORTATION = "transportation"  # 交通
    ACCOMMODATION = "accommodation"  # 住宿
    SIGHTSEEING = "sightseeing"  # 观光
    DINING = "dining"  # 用餐
    SHOPPING = "shopping"  # 购物
    ENTERTAINMENT = "entertainment"  # 娱乐
    OTHER = "other"  # 其他
