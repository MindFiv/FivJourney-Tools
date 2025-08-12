from fastapi import APIRouter

from apps.api.v1.endpoints import (
    auth,
    expenses,
    itineraries,
    travel_logs,
    travel_plans,
    users,
)

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    travel_plans.router, prefix="/travel-plans", tags=["travel-plans"]
)
api_router.include_router(
    itineraries.router, prefix="/itineraries", tags=["itineraries"]
)
api_router.include_router(
    expenses.router, prefix="/expenses", tags=["expenses"]
)
api_router.include_router(
    travel_logs.router, prefix="/travel-logs", tags=["travel-logs"]
)
