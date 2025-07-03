from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    expenses,
    itineraries,
    travel_logs,
    travel_plans,
    users,
)

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(
    travel_plans.router, prefix="/travel-plans", tags=["旅行计划"]
)
api_router.include_router(
    itineraries.router, prefix="/itineraries", tags=["行程安排"]
)
api_router.include_router(
    expenses.router, prefix="/expenses", tags=["费用记录"]
)
api_router.include_router(
    travel_logs.router, prefix="/travel-logs", tags=["旅行日志"]
)
