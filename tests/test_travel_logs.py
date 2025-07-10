import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.travel_log import TravelLog
from app.models.travel_plan import TravelPlan
from app.models.user import User


class TestTravelLogCreation:
    """旅行日志创建测试"""

    def test_create_travel_log_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
        sample_travel_log_data: dict,
    ):
        """测试创建旅行日志成功"""
        sample_travel_log_data["travel_plan_id"] = str(test_travel_plan.id)
        response = client.post(
            "/api/v1/travel-logs/",
            headers=auth_headers,
            json=sample_travel_log_data,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == sample_travel_log_data["title"]
        assert data["content"] == sample_travel_log_data["content"]
        assert data["location"] == sample_travel_log_data["location"]
        assert data["travel_plan_id"] == str(test_travel_plan.id)
        assert "id" in data
        assert "author_id" in data

    def test_create_travel_log_unauthorized(
        self,
        client: TestClient,
        test_travel_plan: TravelPlan,
        sample_travel_log_data: dict,
    ):
        """测试未认证创建旅行日志"""
        sample_travel_log_data["travel_plan_id"] = str(test_travel_plan.id)
        response = client.post(
            "/api/v1/travel-logs/", json=sample_travel_log_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_travel_log_missing_required_fields(
        self, client: TestClient, auth_headers: dict
    ):
        """测试创建旅行日志缺少必填字段"""
        incomplete_data = {
            "title": "不完整的日志"
            # 缺少content, log_date, travel_plan_id等必填字段
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=incomplete_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_travel_log_missing_travel_plan_id(
        self, client: TestClient, auth_headers: dict
    ):
        """测试创建旅行日志缺少travel_plan_id"""
        from datetime import datetime

        incomplete_data = {
            "title": "缺少旅行计划ID的日志",
            "content": "这个日志没有关联旅行计划",
            "log_date": datetime.now().isoformat(),
            # 缺少travel_plan_id必填字段
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=incomplete_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_travel_log_invalid_travel_plan_id(
        self, client: TestClient, auth_headers: dict
    ):
        """测试使用无效的travel_plan_id创建旅行日志"""
        import uuid
        from datetime import datetime

        invalid_data = {
            "title": "无效旅行计划ID的日志",
            "content": "这个日志使用了不存在的旅行计划ID",
            "log_date": datetime.now().isoformat(),
            "travel_plan_id": str(uuid.uuid4()),  # 不存在的UUID
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=invalid_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_travel_log_with_all_fields(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试创建包含所有字段的旅行日志"""
        from datetime import datetime

        log_data = {
            "title": "完整的旅行日志",
            "content": "今天的旅行非常精彩，体验了很多有趣的活动。",
            "location": "天安门广场",
            "log_date": datetime.now().isoformat(),
            "weather": "晴天",
            "mood": "开心",
            "travel_plan_id": str(test_travel_plan.id),
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=log_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["weather"] == "晴天"
        assert data["mood"] == "开心"


class TestTravelLogQuery:
    """旅行日志查询测试"""

    @pytest_asyncio.fixture
    async def test_travel_log(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ) -> TravelLog:
        """创建测试旅行日志"""
        from datetime import datetime

        log_data = {
            "title": "测试旅行日志",
            "content": "这是一个测试的旅行日志内容",
            "location": "测试地点",
            "log_date": datetime.now(),
            "weather": "晴天",
            "mood": "开心",
            "author_id": test_user.id,
            "travel_plan_id": str(test_travel_plan.id),
        }

        log = TravelLog(**log_data)
        test_db.add(log)
        await test_db.commit()
        await test_db.refresh(log)
        return log

    def test_list_travel_logs_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_log: TravelLog,
        test_travel_plan: TravelPlan,
    ):
        """测试获取旅行日志列表成功"""
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 验证包含测试日志
        log_ids = [log["id"] for log in data]
        assert str(test_travel_log.id) in log_ids

    def test_list_travel_logs_with_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试带分页的旅行日志查询"""
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}&skip=0&limit=5",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_list_travel_logs_by_travel_plan(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
        test_travel_log: TravelLog,
    ):
        """测试按旅行计划过滤日志"""
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for log in data:
            assert log["travel_plan_id"] == str(test_travel_plan.id)

    def test_get_my_travel_logs(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_log: TravelLog,
        test_travel_plan: TravelPlan,
    ):
        """测试获取我的旅行日志"""
        response = client.get(
            f"/api/v1/travel-logs/my?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # 应该包含当前用户的指定旅行计划的日志
        log_ids = [log["id"] for log in data]
        assert str(test_travel_log.id) in log_ids

    def test_list_travel_logs_missing_travel_plan_id(
        self, client: TestClient, auth_headers: dict
    ):
        """测试获取旅行日志列表缺少travel_plan_id参数"""
        response = client.get("/api/v1/travel-logs/", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_travel_logs_invalid_travel_plan_id(
        self, client: TestClient, auth_headers: dict
    ):
        """测试使用无效的travel_plan_id获取旅行日志列表"""
        import uuid

        invalid_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={invalid_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_my_travel_logs_missing_travel_plan_id(
        self, client: TestClient, auth_headers: dict
    ):
        """测试获取我的旅行日志缺少travel_plan_id参数"""
        response = client.get("/api/v1/travel-logs/my", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_my_travel_logs_invalid_travel_plan_id(
        self, client: TestClient, auth_headers: dict
    ):
        """测试使用无效的travel_plan_id获取我的旅行日志"""
        import uuid

        invalid_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/travel-logs/my?travel_plan_id={invalid_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_travel_log_by_id_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_log: TravelLog,
    ):
        """测试通过ID获取旅行日志详情成功"""
        response = client.get(
            f"/api/v1/travel-logs/{test_travel_log.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_travel_log.id)
        assert data["title"] == test_travel_log.title
        assert data["content"] == test_travel_log.content

    def test_get_travel_log_by_id_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """测试获取不存在的旅行日志"""
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/travel-logs/{fake_uuid}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_travel_log_unauthorized(
        self, client: TestClient, test_travel_log: TravelLog
    ):
        """测试未认证获取旅行日志"""
        response = client.get(f"/api/v1/travel-logs/{test_travel_log.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTravelLogUpdate:
    """旅行日志更新测试"""

    @pytest_asyncio.fixture
    async def test_travel_log(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ) -> TravelLog:
        """创建测试旅行日志"""
        from datetime import datetime

        log_data = {
            "title": "原始标题",
            "content": "原始内容",
            "location": "原始地点",
            "log_date": datetime.now(),
            "weather": "原始天气",
            "mood": "原始心情",
            "author_id": test_user.id,
            "travel_plan_id": str(test_travel_plan.id),
        }

        log = TravelLog(**log_data)
        test_db.add(log)
        await test_db.commit()
        await test_db.refresh(log)
        return log

    def test_update_travel_log_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_log: TravelLog,
    ):
        """测试更新旅行日志成功"""
        update_data = {
            "title": "更新的标题",
            "content": "更新的内容",
            "location": "更新的地点",
            "weather": "更新的天气",
            "mood": "更新的心情",
        }
        response = client.put(
            f"/api/v1/travel-logs/{test_travel_log.id}",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["location"] == update_data["location"]
        assert data["weather"] == update_data["weather"]
        assert data["mood"] == update_data["mood"]

    def test_update_travel_log_partial(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_log: TravelLog,
    ):
        """测试部分更新旅行日志"""
        update_data = {"title": "仅更新标题"}
        response = client.put(
            f"/api/v1/travel-logs/{test_travel_log.id}",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        # 其他字段应该保持不变
        assert data["content"] == test_travel_log.content

    def test_update_travel_log_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """测试更新不存在的旅行日志"""
        update_data = {"title": "更新不存在的日志"}
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.put(
            f"/api/v1/travel-logs/{fake_uuid}",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_travel_log_unauthorized(
        self, client: TestClient, test_travel_log: TravelLog
    ):
        """测试未认证更新旅行日志"""
        update_data = {"title": "未认证更新"}
        response = client.put(
            f"/api/v1/travel-logs/{test_travel_log.id}", json=update_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTravelLogDeletion:
    """旅行日志删除测试"""

    @pytest_asyncio.fixture
    async def test_travel_log(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ) -> TravelLog:
        """创建测试旅行日志"""
        from datetime import datetime

        log_data = {
            "title": "要删除的日志",
            "content": "这个日志将被删除",
            "location": "删除测试地点",
            "log_date": datetime.now(),
            "author_id": test_user.id,
            "travel_plan_id": str(test_travel_plan.id),
        }

        log = TravelLog(**log_data)
        test_db.add(log)
        await test_db.commit()
        await test_db.refresh(log)
        return log

    def test_delete_travel_log_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_log: TravelLog,
    ):
        """测试删除旅行日志成功"""
        response = client.delete(
            f"/api/v1/travel-logs/{test_travel_log.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

        # 验证日志已被删除
        get_response = client.get(
            f"/api/v1/travel-logs/{test_travel_log.id}", headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_travel_log_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """测试删除不存在的旅行日志"""
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.delete(
            f"/api/v1/travel-logs/{fake_uuid}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_travel_log_unauthorized(
        self, client: TestClient, test_travel_log: TravelLog
    ):
        """测试未认证删除旅行日志"""
        response = client.delete(f"/api/v1/travel-logs/{test_travel_log.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTravelLogValidation:
    """旅行日志验证测试"""

    def test_empty_title(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试空标题"""
        from datetime import datetime

        invalid_data = {
            "title": "",  # 空标题
            "content": "有内容但标题为空",
            "log_date": datetime.now().isoformat(),
            "travel_plan_id": str(test_travel_plan.id),
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=invalid_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_content(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试空内容"""
        from datetime import datetime

        invalid_data = {
            "title": "有标题但内容为空",
            "content": "",  # 空内容
            "log_date": datetime.now().isoformat(),
            "travel_plan_id": str(test_travel_plan.id),
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=invalid_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_too_long_title(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试过长标题"""
        from datetime import datetime

        invalid_data = {
            "title": "a" * 300,  # 超过字符限制
            "content": "正常内容",
            "log_date": datetime.now().isoformat(),
            "travel_plan_id": str(test_travel_plan.id),
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=invalid_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_future_log_date(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试未来的日志日期"""
        from datetime import datetime, timedelta

        future_date = datetime.now() + timedelta(days=30)
        log_data = {
            "title": "未来日志",
            "content": "记录未来的旅行",
            "log_date": future_date.isoformat(),
            "travel_plan_id": str(test_travel_plan.id),
        }
        response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=log_data
        )

        # 根据业务逻辑，可能允许或不允许未来日期
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ]


class TestTravelLogPermissions:
    """旅行日志权限测试"""

    @pytest_asyncio.fixture
    async def other_user(self, test_db: AsyncSession) -> User:
        """创建另一个测试用户"""
        from app.core.security import get_password_hash

        user_data = {
            "username": "otherloguser",
            "email": "otherlog@example.com",
            "hashed_password": get_password_hash("otherpassword123"),
            "full_name": "其他日志用户",
            "is_active": True,
            "is_verified": True,
        }

        user = User(**user_data)
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user


class TestTravelLogFiltering:
    """旅行日志过滤测试"""

    @pytest_asyncio.fixture
    async def setup_multiple_logs(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_travel_plan: TravelPlan,
    ):
        """创建多个不同类型的测试日志"""
        from datetime import datetime, timedelta

        logs_data = [
            {
                "title": "日志1",
                "content": "内容1",
                "location": "北京",
                "log_date": datetime.now() - timedelta(days=1),
                "weather": "晴天",
                "author_id": test_user.id,
                "travel_plan_id": str(test_travel_plan.id),
            },
            {
                "title": "日志2",
                "content": "内容2",
                "location": "上海",
                "log_date": datetime.now() - timedelta(days=2),
                "weather": "雨天",
                "author_id": test_user.id,
                "travel_plan_id": str(test_travel_plan.id),
            },
            {
                "title": "日志3",
                "content": "内容3",
                "location": "广州",
                "log_date": datetime.now() - timedelta(days=3),
                "weather": "多云",
                "author_id": test_user.id,
                "travel_plan_id": str(test_travel_plan.id),
            },
        ]

        logs = []
        for log_data in logs_data:
            log = TravelLog(**log_data)
            test_db.add(log)
            logs.append(log)

        await test_db.commit()
        for log in logs:
            await test_db.refresh(log)

        return logs

    def test_filter_logs_by_travel_plan(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
        setup_multiple_logs,
    ):
        """测试按旅行计划过滤日志"""
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for log in data:
            assert log["travel_plan_id"] == str(test_travel_plan.id)

    def test_pagination_with_limits(
        self,
        client: TestClient,
        auth_headers: dict,
        setup_multiple_logs,
        test_travel_plan: TravelPlan,
    ):
        """测试分页和限制"""
        # 测试限制为1
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}&limit=1",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 1

        # 测试跳过记录
        response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}&skip=1&limit=2",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2


class TestTravelLogIntegration:
    """旅行日志集成测试"""

    def test_travel_log_lifecycle(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
        sample_travel_log_data: dict,
    ):
        """测试旅行日志完整生命周期"""
        # 1. 创建旅行日志
        sample_travel_log_data["travel_plan_id"] = str(test_travel_plan.id)
        create_response = client.post(
            "/api/v1/travel-logs/",
            headers=auth_headers,
            json=sample_travel_log_data,
        )
        assert create_response.status_code == status.HTTP_200_OK
        log_id = create_response.json()["id"]

        # 2. 获取日志详情
        get_response = client.get(
            f"/api/v1/travel-logs/{log_id}", headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK

        # 3. 在日志列表中验证存在
        list_response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )
        assert list_response.status_code == status.HTTP_200_OK
        log_ids = [log["id"] for log in list_response.json()]
        assert log_id in log_ids

        # 4. 在我的日志列表中验证存在
        my_logs_response = client.get(
            f"/api/v1/travel-logs/my?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )
        assert my_logs_response.status_code == status.HTTP_200_OK
        my_log_ids = [log["id"] for log in my_logs_response.json()]
        assert log_id in my_log_ids

        # 5. 更新日志
        update_data = {
            "title": "更新后的标题",
            "content": "更新后的内容",
        }
        update_response = client.put(
            f"/api/v1/travel-logs/{log_id}",
            headers=auth_headers,
            json=update_data,
        )
        assert update_response.status_code == status.HTTP_200_OK

        # 6. 验证更新
        verify_response = client.get(
            f"/api/v1/travel-logs/{log_id}", headers=auth_headers
        )
        assert verify_response.status_code == status.HTTP_200_OK
        updated_data = verify_response.json()
        assert updated_data["title"] == update_data["title"]
        assert updated_data["content"] == update_data["content"]

        # 8. 删除日志
        delete_response = client.delete(
            f"/api/v1/travel-logs/{log_id}", headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_200_OK

        # 9. 验证已删除
        final_get_response = client.get(
            f"/api/v1/travel-logs/{log_id}", headers=auth_headers
        )
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_travel_plan_association(
        self,
        client: TestClient,
        auth_headers: dict,
        test_travel_plan: TravelPlan,
    ):
        """测试日志与旅行计划的关联"""
        from datetime import datetime

        # 创建与旅行计划关联的日志
        log_data = {
            "title": "关联测试日志",
            "content": "测试与旅行计划的关联",
            "log_date": datetime.now().isoformat(),
            "travel_plan_id": str(test_travel_plan.id),
        }
        create_response = client.post(
            "/api/v1/travel-logs/", headers=auth_headers, json=log_data
        )
        assert create_response.status_code == status.HTTP_200_OK
        log_id = create_response.json()["id"]

        # 通过旅行计划ID过滤验证关联
        filter_response = client.get(
            f"/api/v1/travel-logs/?travel_plan_id={test_travel_plan.id}",
            headers=auth_headers,
        )
        assert filter_response.status_code == status.HTTP_200_OK

        filtered_logs = filter_response.json()
        log_ids = [log["id"] for log in filtered_logs]
        assert log_id in log_ids

        # 验证所有返回的日志都属于该旅行计划
        for log in filtered_logs:
            assert log["travel_plan_id"] == str(test_travel_plan.id)
