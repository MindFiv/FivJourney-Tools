import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User


class TestUserProfile:
    """用户资料相关测试"""

    def test_get_current_user_success(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """测试获取当前用户信息成功"""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "hashed_password" not in data  # 确保不返回密码

    def test_get_current_user_unauthorized(self, client: TestClient):
        """测试未认证获取用户信息"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client: TestClient):
        """测试使用无效token获取用户信息"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile_success(
        self, client: TestClient, auth_headers: dict
    ):
        """测试更新用户资料成功"""
        update_data = {
            "full_name": "更新的全名",
            "phone": "13900000000",
            "bio": "更新的个人简介",
        }
        response = client.put(
            "/api/v1/users/me", headers=auth_headers, json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone"] == update_data["phone"]
        assert data["bio"] == update_data["bio"]

    def test_update_user_profile_partial(
        self, client: TestClient, auth_headers: dict
    ):
        """测试部分更新用户资料"""
        update_data = {"full_name": "仅更新全名"}
        response = client.put(
            "/api/v1/users/me", headers=auth_headers, json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]

    def test_update_user_profile_unauthorized(self, client: TestClient):
        """测试未认证更新用户资料"""
        update_data = {"full_name": "新全名"}
        response = client.put("/api/v1/users/me", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile_readonly_fields(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """测试更新只读字段（应该被忽略）"""
        original_username = test_user.username
        original_email = test_user.email

        update_data = {
            "username": "new_username",  # 只读字段
            "email": "new@example.com",  # 只读字段
            "id": 999,  # 只读字段
            "full_name": "新的全名",
        }
        response = client.put(
            "/api/v1/users/me", headers=auth_headers, json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == original_username  # 用户名不应该改变
        assert data["email"] == original_email  # 邮箱不应该改变
        assert data["id"] == str(test_user.id)  # ID不应该改变
        assert (
            data["full_name"] == update_data["full_name"]
        )  # 允许更新的字段应该改变


class TestUserValidation:
    """用户数据验证测试"""

    @pytest.mark.parametrize(
        "phone",
        [
            "1234567890123456789012345678901",  # 太长
            "abc123",  # 包含非数字字符
            "123",  # 太短
        ],
    )
    def test_update_invalid_phone(
        self, client: TestClient, auth_headers: dict, phone: str
    ):
        """测试更新无效电话号码"""
        update_data = {"phone": phone}
        response = client.put(
            "/api/v1/users/me", headers=auth_headers, json=update_data
        )

        # 根据具体的验证规则，可能返回400或422
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_update_empty_full_name(
        self, client: TestClient, auth_headers: dict
    ):
        """测试更新空的全名"""
        update_data = {"full_name": ""}
        response = client.put(
            "/api/v1/users/me", headers=auth_headers, json=update_data
        )

        # 应该允许空的全名或返回验证错误
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_update_too_long_bio(self, client: TestClient, auth_headers: dict):
        """测试更新过长的个人简介"""
        update_data = {"bio": "a" * 1000}  # 假设bio有长度限制
        response = client.put(
            "/api/v1/users/me", headers=auth_headers, json=update_data
        )

        # 根据具体的验证规则，可能成功或失败
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]


class TestUserQueries:
    """用户查询测试"""

    def test_get_user_by_id_success(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """测试通过ID获取用户信息成功"""
        response = client.get(
            f"/api/v1/users/{test_user.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["username"] == test_user.username
        assert "hashed_password" not in data

    def test_get_user_by_id_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """测试获取不存在的用户"""
        import uuid

        fake_uuid = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/users/{fake_uuid}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_by_id_unauthorized(
        self, client: TestClient, test_user: User
    ):
        """测试未认证获取用户信息"""
        response = client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserSecurity:
    """用户安全性测试"""

    def test_user_response_no_sensitive_data(
        self, client: TestClient, auth_headers: dict
    ):
        """测试用户响应不包含敏感数据"""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 确保敏感字段不在响应中
        sensitive_fields = ["hashed_password", "password"]
        for field in sensitive_fields:
            assert field not in data

    def test_inactive_user_cannot_access_profile(
        self, client: TestClient, test_inactive_user: User
    ):
        """测试非活跃用户无法访问资料"""
        from app.core.security import create_access_token

        # 为非活跃用户创建token
        token = create_access_token(data={"sub": test_inactive_user.username})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户已被禁用" in response.json()["detail"]


class TestUserIntegration:
    """用户集成测试"""

    def test_user_lifecycle(self, client: TestClient, sample_user_data: dict):
        """测试用户完整生命周期"""
        # 1. 注册用户
        register_response = client.post(
            "/api/v1/auth/register", json=sample_user_data
        )
        assert register_response.status_code == status.HTTP_200_OK
        user_id = register_response.json()["id"]

        # 2. 登录用户
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        }
        login_response = client.post(
            "/api/v1/auth/login-json", json=login_data
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. 获取用户资料
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK

        # 4. 更新用户资料
        update_data = {"full_name": "更新后的姓名", "bio": "更新后的简介"}
        update_response = client.put(
            "/api/v1/users/me", headers=headers, json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        # 5. 验证更新后的资料
        verify_response = client.get("/api/v1/users/me", headers=headers)
        assert verify_response.status_code == status.HTTP_200_OK
        updated_data = verify_response.json()
        assert updated_data["full_name"] == update_data["full_name"]
        assert updated_data["bio"] == update_data["bio"]

        # 6. 通过ID获取用户（如果有此端点）
        by_id_response = client.get(
            f"/api/v1/users/{user_id}", headers=headers
        )
        if (
            by_id_response.status_code != status.HTTP_404_NOT_FOUND
        ):  # 如果端点存在
            assert by_id_response.status_code == status.HTTP_200_OK
            by_id_data = by_id_response.json()
            assert by_id_data["id"] == user_id
