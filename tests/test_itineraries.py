import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.itinerary import Itinerary
from app.models.travel_plan import TravelPlan
from app.models.user import User


class TestItineraryCreation:
    """行程创建测试"""

    def test_create_itinerary_success(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_itinerary_data: dict
    ):
        """测试创建行程成功"""
        sample_itinerary_data["travel_plan_id"] = test_travel_plan.id
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=sample_itinerary_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["day_number"] == sample_itinerary_data["day_number"]
        assert data["location"] == sample_itinerary_data["location"]
        assert data["activity"] == sample_itinerary_data["activity"]
        assert data["travel_plan_id"] == test_travel_plan.id
        assert "id" in data

    def test_create_itinerary_unauthorized(
        self, client: TestClient, test_travel_plan: TravelPlan, sample_itinerary_data: dict
    ):
        """测试未认证创建行程"""
        sample_itinerary_data["travel_plan_id"] = test_travel_plan.id
        response = client.post("/api/v1/itineraries/", json=sample_itinerary_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_itinerary_invalid_travel_plan(
        self, client: TestClient, auth_headers: dict, sample_itinerary_data: dict
    ):
        """测试创建行程时使用无效的旅行计划ID"""
        sample_itinerary_data["travel_plan_id"] = 99999  # 不存在的计划ID
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=sample_itinerary_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_itinerary_missing_required_fields(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan
    ):
        """测试创建行程缺少必填字段"""
        incomplete_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            # 缺少location, activity等必填字段
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_itinerary_with_time_fields(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan
    ):
        """测试创建包含时间字段的行程"""
        from datetime import date, time, timedelta

        itinerary_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "location": "测试地点",
            "activity": "测试活动",
            "start_time": time(9, 0).isoformat(),
            "end_time": time(17, 0).isoformat(),
            "notes": "测试备注",
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=itinerary_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["start_time"] == "09:00:00"
        assert data["end_time"] == "17:00:00"
        assert data["notes"] == "测试备注"


class TestItineraryQuery:
    """行程查询测试"""

    @pytest_asyncio.fixture
    async def test_itinerary(self, test_db: AsyncSession, test_travel_plan: TravelPlan) -> Itinerary:
        """创建测试行程"""
        from datetime import date, time, timedelta

        itinerary_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": date.today() + timedelta(days=1),
            "location": "测试地点",
            "activity": "测试活动",
            "start_time": time(9, 0),
            "end_time": time(11, 0),
            "notes": "测试备注",
        }

        itinerary = Itinerary(**itinerary_data)
        test_db.add(itinerary)
        await test_db.commit()
        await test_db.refresh(itinerary)
        return itinerary

    def test_get_itineraries_by_plan_success(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, test_itinerary: Itinerary
    ):
        """测试获取旅行计划的行程列表成功"""
        response = client.get(f"/api/v1/itineraries/travel-plan/{test_travel_plan.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 验证包含测试行程
        itinerary_ids = [itinerary["id"] for itinerary in data]
        assert test_itinerary.id in itinerary_ids

    def test_get_itineraries_by_plan_unauthorized(self, client: TestClient, test_travel_plan: TravelPlan):
        """测试未认证获取行程列表"""
        response = client.get(f"/api/v1/itineraries/travel-plan/{test_travel_plan.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_itineraries_by_invalid_plan(self, client: TestClient, auth_headers: dict):
        """测试获取不存在旅行计划的行程列表"""
        response = client.get("/api/v1/itineraries/travel-plan/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_itinerary_by_id_success(self, client: TestClient, auth_headers: dict, test_itinerary: Itinerary):
        """测试通过ID获取行程详情成功"""
        response = client.get(f"/api/v1/itineraries/{test_itinerary.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_itinerary.id
        assert data["location"] == test_itinerary.location
        assert data["activity"] == test_itinerary.activity

    def test_get_itinerary_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """测试获取不存在的行程"""
        response = client.get("/api/v1/itineraries/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_itinerary_unauthorized(self, client: TestClient, test_itinerary: Itinerary):
        """测试未认证获取行程详情"""
        response = client.get(f"/api/v1/itineraries/{test_itinerary.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestItineraryUpdate:
    """行程更新测试"""

    @pytest_asyncio.fixture
    async def test_itinerary(self, test_db: AsyncSession, test_travel_plan: TravelPlan) -> Itinerary:
        """创建测试行程"""
        from datetime import date, time, timedelta

        itinerary_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": date.today() + timedelta(days=1),
            "location": "原始地点",
            "activity": "原始活动",
            "start_time": time(9, 0),
            "end_time": time(11, 0),
            "notes": "原始备注",
        }

        itinerary = Itinerary(**itinerary_data)
        test_db.add(itinerary)
        await test_db.commit()
        await test_db.refresh(itinerary)
        return itinerary

    def test_update_itinerary_success(self, client: TestClient, auth_headers: dict, test_itinerary: Itinerary):
        """测试更新行程成功"""
        update_data = {"location": "更新的地点", "activity": "更新的活动", "notes": "更新的备注"}
        response = client.put(f"/api/v1/itineraries/{test_itinerary.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["location"] == update_data["location"]
        assert data["activity"] == update_data["activity"]
        assert data["notes"] == update_data["notes"]

    def test_update_itinerary_partial(self, client: TestClient, auth_headers: dict, test_itinerary: Itinerary):
        """测试部分更新行程"""
        update_data = {"location": "仅更新地点"}
        response = client.put(f"/api/v1/itineraries/{test_itinerary.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["location"] == update_data["location"]
        # 其他字段应该保持不变
        assert data["activity"] == test_itinerary.activity

    def test_update_itinerary_with_time(self, client: TestClient, auth_headers: dict, test_itinerary: Itinerary):
        """测试更新行程时间"""
        from datetime import time

        update_data = {"start_time": time(14, 0).isoformat(), "end_time": time(16, 0).isoformat()}
        response = client.put(f"/api/v1/itineraries/{test_itinerary.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["start_time"] == "14:00:00"
        assert data["end_time"] == "16:00:00"

    def test_update_itinerary_not_found(self, client: TestClient, auth_headers: dict):
        """测试更新不存在的行程"""
        update_data = {"location": "更新不存在的行程"}
        response = client.put("/api/v1/itineraries/99999", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_itinerary_unauthorized(self, client: TestClient, test_itinerary: Itinerary):
        """测试未认证更新行程"""
        update_data = {"location": "未认证更新"}
        response = client.put(f"/api/v1/itineraries/{test_itinerary.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestItineraryDeletion:
    """行程删除测试"""

    @pytest_asyncio.fixture
    async def test_itinerary(self, test_db: AsyncSession, test_travel_plan: TravelPlan) -> Itinerary:
        """创建测试行程"""
        from datetime import date, timedelta

        itinerary_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": date.today() + timedelta(days=1),
            "location": "要删除的地点",
            "activity": "要删除的活动",
        }

        itinerary = Itinerary(**itinerary_data)
        test_db.add(itinerary)
        await test_db.commit()
        await test_db.refresh(itinerary)
        return itinerary

    def test_delete_itinerary_success(self, client: TestClient, auth_headers: dict, test_itinerary: Itinerary):
        """测试删除行程成功"""
        response = client.delete(f"/api/v1/itineraries/{test_itinerary.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

        # 验证行程已被删除
        get_response = client.get(f"/api/v1/itineraries/{test_itinerary.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_itinerary_not_found(self, client: TestClient, auth_headers: dict):
        """测试删除不存在的行程"""
        response = client.delete("/api/v1/itineraries/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_itinerary_unauthorized(self, client: TestClient, test_itinerary: Itinerary):
        """测试未认证删除行程"""
        response = client.delete(f"/api/v1/itineraries/{test_itinerary.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestItineraryValidation:
    """行程验证测试"""

    def test_negative_day_number(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试负数天数"""
        from datetime import date, timedelta

        invalid_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": -1,  # 无效的天数
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "location": "测试地点",
            "activity": "测试活动",
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_zero_day_number(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试零天数"""
        from datetime import date, timedelta

        invalid_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 0,  # 无效的天数
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "location": "测试地点",
            "activity": "测试活动",
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_location(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试空地点"""
        from datetime import date, timedelta

        invalid_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "location": "",  # 空地点
            "activity": "测试活动",
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_activity(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试空活动"""
        from datetime import date, timedelta

        invalid_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "location": "测试地点",
            "activity": "",  # 空活动
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_time_order(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试结束时间早于开始时间"""
        from datetime import date, time, timedelta

        invalid_data = {
            "travel_plan_id": test_travel_plan.id,
            "day_number": 1,
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "location": "测试地点",
            "activity": "测试活动",
            "start_time": time(17, 0).isoformat(),  # 结束时间
            "end_time": time(9, 0).isoformat(),  # 开始时间（无效顺序）
        }
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=invalid_data)

        # 根据业务逻辑，这可能在后端验证中被拦截
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestItineraryPermissions:
    """行程权限测试"""

    @pytest_asyncio.fixture
    async def other_user(self, test_db: AsyncSession) -> User:
        """创建另一个测试用户"""
        from app.core.security import get_password_hash

        user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "hashed_password": get_password_hash("otherpassword123"),
            "full_name": "其他用户",
            "is_active": True,
            "is_verified": True,
        }

        user = User(**user_data)
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest_asyncio.fixture
    async def other_user_travel_plan(self, test_db: AsyncSession, other_user: User) -> TravelPlan:
        """创建其他用户的旅行计划"""
        from datetime import date, timedelta

        from app.models.travel_plan import TravelStatus

        plan_data = {
            "title": "其他用户的计划",
            "description": "这是其他用户的旅行计划",
            "destination": "上海",
            "start_date": date.today() + timedelta(days=7),
            "end_date": date.today() + timedelta(days=14),
            "budget": 3000.00,
            "status": TravelStatus.PLANNING,
            "owner_id": other_user.id,
        }

        plan = TravelPlan(**plan_data)
        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)
        return plan

    def test_create_itinerary_for_other_user_plan(
        self, client: TestClient, auth_headers: dict, other_user_travel_plan: TravelPlan, sample_itinerary_data: dict
    ):
        """测试为其他用户的旅行计划创建行程（应该失败）"""
        sample_itinerary_data["travel_plan_id"] = other_user_travel_plan.id
        response = client.post("/api/v1/itineraries/", headers=auth_headers, json=sample_itinerary_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_user_plan_itineraries(
        self, client: TestClient, auth_headers: dict, other_user_travel_plan: TravelPlan
    ):
        """测试获取其他用户旅行计划的行程（应该失败）"""
        response = client.get(f"/api/v1/itineraries/travel-plan/{other_user_travel_plan.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestItineraryIntegration:
    """行程集成测试"""

    def test_itinerary_lifecycle(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_itinerary_data: dict
    ):
        """测试行程完整生命周期"""
        # 1. 创建行程
        sample_itinerary_data["travel_plan_id"] = test_travel_plan.id
        create_response = client.post("/api/v1/itineraries/", headers=auth_headers, json=sample_itinerary_data)
        assert create_response.status_code == status.HTTP_200_OK
        itinerary_id = create_response.json()["id"]

        # 2. 获取行程详情
        get_response = client.get(f"/api/v1/itineraries/{itinerary_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK

        # 3. 在旅行计划的行程列表中验证存在
        list_response = client.get(f"/api/v1/itineraries/travel-plan/{test_travel_plan.id}", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        itinerary_ids = [itinerary["id"] for itinerary in list_response.json()]
        assert itinerary_id in itinerary_ids

        # 4. 更新行程
        update_data = {"location": "更新后的地点", "activity": "更新后的活动"}
        update_response = client.put(f"/api/v1/itineraries/{itinerary_id}", headers=auth_headers, json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        # 5. 验证更新
        verify_response = client.get(f"/api/v1/itineraries/{itinerary_id}", headers=auth_headers)
        assert verify_response.status_code == status.HTTP_200_OK
        updated_data = verify_response.json()
        assert updated_data["location"] == update_data["location"]
        assert updated_data["activity"] == update_data["activity"]

        # 6. 删除行程
        delete_response = client.delete(f"/api/v1/itineraries/{itinerary_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK

        # 7. 验证已删除
        final_get_response = client.get(f"/api/v1/itineraries/{itinerary_id}", headers=auth_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_itineraries_ordering(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试多个行程的排序"""
        from datetime import date, time, timedelta

        # 创建多个行程
        itineraries_data = [
            {
                "travel_plan_id": test_travel_plan.id,
                "day_number": 2,
                "date": (date.today() + timedelta(days=2)).isoformat(),
                "location": "地点2",
                "activity": "活动2",
                "start_time": time(14, 0).isoformat(),
            },
            {
                "travel_plan_id": test_travel_plan.id,
                "day_number": 1,
                "date": (date.today() + timedelta(days=1)).isoformat(),
                "location": "地点1",
                "activity": "活动1",
                "start_time": time(9, 0).isoformat(),
            },
            {
                "travel_plan_id": test_travel_plan.id,
                "day_number": 1,
                "date": (date.today() + timedelta(days=1)).isoformat(),
                "location": "地点1-下午",
                "activity": "活动1-下午",
                "start_time": time(14, 0).isoformat(),
            },
        ]

        # 创建所有行程
        for itinerary_data in itineraries_data:
            response = client.post("/api/v1/itineraries/", headers=auth_headers, json=itinerary_data)
            assert response.status_code == status.HTTP_200_OK

        # 获取行程列表并验证排序
        list_response = client.get(f"/api/v1/itineraries/travel-plan/{test_travel_plan.id}", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK

        itineraries = list_response.json()
        assert len(itineraries) >= 3

        # 验证按天数和时间排序
        for i in range(len(itineraries) - 1):
            current = itineraries[i]
            next_item = itineraries[i + 1]

            # 当前天数应该小于等于下一个天数
            assert current["day_number"] <= next_item["day_number"]

            # 如果天数相同，时间应该按顺序排列
            if current["day_number"] == next_item["day_number"]:
                if current["start_time"] and next_item["start_time"]:
                    assert current["start_time"] <= next_item["start_time"]
