import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestMainEndpoints:
    """Test main application endpoints"""

    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Task Management API" in data["message"] or "Welcome" in data["message"]

    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_docs_endpoint(self, client):
        """Test that API docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")

    def test_openapi_endpoint(self, client):
        """Test that OpenAPI spec is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present - may fail due to overly permissive settings"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200

        # Candidates should restrict CORS in production
        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        response = client.options(
            "/api/v1/tasks/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization",
            },
        )
        # Should return 200 for preflight
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling"""

    def test_internal_server_error_handling(self, client):
        """Test that internal server errors are handled properly"""
        # This endpoint doesn't exist, so we'll test with an endpoint that might cause an error
        # Due to the buggy error handler, this might expose internal details
        response = client.get("/api/v1/tasks/invalid_id_type")
        # Should return 422 for validation error, not 500
        assert response.status_code in [422, 400]

    def test_validation_error_format(self, client):
        """Test that validation errors are properly formatted"""
        # Send invalid data to trigger validation error
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",  # Invalid email
                "username": "test",
                "password": "pass",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestAuthentication:
    """Test authentication middleware and dependencies"""

    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/tasks/",
            "/api/v1/users/me",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert (
                response.status_code == 401
            ), f"Endpoint {endpoint} should require auth"

    def test_auth_endpoints_dont_require_auth(self, client):
        """Test that auth endpoints don't require authentication"""
        # These should be accessible without auth (though they might fail for other reasons)
        response = client.post("/api/v1/auth/register", json={})
        # Should get validation error (422), not auth error (401)
        assert response.status_code != 401

        response = client.post("/api/v1/auth/login", json={})
        # Should get validation error (422), not auth error (401)
        assert response.status_code != 401


class TestApplicationStartup:
    """Test application startup and initialization"""

    def test_database_tables_created(self, client, db_session):
        """Test that database tables are created properly"""
        # This test verifies that the database setup works
        # If there are model relationship bugs, this might fail
        from app.models.user import User
        from app.models.task import Task

        # Try to create a user - this will fail if there are model issues
        user = User(
            email="startup_test@example.com",
            username="startup_test",
            hashed_password="dummy_hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()  # This might fail due to model bugs

        # Try to create a task - this will fail if there are relationship bugs
        task = Task(
            title="Startup Test Task",
            description="Testing database setup",
            priority="medium",
            owner_id=user.id,
        )
        db_session.add(task)
        db_session.commit()  # This might fail due to relationship bugs

        # If we get here, the basic models work
        assert user.id is not None
        assert task.id is not None
        assert task.owner_id == user.id


class TestBugIdentification:
    """Tests specifically designed to expose bugs"""

    def test_import_errors_cause_startup_failure(self, client):
        """This test might fail if there are import errors in the codebase"""
        # Simply creating the client and making a request will expose import issues
        response = client.get("/health")
        # If there are import errors, this test will fail during client creation
        assert response.status_code == 200
