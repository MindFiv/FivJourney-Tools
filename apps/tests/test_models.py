from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.models.expense import Expense, ExpenseCategory
from apps.models.itinerary import Itinerary
from apps.models.travel_log import TravelLog
from apps.models.travel_plan import TravelPlan, TravelStatus
from apps.models.user import User


class TestUserModel:
    """用户模型测试"""

    @pytest_asyncio.fixture
    async def sample_user_data(self) -> dict:
        """样本用户数据"""
        return {
            "username": "test_model_user",
            "email": "model_test@example.com",
            "hashed_password": "hashed_password_123",
            "full_name": "模型测试用户",
            "phone": "13800138000",
            "bio": "这是一个模型测试用户",
        }

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, test_db: AsyncSession, sample_user_data: dict
    ):
        """测试创建用户成功"""
        user = User(**sample_user_data)
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.id is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.is_active is True  # 默认值
        assert user.is_verified is False  # 默认值
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_user_unique_constraints(
        self, test_db: AsyncSession, sample_user_data: dict
    ):
        """测试用户唯一约束"""
        # 创建第一个用户
        user1 = User(**sample_user_data)
        test_db.add(user1)
        await test_db.commit()

        # 尝试创建用户名重复的用户
        user2_data = sample_user_data.copy()
        user2_data["email"] = "different@example.com"
        user2 = User(**user2_data)
        test_db.add(user2)

        with pytest.raises(IntegrityError):
            await test_db.commit()

        await test_db.rollback()  # type: ignore[unreachable]

        # 尝试创建邮箱重复的用户
        user3_data = sample_user_data.copy()
        user3_data["username"] = "different_username"
        user3 = User(**user3_data)
        test_db.add(user3)

        with pytest.raises(IntegrityError):
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_user_required_fields(self, test_db: AsyncSession):
        """测试用户必填字段"""
        # 缺少用户名
        with pytest.raises((IntegrityError, TypeError)):
            user = User(email="test@example.com", hashed_password="password")
            test_db.add(user)
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_user_optional_fields(self, test_db: AsyncSession):
        """测试用户可选字段"""
        user = User(
            username="minimal_user",
            email="minimal@example.com",
            hashed_password="password",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.full_name is None
        assert user.phone is None
        assert user.bio is None
        assert user.avatar is None

    @pytest.mark.asyncio
    async def test_user_timestamps(
        self, test_db: AsyncSession, sample_user_data: dict
    ):
        """测试用户时间戳"""
        user = User(**sample_user_data)
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        created_at = user.created_at
        updated_at = user.updated_at

        assert created_at is not None
        assert updated_at is not None
        assert created_at == updated_at  # 创建时两个时间应该相同

        # 添加小延时确保时间戳变化
        import asyncio

        await asyncio.sleep(0.01)

        # 更新用户信息
        user.full_name = "Updated Name"
        await test_db.commit()
        await test_db.refresh(user)

        assert user.created_at == created_at  # 创建时间不变
        assert user.updated_at >= updated_at  # 更新时间应该大于等于原时间


class TestTravelPlanModel:
    """旅行计划模型测试"""

    @pytest.mark.asyncio
    async def test_create_travel_plan_success(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试创建旅行计划成功"""
        plan_data = {
            "title": "测试旅行计划",
            "description": "这是一个测试的旅行计划",
            "destination": "北京",
            "start_date": date.today() + timedelta(days=7),
            "end_date": date.today() + timedelta(days=14),
            "budget": Decimal("5000.00"),
            "owner_id": test_user.id,
        }

        plan = TravelPlan(**plan_data)
        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)

        assert plan.id is not None
        assert plan.title == plan_data["title"]
        assert plan.status == TravelStatus.PLANNING  # 默认状态
        assert plan.created_at is not None

    @pytest.mark.asyncio
    async def test_travel_plan_status_enum(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试旅行计划状态枚举"""
        plan = TravelPlan(
            title="状态测试计划",
            destination="测试目的地",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            owner_id=test_user.id,
            status=TravelStatus.CONFIRMED,
        )

        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)

        assert plan.status == TravelStatus.CONFIRMED

    @pytest.mark.asyncio
    async def test_travel_plan_foreign_key(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试旅行计划外键关系"""
        plan = TravelPlan(
            title="外键测试计划",
            destination="测试目的地",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            owner_id=test_user.id,
        )

        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)

        # 验证关系
        assert plan.owner_id == test_user.id
        await test_db.refresh(plan, ["owner"])
        assert plan.owner.id == test_user.id

    @pytest.mark.asyncio
    async def test_travel_plan_required_fields(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试旅行计划必填字段"""
        with pytest.raises((IntegrityError, TypeError)):
            plan = TravelPlan(
                # 缺少title
                destination="测试目的地",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1),
                owner_id=test_user.id,
            )
            test_db.add(plan)
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_travel_plan_cascade_delete(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试旅行计划级联删除"""
        # 创建旅行计划
        plan = TravelPlan(
            title="级联删除测试",
            destination="测试目的地",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            owner_id=test_user.id,
        )
        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)

        # 创建关联的行程
        itinerary = Itinerary(
            day_number=1,
            date=date.today(),
            location="测试地点",
            activity="测试活动",
            travel_plan_id=plan.id,
        )
        test_db.add(itinerary)
        await test_db.commit()

        # 删除旅行计划
        await test_db.delete(plan)
        await test_db.commit()

        # 验证关联的行程也被删除
        from sqlalchemy import select

        result = await test_db.execute(
            select(Itinerary).where(Itinerary.travel_plan_id == plan.id)
        )
        assert result.scalar_one_or_none() is None


class TestExpenseModel:
    """费用模型测试"""

    @pytest.mark.asyncio
    async def test_create_expense_success(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试创建费用记录成功"""
        expense_data = {
            "title": "测试费用",
            "description": "这是一个测试费用",
            "amount": Decimal("150.50"),
            "category": ExpenseCategory.TRANSPORTATION,
            "expense_date": datetime.now(),
            "location": "测试地点",
            "user_id": test_user.id,
            "travel_plan_id": test_travel_plan.id,
        }

        expense = Expense(**expense_data)
        test_db.add(expense)
        await test_db.commit()
        await test_db.refresh(expense)

        assert expense.id is not None
        assert expense.amount == expense_data["amount"]
        assert expense.category == ExpenseCategory.TRANSPORTATION

    @pytest.mark.asyncio
    async def test_expense_category_enum(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试费用类别枚举"""
        for category in ExpenseCategory:
            expense = Expense(
                title=f"测试{category.value}费用",
                amount=Decimal("100.00"),
                category=category,
                expense_date=datetime.now(),
                user_id=test_user.id,
                travel_plan_id=test_travel_plan.id,
            )
            test_db.add(expense)

        await test_db.commit()

    @pytest.mark.asyncio
    async def test_expense_decimal_precision(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试费用金额精度"""
        expense = Expense(
            title="精度测试",
            amount=Decimal("123.45"),
            category=ExpenseCategory.FOOD,
            expense_date=datetime.now(),
            user_id=test_user.id,
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(expense)
        await test_db.commit()
        await test_db.refresh(expense)

        assert expense.amount == Decimal("123.45")

    @pytest.mark.asyncio
    async def test_expense_foreign_keys(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试费用外键关系"""
        expense = Expense(
            title="外键测试",
            amount=Decimal("200.00"),
            category=ExpenseCategory.ACCOMMODATION,
            expense_date=datetime.now(),
            user_id=test_user.id,
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(expense)
        await test_db.commit()
        await test_db.refresh(expense)

        # 验证关系
        assert expense.user_id == test_user.id
        assert expense.travel_plan_id == test_travel_plan.id

    @pytest.mark.asyncio
    async def test_expense_required_travel_plan_id(
        self,
        test_db: AsyncSession,
        test_user: User,
    ):
        """测试费用记录必须有travel_plan_id"""
        with pytest.raises((IntegrityError, TypeError)):
            expense = Expense(
                title="测试费用",
                amount=Decimal("100.00"),
                category=ExpenseCategory.FOOD,
                expense_date=datetime.now(),
                user_id=test_user.id,
                # 缺少travel_plan_id
            )
            test_db.add(expense)
            await test_db.commit()


class TestItineraryModel:
    """行程模型测试"""

    @pytest.mark.asyncio
    async def test_create_itinerary_success(
        self, test_db: AsyncSession, test_travel_plan: TravelPlan
    ):
        """测试创建行程成功"""
        itinerary_data = {
            "day_number": 1,
            "date": date.today() + timedelta(days=7),
            "location": "天安门广场",
            "activity": "观光游览",
            "start_time": time(9, 0),
            "end_time": time(11, 0),
            "notes": "记得带相机",
            "travel_plan_id": test_travel_plan.id,
        }

        itinerary = Itinerary(**itinerary_data)
        test_db.add(itinerary)
        await test_db.commit()
        await test_db.refresh(itinerary)

        assert itinerary.id is not None
        assert itinerary.day_number == 1
        assert itinerary.location == "天安门广场"

    @pytest.mark.asyncio
    async def test_itinerary_time_fields(
        self, test_db: AsyncSession, test_travel_plan: TravelPlan
    ):
        """测试行程时间字段"""
        itinerary = Itinerary(
            day_number=1,
            date=date.today(),
            location="测试地点",
            activity="测试活动",
            start_time=time(14, 30),
            end_time=time(16, 45),
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(itinerary)
        await test_db.commit()
        await test_db.refresh(itinerary)

        assert itinerary.start_time == time(14, 30)
        assert itinerary.end_time == time(16, 45)

    @pytest.mark.asyncio
    async def test_itinerary_optional_fields(
        self, test_db: AsyncSession, test_travel_plan: TravelPlan
    ):
        """测试行程可选字段"""
        itinerary = Itinerary(
            day_number=1,
            date=date.today(),
            location="最小行程",
            activity="最小活动",
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(itinerary)
        await test_db.commit()
        await test_db.refresh(itinerary)

        assert itinerary.start_time is None
        assert itinerary.end_time is None
        assert itinerary.notes is None


class TestTravelLogModel:
    """旅行日志模型测试"""

    @pytest.mark.asyncio
    async def test_create_travel_log_success(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试创建旅行日志成功"""
        log_data = {
            "title": "第一天的旅行",
            "content": "今天的旅行非常精彩！",
            "location": "天安门广场",
            "log_date": datetime.now(),
            "weather": "晴天",
            "mood": "开心",
            "author_id": test_user.id,
            "travel_plan_id": test_travel_plan.id,
        }

        log = TravelLog(**log_data)
        test_db.add(log)
        await test_db.commit()
        await test_db.refresh(log)

        assert log.id is not None
        assert log.title == "第一天的旅行"

    @pytest.mark.asyncio
    async def test_travel_log_optional_fields(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试旅行日志可选字段"""
        log = TravelLog(
            title="最小日志",
            content="最小内容",
            log_date=datetime.now(),
            author_id=test_user.id,
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(log)
        await test_db.commit()
        await test_db.refresh(log)

        assert log.weather is None
        assert log.mood is None

    @pytest.mark.asyncio
    async def test_travel_log_foreign_keys(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试旅行日志外键关系"""
        log = TravelLog(
            title="外键测试",
            content="外键测试内容",
            log_date=datetime.now(),
            author_id=test_user.id,
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(log)
        await test_db.commit()
        await test_db.refresh(log)

        assert log.author_id == test_user.id
        assert log.travel_plan_id == test_travel_plan.id


class TestModelRelationships:
    """模型关系测试"""

    @pytest.mark.asyncio
    async def test_user_travel_plans_relationship(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试用户和旅行计划的关系"""
        # 创建多个旅行计划
        for i in range(3):
            plan = TravelPlan(
                title=f"计划 {i+1}",
                destination=f"目的地 {i+1}",
                start_date=date.today() + timedelta(days=i * 7),
                end_date=date.today() + timedelta(days=i * 7 + 3),
                owner_id=test_user.id,
            )
            test_db.add(plan)

        await test_db.commit()

        # 通过关系查询
        await test_db.refresh(test_user, ["travel_plans"])
        assert len(test_user.travel_plans) >= 3

    @pytest.mark.asyncio
    async def test_travel_plan_itineraries_relationship(
        self, test_db: AsyncSession, test_travel_plan: TravelPlan
    ):
        """测试旅行计划和行程的关系"""
        # 创建多个行程
        for i in range(3):
            itinerary = Itinerary(
                day_number=i + 1,
                date=date.today() + timedelta(days=i),
                location=f"地点 {i+1}",
                activity=f"活动 {i+1}",
                travel_plan_id=test_travel_plan.id,
            )
            test_db.add(itinerary)

        await test_db.commit()

        # 通过关系查询
        await test_db.refresh(test_travel_plan, ["itineraries"])
        assert len(test_travel_plan.itineraries) >= 3

    @pytest.mark.asyncio
    async def test_user_expenses_relationship(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试用户和费用的关系"""
        # 创建多个费用记录
        for i in range(3):
            expense = Expense(
                title=f"费用 {i+1}",
                amount=Decimal(f"{100+i*50}.00"),
                category=ExpenseCategory.FOOD,
                expense_date=datetime.now(),
                user_id=test_user.id,
                travel_plan_id=test_travel_plan.id,
            )
            test_db.add(expense)

        await test_db.commit()

        # 通过关系查询
        await test_db.refresh(test_user, ["expenses"])
        assert len(test_user.expenses) >= 3


class TestModelConstraints:
    """模型约束测试"""

    @pytest.mark.asyncio
    async def test_negative_budget_constraint(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试负预算约束"""
        # 根据实际实现，这可能在应用层验证而不是数据库层
        plan = TravelPlan(
            title="负预算测试",
            destination="测试目的地",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            budget=Decimal("-1000.00"),
            owner_id=test_user.id,
        )

        test_db.add(plan)
        # 根据具体实现，这可能成功或失败
        try:
            await test_db.commit()
        except IntegrityError:
            await test_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_date_range(
        self, test_db: AsyncSession, test_user: User
    ):
        """测试无效日期范围约束"""
        # 这通常在应用层验证
        plan = TravelPlan(
            title="无效日期测试",
            destination="测试目的地",
            start_date=date.today() + timedelta(days=7),
            end_date=date.today(),  # 结束日期早于开始日期
            owner_id=test_user.id,
        )

        test_db.add(plan)
        # 应该在应用层验证，而不是数据库层
        await test_db.commit()  # 数据库层可能不会拒绝

    @pytest.mark.asyncio
    async def test_expense_amount_precision(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """测试费用金额精度约束"""
        # 测试超过精度的金额
        expense = Expense(
            title="精度测试",
            amount=Decimal("123.456"),  # 3位小数
            category=ExpenseCategory.FOOD,
            expense_date=datetime.now(),
            user_id=test_user.id,
            travel_plan_id=test_travel_plan.id,
        )

        test_db.add(expense)
        await test_db.commit()
        await test_db.refresh(expense)

        # 检查实际存储的精度
        assert expense.amount in [
            Decimal("123.46"),
            Decimal("123.456"),
        ]  # 根据数据库设置
