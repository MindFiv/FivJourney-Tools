import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.travel_plan import TravelPlan


class TestTravelPlanCreation:
    """旅行计划创建测试"""

    def test_create_travel_plan_success(self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict):
        """测试创建旅行计划成功"""
        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == sample_travel_plan_data["title"]
        assert data["description"] == sample_travel_plan_data["description"]
        assert data["destination"] == sample_travel_plan_data["destination"]
        assert float(data["budget"]) == sample_travel_plan_data["budget"]
        assert data["status"] == "planning"  # 默认状态
        assert "id" in data
        assert "owner_id" in data

    def test_create_travel_plan_unauthorized(self, client: TestClient, sample_travel_plan_data: dict):
        """测试未认证创建旅行计划"""
        response = client.post("/api/v1/travel-plans/", json=sample_travel_plan_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_travel_plan_missing_required_fields(self, client: TestClient, auth_headers: dict):
        """测试创建旅行计划缺少必填字段"""
        incomplete_data = {
            "title": "不完整的计划"
            # 缺少destination, start_date, end_date
        }
        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_travel_plan_invalid_dates(
        self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict
    ):
        """测试创建旅行计划日期无效（结束日期早于开始日期）"""
        from datetime import date, timedelta

        sample_travel_plan_data["start_date"] = (date.today() + timedelta(days=10)).isoformat()
        sample_travel_plan_data["end_date"] = (date.today() + timedelta(days=5)).isoformat()  # 结束日期早于开始日期

        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_travel_plan_negative_budget(
        self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict
    ):
        """测试创建旅行计划预算为负数"""
        sample_travel_plan_data["budget"] = -1000.00
        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTravelPlanQuery:
    """旅行计划查询测试"""

    def test_get_travel_plans_success(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试获取用户旅行计划列表成功"""
        response = client.get("/api/v1/travel-plans/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 验证包含测试旅行计划
        plan_ids = [plan["id"] for plan in data]
        assert str(test_travel_plan.id) in plan_ids

    def test_get_travel_plan_by_id_success(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试通过ID获取旅行计划成功"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_travel_plan.id)
        assert data["title"] == test_travel_plan.title
        assert data["destination"] == test_travel_plan.destination

    def test_get_travel_plan_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """测试获取不存在的旅行计划"""
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.get(f"/api/v1/travel-plans/{fake_uuid}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_travel_plan_unauthorized(self, client: TestClient, test_travel_plan: TravelPlan):
        """测试未认证获取旅行计划"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_other_user_travel_plan(self, client: TestClient, auth_headers: dict, test_db: AsyncSession):
        """测试获取其他用户的旅行计划（应该失败）"""
        # 这个测试需要创建另一个用户和他的旅行计划
        # 实际实现取决于是否允许查看其他用户的计划


class TestTravelPlanUpdate:
    """旅行计划更新测试"""

    def test_update_travel_plan_success(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试更新旅行计划成功"""
        update_data = {"title": "更新的旅行计划", "description": "更新的描述", "budget": 6000.00}
        response = client.put(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert float(data["budget"]) == update_data["budget"]

    def test_update_travel_plan_partial(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试部分更新旅行计划"""
        update_data = {"title": "仅更新标题"}
        response = client.put(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]

    def test_update_travel_plan_not_found(self, client: TestClient, auth_headers: dict):
        """测试更新不存在的旅行计划"""
        update_data = {"title": "更新不存在的计划"}
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.put(f"/api/v1/travel-plans/{fake_uuid}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_travel_plan_unauthorized(self, client: TestClient, test_travel_plan: TravelPlan):
        """测试未认证更新旅行计划"""
        update_data = {"title": "未认证更新"}
        response = client.put(f"/api/v1/travel-plans/{test_travel_plan.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_travel_plan_status(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试更新旅行计划状态"""
        update_data = {"status": "confirmed"}
        response = client.put(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "confirmed"

    def test_update_travel_plan_invalid_status(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan
    ):
        """测试更新旅行计划为无效状态"""
        update_data = {"status": "invalid_status"}
        response = client.put(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTravelPlanDeletion:
    """旅行计划删除测试"""

    def test_delete_travel_plan_success(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试删除旅行计划成功"""
        response = client.delete(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        # 验证计划已被删除
        get_response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_travel_plan_not_found(self, client: TestClient, auth_headers: dict):
        """测试删除不存在的旅行计划"""
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.delete(f"/api/v1/travel-plans/{fake_uuid}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_travel_plan_unauthorized(self, client: TestClient, test_travel_plan: TravelPlan):
        """测试未认证删除旅行计划"""
        response = client.delete(f"/api/v1/travel-plans/{test_travel_plan.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTravelPlanValidation:
    """旅行计划验证测试"""

    @pytest.mark.parametrize("status_value", ["planning", "confirmed", "in_progress", "completed", "cancelled"])
    def test_valid_status_values(
        self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict, status_value: str
    ):
        """测试有效的状态值"""
        sample_travel_plan_data["status"] = status_value
        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        # 根据业务逻辑，创建时可能只允许某些状态
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_empty_title(self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict):
        """测试空标题"""
        sample_travel_plan_data["title"] = ""
        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_too_long_title(self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict):
        """测试过长标题"""
        sample_travel_plan_data["title"] = "a" * 300  # 超过200字符限制
        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_past_dates(self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict):
        """测试过去的日期"""
        from datetime import date, timedelta

        sample_travel_plan_data["start_date"] = (date.today() - timedelta(days=10)).isoformat()
        sample_travel_plan_data["end_date"] = (date.today() - timedelta(days=5)).isoformat()

        response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)

        # 根据业务逻辑，可能允许或不允许过去的日期
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestTravelPlanFiltering:
    """旅行计划过滤测试"""

    def test_filter_by_status(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试按状态过滤旅行计划"""
        response = client.get("/api/v1/travel-plans/?status=planning", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # 验证所有返回的计划都是planning状态
        for plan in data:
            assert plan["status"] == "planning"

    def test_filter_by_destination(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试按目的地过滤旅行计划"""
        response = client.get(f"/api/v1/travel-plans/?destination={test_travel_plan.destination}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # 验证所有返回的计划都有正确的目的地
        for plan in data:
            assert plan["destination"] == test_travel_plan.destination

    def test_pagination(self, client: TestClient, auth_headers: dict):
        """测试分页"""
        response = client.get("/api/v1/travel-plans/?page=1&size=10", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        # 根据实际API设计验证分页响应格式


class TestTravelPlanIntegration:
    """旅行计划集成测试"""

    def test_travel_plan_lifecycle(self, client: TestClient, auth_headers: dict, sample_travel_plan_data: dict):
        """测试旅行计划完整生命周期"""
        # 1. 创建旅行计划
        create_response = client.post("/api/v1/travel-plans/", headers=auth_headers, json=sample_travel_plan_data)
        assert create_response.status_code == status.HTTP_200_OK
        plan_id = create_response.json()["id"]

        # 2. 获取旅行计划
        get_response = client.get(f"/api/v1/travel-plans/{plan_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK

        # 3. 更新旅行计划
        update_data = {"title": "更新后的标题", "status": "confirmed"}
        update_response = client.put(f"/api/v1/travel-plans/{plan_id}", headers=auth_headers, json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        # 4. 验证更新
        verify_response = client.get(f"/api/v1/travel-plans/{plan_id}", headers=auth_headers)
        assert verify_response.status_code == status.HTTP_200_OK
        updated_data = verify_response.json()
        assert updated_data["title"] == update_data["title"]
        assert updated_data["status"] == update_data["status"]

        # 5. 在列表中验证存在
        list_response = client.get("/api/v1/travel-plans/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        plan_ids = [plan["id"] for plan in list_response.json()]
        assert plan_id in plan_ids

        # 6. 删除旅行计划
        delete_response = client.delete(f"/api/v1/travel-plans/{plan_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK

        # 7. 验证已删除
        final_get_response = client.get(f"/api/v1/travel-plans/{plan_id}", headers=auth_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
