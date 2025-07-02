import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestUserRegistration:
    """Test user registration functionality"""

    def test_register_user_success(self, client):
        """This test should work once bugs are fixed"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "hashed_password" not in data  # Security check
        assert data["is_active"] is True

    def test_register_user_duplicate_email(self, client, sample_user):
        """Test that duplicate emails are rejected - will fail due to missing validation"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": sample_user.email,  # Same email as existing user
                "username": "differentuser",
                "password": "password123",
            },
        )
        # This should return 400, but will likely return 201 due to bug
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_user_weak_password(self, client):
        """Test password validation - will fail due to missing validation"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "123",  # Too short
            },
        )
        # Should return 422 for validation error, but might not due to missing validation
        assert response.status_code == 422

    def test_register_user_invalid_email(self, client):
        """Test email validation - this should work (pydantic validation)"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 422


class TestUserLogin:
    """Test user login functionality"""

    def test_login_success(self, client, sample_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user.email, "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_wrong_password(self, client, sample_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_with_username_should_fail(self, client, sample_user):
        """Bug: Test shows that login schema only accepts email, not username"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,  # This should work but won't due to schema bug
                "password": "testpassword123",
            },
        )
        # This test will fail because the schema doesn't support username login
        # Candidates should fix this by updating the login schema
        assert response.status_code == 422  # Will get validation error

    def test_login_inactive_user_should_fail(self, client, db_session):
        """Test that inactive users cannot login - will fail due to missing check"""
        # Create inactive user
        from app.models.user import User
        from app.core.security import hash_password

        inactive_user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=hash_password("password123"),
            is_active=False,  # Inactive user
        )
        db_session.add(inactive_user)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )
        # Should fail with 401, but might succeed due to missing is_active check
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()


class TestTokenAuth:
    """Test JWT token authentication"""

    def test_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401

    # Bug: This test has wrong assertion - will help identify test bugs vs code bugs
    def test_token_format_is_wrong(self, client, sample_user):
        """This test itself has a bug - wrong assertion"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user.email, "password": "testpassword123"},
        )
        data = response.json()
        # Bug: This assertion is wrong - token_type should be "bearer" not "Bearer"
        assert data["token_type"] == "Bearer"  # Wrong! Should be "bearer"


class TestOAuth2Integration:
    """Test OAuth2 password flow (the /token endpoint)"""

    def test_oauth2_token_endpoint(self, client, sample_user):
        """Test the OAuth2 compatible token endpoint"""
        response = client.post(
            "/api/v1/auth/token",
            data={  # OAuth2 uses form data, not JSON
                "username": sample_user.username,
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_oauth2_token_wrong_credentials(self, client):
        """Test OAuth2 endpoint with wrong credentials"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401
