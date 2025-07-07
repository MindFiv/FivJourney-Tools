from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    await create_tables()
    yield
    # 关闭时的清理工作


app = FastAPI(
    title="FivJourney Tools",
    description="为用户提供旅游行前、行中、行后的全过程追踪和帮助",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["system"])
async def root():
    return {"message": "FivJourney Tools API", "version": "1.0.0"}


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy"}


# mcp = FastApiMCP(
#     app,
#     describe_full_response_schema=True,
#     describe_all_responses=True,
# )
# mcp.mount(mount_path="/sse")

mcp_travel_plan = FastApiMCP(
    app,
    describe_full_response_schema=True,
    describe_all_responses=True,
    include_tags=["travel-plans"],
)
mcp_travel_plan.mount(mount_path="/sse/travel-plans")

mcp_itineraries = FastApiMCP(
    app,
    describe_full_response_schema=True,
    describe_all_responses=True,
    include_tags=["itineraries"],
)
mcp_itineraries.mount(mount_path="/sse/itineraries")

mcp_expenses = FastApiMCP(
    app,
    describe_full_response_schema=True,
    describe_all_responses=True,
    include_tags=["expenses"],
)
mcp_expenses.mount(mount_path="/sse/expenses")

mcp_travel_logs = FastApiMCP(
    app,
    describe_full_response_schema=True,
    describe_all_responses=True,
    include_tags=["travel-logs"],
)
mcp_travel_logs.mount(mount_path="/sse/travel-logs")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
