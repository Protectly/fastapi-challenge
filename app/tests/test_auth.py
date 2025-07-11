import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User


client = TestClient(app)


class TestUserRegistration:
    def test_register_user_success(self, db_session):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, db_session, sample_user):
        user_data = {
            "username": "newuser",
            "email": sample_user.email,
            "password": "testpass123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400

    def test_register_invalid_password(self, db_session):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422


class TestUserLogin:
    def test_login_success(self, db_session, sample_user):
        login_data = {"email": sample_user.email, "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, db_session, sample_user):
        login_data = {"email": sample_user.email, "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_login_nonexistent_user(self, db_session):
        login_data = {"email": "nonexistent@example.com", "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401


class TestOAuth2Login:
    def test_oauth2_login_success(self, db_session, sample_user):
        login_data = {"username": sample_user.username, "password": "testpass123"}

        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200

    def test_oauth2_login_with_username_instead_of_email(self, db_session, sample_user):
        login_data = {"username": sample_user.username, "password": "testpass123"}
        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 422

    def test_login_inactive_user(self, db_session):
        inactive_user = User(
            username="inactive",
            email="inactive@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            is_active=False,
        )
        db_session.add(inactive_user)
        db_session.commit()

        login_data = {"email": inactive_user.email, "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401


class TestTokenValidation:
    def test_access_protected_route_with_valid_token(self, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "username" in data
        assert "email" in data

    def test_access_protected_route_without_token(self):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_access_protected_route_with_invalid_token(self):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_token_format_is_wrong(self, client, sample_user):
        """This test itself has a bug - wrong assertion"""
        login_data = {"email": sample_user.email, "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        data = response.json()
        assert data["token_type"] == "Bearer"

    def test_oauth2_with_form_data_not_json(self, sample_user):
        login_data = {"username": sample_user.username, "password": "testpass123"}

        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200
