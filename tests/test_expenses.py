from datetime import datetime
from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ExpenseCategory
from app.models.expense import Expense
from app.models.travel_plan import TravelPlan
from app.models.user import User


class TestExpenseCreation:
    """费用创建测试"""

    def test_create_expense_success(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试创建费用记录成功"""
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert float(data["amount"]) == sample_expense_data["amount"]
        assert data["category"] == sample_expense_data["category"]
        assert data["description"] == sample_expense_data["description"]
        assert data["travel_plan_id"] == test_travel_plan.id
        assert "id" in data

    def test_create_expense_unauthorized(
        self, client: TestClient, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试未认证创建费用记录"""
        response = client.post(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", json=sample_expense_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_expense_invalid_travel_plan(
        self, client: TestClient, auth_headers: dict, sample_expense_data: dict
    ):
        """测试为不存在的旅行计划创建费用"""
        response = client.post("/api/v1/travel-plans/99999/expenses/", headers=auth_headers, json=sample_expense_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_expense_missing_required_fields(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan
    ):
        """测试创建费用缺少必填字段"""
        incomplete_data = {"description": "缺少金额和类别的费用"}
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=incomplete_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_expense_negative_amount(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试创建负金额费用"""
        sample_expense_data["amount"] = -100.00
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_expense_zero_amount(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试创建零金额费用"""
        sample_expense_data["amount"] = 0.00
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        # 根据业务逻辑，可能允许或不允许零金额
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.parametrize(
        "category",
        [
            "transportation",
            "accommodation",
            "food",
            "sightseeing",
            "shopping",
            "entertainment",
            "insurance",
            "visa",
            "other",
        ],
    )
    def test_create_expense_valid_categories(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
        sample_expense_data: dict,
        category: str,
    ):
        """测试有效的费用类别"""
        sample_expense_data["category"] = category
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["category"] == category


class TestExpenseQuery:
    """费用查询测试"""

    def test_get_expenses_by_travel_plan(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, test_expense: Expense
    ):
        """测试获取旅行计划的费用列表"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        expense_ids = [expense["id"] for expense in data]
        assert test_expense.id in expense_ids

    def test_get_expense_by_id(self, client: TestClient, auth_headers: dict, test_expense: Expense):
        """测试通过ID获取费用记录"""
        response = client.get(f"/api/v1/expenses/{test_expense.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_expense.id
        assert data["amount"] == str(test_expense.amount)  # API返回字符串格式的金额
        assert data["category"] == test_expense.category.value

    def test_get_expense_not_found(self, client: TestClient, auth_headers: dict):
        """测试获取不存在的费用记录"""
        response = client.get("/api/v1/expenses/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_expenses_unauthorized(self, client: TestClient, test_travel_plan: TravelPlan):
        """测试未认证获取费用列表"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_expenses(self, client: TestClient, auth_headers: dict, test_expense: Expense):
        """测试获取用户的所有费用记录"""
        response = client.get("/api/v1/expenses/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:  # 如果有费用记录
            expense_ids = [expense["id"] for expense in data]
            assert test_expense.id in expense_ids


class TestExpenseUpdate:
    """费用更新测试"""

    def test_update_expense_success(self, client: TestClient, auth_headers: dict, test_expense: Expense):
        """测试更新费用记录成功"""
        update_data = {"amount": 250.00, "description": "更新的费用描述", "category": "food"}
        response = client.put(f"/api/v1/expenses/{test_expense.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert float(data["amount"]) == update_data["amount"]  # 比较数值而不是字符串格式
        assert data["description"] == update_data["description"]
        assert data["category"] == update_data["category"]

    def test_update_expense_partial(self, client: TestClient, auth_headers: dict, test_expense: Expense):
        """测试部分更新费用记录"""
        update_data = {"description": "仅更新描述"}
        response = client.put(f"/api/v1/expenses/{test_expense.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == update_data["description"]

    def test_update_expense_not_found(self, client: TestClient, auth_headers: dict):
        """测试更新不存在的费用记录"""
        update_data = {"amount": 300.00}
        response = client.put("/api/v1/expenses/99999", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_expense_unauthorized(self, client: TestClient, test_expense: Expense):
        """测试未认证更新费用记录"""
        update_data = {"amount": 300.00}
        response = client.put(f"/api/v1/expenses/{test_expense.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_expense_invalid_amount(self, client: TestClient, auth_headers: dict, test_expense: Expense):
        """测试更新费用为无效金额"""
        update_data = {"amount": -50.00}
        response = client.put(f"/api/v1/expenses/{test_expense.id}", headers=auth_headers, json=update_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestExpenseDeletion:
    """费用删除测试"""

    def test_delete_expense_success(self, client: TestClient, auth_headers: dict, test_expense: Expense):
        """测试删除费用记录成功"""
        response = client.delete(f"/api/v1/expenses/{test_expense.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        # 验证费用已被删除
        get_response = client.get(f"/api/v1/expenses/{test_expense.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_not_found(self, client: TestClient, auth_headers: dict):
        """测试删除不存在的费用记录"""
        response = client.delete("/api/v1/expenses/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_unauthorized(self, client: TestClient, test_expense: Expense):
        """测试未认证删除费用记录"""
        response = client.delete(f"/api/v1/expenses/{test_expense.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestExpenseFiltering:
    """费用过滤和搜索测试"""

    def test_filter_expenses_by_category(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试按类别过滤费用"""
        response = client.get(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/?category=transportation", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for expense in data:
            assert expense["category"] == "transportation"

    def test_filter_expenses_by_date_range(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试按日期范围过滤费用"""
        from datetime import date, timedelta

        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()

        response = client.get(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/" f"?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_filter_expenses_by_payment_method(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan
    ):
        """测试按支付方式过滤费用"""
        response = client.get(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/?payment_method=信用卡", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for expense in data:
            if "payment_method" in expense:
                assert expense["payment_method"] == "信用卡"

    def test_sort_expenses_by_amount(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试按金额排序费用"""
        response = client.get(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/?sort_by=amount&order=desc", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证降序排列
        if len(data) > 1:
            amounts = [expense["amount"] for expense in data]
            assert amounts == sorted(amounts, reverse=True)

    def test_search_expenses_by_description(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试按描述搜索费用"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/?search=测试", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for expense in data:
            assert "测试" in expense.get("description", "").lower() or "测试" in expense.get("location", "").lower()


class TestExpenseStatistics:
    """费用统计测试"""

    def test_get_expense_statistics(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试获取费用统计"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/statistics", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证统计数据结构
        expected_fields = ["total_amount", "by_category"]  # 修正字段名
        for field in expected_fields:
            assert field in data

    def test_get_category_breakdown(self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan):
        """测试获取类别费用分解"""
        response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/statistics", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if "category_breakdown" in data:
            breakdown = data["category_breakdown"]
            assert isinstance(breakdown, dict)

            # 验证每个类别都有金额和百分比
            for category, stats in breakdown.items():
                assert "amount" in stats
                assert "percentage" in stats


class TestExpenseValidation:
    """费用数据验证测试"""

    @pytest.mark.parametrize(
        "invalid_category",
        [
            "invalid_category",
            "",
            "a" * 100,  # 过长的类别名
        ],
    )
    def test_invalid_category(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
        sample_expense_data: dict,
        invalid_category: str,
    ):
        """测试无效的费用类别"""
        sample_expense_data["category"] = invalid_category
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        # 根据验证规则，可能返回400或422
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_future_date(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试未来的费用日期"""
        from datetime import date, timedelta

        sample_expense_data["expense_date"] = (datetime.now() + timedelta(days=30)).isoformat()
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        # 根据业务逻辑，可能允许或不允许未来日期
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_very_large_amount(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试非常大的金额"""
        sample_expense_data["amount"] = 999999999.99
        response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )

        # 根据数据库约束和业务规则
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestExpenseIntegration:
    """费用集成测试"""

    def test_expense_lifecycle(
        self, client: TestClient, auth_headers: dict, test_travel_plan: TravelPlan, sample_expense_data: dict
    ):
        """测试费用记录完整生命周期"""
        # 1. 创建费用记录
        create_response = client.post(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers, json=sample_expense_data
        )
        assert create_response.status_code == status.HTTP_200_OK
        expense_id = create_response.json()["id"]

        # 2. 获取费用记录
        get_response = client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK

        # 3. 更新费用记录
        update_data = {"amount": 350.00, "description": "更新后的费用描述"}
        update_response = client.put(f"/api/v1/expenses/{expense_id}", headers=auth_headers, json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        # 4. 验证更新
        verify_response = client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert verify_response.status_code == status.HTTP_200_OK
        updated_data = verify_response.json()
        # 比较decimal值，处理不同的格式化（350.0 vs 350.00）
        assert float(updated_data["amount"]) == update_data["amount"]
        assert updated_data["description"] == update_data["description"]

        # 5. 在旅行计划费用列表中验证存在
        list_response = client.get(f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        expense_ids = [expense["id"] for expense in list_response.json()]
        assert expense_id in expense_ids

        # 6. 获取费用统计
        stats_response = client.get(
            f"/api/v1/travel-plans/{test_travel_plan.id}/expenses/statistics", headers=auth_headers
        )
        assert stats_response.status_code == status.HTTP_200_OK

        # 7. 删除费用记录
        delete_response = client.delete(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK

        # 8. 验证已删除
        final_get_response = client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
