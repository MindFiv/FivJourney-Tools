import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.travel_plan import TravelPlan, TravelStatus
from app.models.user import User
from main import app

# 测试数据库引擎
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """创建测试客户端"""

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """创建测试用户"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "full_name": "测试用户",
        "phone": "13800138000",
        "bio": "这是一个测试用户",
        "is_active": True,
        "is_verified": True,
    }

    user = User(**user_data)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_inactive_user(test_db: AsyncSession) -> User:
    """创建非活跃测试用户"""
    user_data = {
        "username": "inactiveuser",
        "email": "inactive@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "full_name": "非活跃用户",
        "is_active": False,
        "is_verified": False,
    }

    user = User(**user_data)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """创建测试用户的JWT token"""
    return create_access_token(data={"sub": test_user.username})


@pytest.fixture
def auth_headers(test_user_token: str) -> dict:
    """创建认证请求头"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def test_travel_plan(test_db: AsyncSession, test_user: User) -> TravelPlan:
    """创建测试旅行计划"""
    from datetime import date, timedelta

    plan_data = {
        "title": "测试旅行计划",
        "description": "这是一个测试的旅行计划",
        "destination": "北京",
        "start_date": date.today() + timedelta(days=7),
        "end_date": date.today() + timedelta(days=14),
        "budget": 5000.00,
        "status": TravelStatus.PLANNING,
        "tags": "城市游,文化,美食",
        "owner_id": test_user.id,
    }

    plan = TravelPlan(**plan_data)
    test_db.add(plan)
    await test_db.commit()
    await test_db.refresh(plan)
    return plan


@pytest.fixture
def sample_user_data() -> dict:
    """样本用户数据"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "新用户",
        "phone": "13900139000",
        "bio": "新注册的用户",
    }


@pytest.fixture
def sample_travel_plan_data() -> dict:
    """样本旅行计划数据"""
    from datetime import date, timedelta

    return {
        "title": "新的旅行计划",
        "description": "探索美丽的城市",
        "destination": "上海",
        "start_date": (date.today() + timedelta(days=30)).isoformat(),
        "end_date": (date.today() + timedelta(days=37)).isoformat(),
        "budget": 8000.00,
        "tags": "城市游,购物,美食",
    }


@pytest.fixture
def sample_itinerary_data() -> dict:
    """样本行程数据"""
    from datetime import date, time, timedelta

    return {
        "day_number": 1,
        "date": (date.today() + timedelta(days=30)).isoformat(),
        "location": "外滩",
        "activity": "观赏黄浦江夜景",
        "start_time": time(19, 0).isoformat(),
        "end_time": time(21, 0).isoformat(),
        "notes": "建议穿舒适的鞋子",
    }


@pytest.fixture
def sample_expense_data() -> dict:
    """样本费用数据"""
    from datetime import datetime, timedelta

    return {
        "title": "机票费用",
        "description": "往返机票",
        "amount": 150.00,
        "category": "transportation",
        "expense_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "location": "机场",
        "notes": "信用卡支付",
    }


@pytest.fixture
def sample_travel_log_data() -> dict:
    """样本旅行日志数据"""
    from datetime import datetime, timedelta

    return {
        "title": "第一天的旅行",
        "content": "今天的旅行非常精彩，看到了很多美丽的风景。",
        "location": "外滩",
        "log_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "weather": "晴天",
        "mood": "开心",
        "is_public": "public",
    }


@pytest_asyncio.fixture
async def test_expense(test_db: AsyncSession, test_user: User, test_travel_plan: TravelPlan):
    """创建测试费用记录"""
    from datetime import datetime, timedelta
    from decimal import Decimal

    from app.models.enums import ExpenseCategory
    from app.models.expense import Expense

    expense_data = {
        "title": "测试费用",
        "description": "这是一个测试费用记录",
        "amount": Decimal("200.00"),
        "category": ExpenseCategory.TRANSPORTATION,
        "expense_date": datetime.now() + timedelta(days=30),
        "location": "测试地点",
        "notes": "测试备注",
        "user_id": test_user.id,
        "travel_plan_id": test_travel_plan.id,
    }

    expense = Expense(**expense_data)
    test_db.add(expense)
    await test_db.commit()
    await test_db.refresh(expense)
    return expense
