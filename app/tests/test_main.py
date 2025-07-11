import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.task import Favorite


client = TestClient(app)


class TestRootEndpoint:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Pokemon API" in data["message"]

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestCORSHeaders:
    def test_cors_headers_present(self):
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_preflight_request(self):
        response = client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200


class TestErrorHandling:
    def test_404_error_handler(self):
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_validation_error_handling(self):
        invalid_user_data = {
            "username": "test",
            "email": "not-an-email",
            "password": "short",
        }

        response = client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 422


class TestUnauthenticatedAccess:
    def test_protected_endpoints_require_auth(self):
        protected_endpoints = ["/api/v1/pokemon/", "/favorites/", "/api/v1/users/me"]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401

    def test_public_endpoints_accessible(self):
        public_endpoints = [
            "/",
            "/health",
        ]

        for endpoint in public_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200


class TestDatabaseConnectivity:
    def test_database_models_can_be_created(self, db_session):
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
        )
        db_session.add(user)
        db_session.commit()

        favorite = Favorite(user_id=user.id, pokemon_id=1, pokemon_name="bulbasaur")
        db_session.add(favorite)
        db_session.commit()

        assert user.id is not None
        assert favorite.id is not None


class TestAppStartup:
    def test_app_can_start_without_import_errors(self):
        response = client.get("/health")
        assert response.status_code == 200
