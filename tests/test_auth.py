import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.security import create_access_token, verify_password
from app.models.user import User


class TestAuth:
    """认证相关测试"""

    def test_register_success(self, client: TestClient, sample_user_data: dict):
        """测试用户注册成功"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "hashed_password" not in data  # 确保不返回密码
        assert "id" in data
        assert data["is_active"] is True

    def test_register_duplicate_username(self, client: TestClient, test_user: User, sample_user_data: dict):
        """测试注册重复用户名"""
        sample_user_data["username"] = test_user.username
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名已存在" in response.json()["detail"]

    def test_register_duplicate_email(self, client: TestClient, test_user: User, sample_user_data: dict):
        """测试注册重复邮箱"""
        sample_user_data["email"] = test_user.email
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "邮箱已被注册" in response.json()["detail"]

    def test_register_invalid_data(self, client: TestClient):
        """测试注册无效数据"""
        invalid_data = {
            "username": "",  # 空用户名
            "email": "invalid-email",  # 无效邮箱
            "password": "123",  # 密码太短
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client: TestClient, test_user: User):
        """测试用户登录成功"""
        login_data = {"username": test_user.username, "password": "testpassword123"}
        response = client.post("/api/v1/auth/login-json", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == test_user.username

    def test_login_invalid_username(self, client: TestClient):
        """测试登录无效用户名"""
        login_data = {"username": "nonexistent", "password": "testpassword123"}
        response = client.post("/api/v1/auth/login-json", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "用户名或密码错误" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """测试登录无效密码"""
        login_data = {"username": test_user.username, "password": "wrongpassword"}
        response = client.post("/api/v1/auth/login-json", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "用户名或密码错误" in response.json()["detail"]

    def test_login_inactive_user(self, client: TestClient, test_inactive_user: User):
        """测试登录非活跃用户"""
        login_data = {"username": test_inactive_user.username, "password": "testpassword123"}
        response = client.post("/api/v1/auth/login-json", json=login_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户账户已被禁用" in response.json()["detail"]

    def test_login_missing_data(self, client: TestClient):
        """测试登录缺失数据"""
        login_data = {"username": "testuser"}  # 缺少密码
        response = client.post("/api/v1/auth/login-json", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenSecurity:
    """Token安全性测试"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "testpassword123"
        from app.core.security import get_password_hash

        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_protected_endpoint_without_token(self, client: TestClient):
        """测试未提供token访问受保护端点"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_invalid_token(self, client: TestClient):
        """测试使用无效token访问受保护端点"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_valid_token(self, client: TestClient, auth_headers: dict):
        """测试使用有效token访问受保护端点"""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK


class TestPasswordValidation:
    """密码验证测试"""

    @pytest.mark.parametrize(
        "password",
        [
            "short",  # 太短
            "",  # 空密码
            "   ",  # 空白字符
        ],
    )
    def test_weak_passwords(self, client: TestClient, sample_user_data: dict, password: str):
        """测试弱密码"""
        sample_user_data["password"] = password
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "password",
        [
            "strongpassword123",
            "VeryStrongP@ssw0rd",
            "test_password_123",
        ],
    )
    def test_strong_passwords(self, client: TestClient, sample_user_data: dict, password: str):
        """测试强密码"""
        sample_user_data["password"] = password
        sample_user_data["username"] = f"user_{password[:5]}"  # 避免重复用户名
        sample_user_data["email"] = f"{password[:5]}@example.com"  # 避免重复邮箱
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_200_OK


class TestAuthIntegration:
    """认证集成测试"""

    def test_register_and_login_flow(self, client: TestClient, sample_user_data: dict):
        """测试注册和登录完整流程"""
        # 1. 注册用户
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # 2. 登录用户
        login_data = {"username": sample_user_data["username"], "password": sample_user_data["password"]}
        login_response = client.post("/api/v1/auth/login-json", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        # 3. 使用token访问受保护端点
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK

        # 4. 验证用户信息
        user_data = profile_response.json()
        assert user_data["username"] == sample_user_data["username"]
        assert user_data["email"] == sample_user_data["email"]
