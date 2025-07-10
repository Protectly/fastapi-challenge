import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestTaskCreation:
    """Test task creation functionality"""

    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation"""
        task_data = {
            "title": "New Task",
            "description": "This is a new task",
            "priority": "high",
        }
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["is_completed"] is False
        assert "owner_id" in data

    def test_create_task_without_auth(self, client):
        """Test that task creation requires authentication"""
        task_data = {
            "title": "Unauthorized Task",
            "description": "This should fail",
            "priority": "medium",
        }
        response = client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 401

    def test_create_task_with_invalid_priority(self, client, auth_headers):
        """Test task creation with invalid priority - will pass due to missing validation"""
        task_data = {
            "title": "Task with bad priority",
            "description": "This has invalid priority",
            "priority": "super_ultra_mega_high",  # Invalid priority
        }
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        # This should fail with 422, but will pass due to missing priority validation
        # Candidates should add proper priority validation
        assert response.status_code == 422  # Will fail - no validation exists

    def test_create_task_long_title(self, client, auth_headers):
        """Test task creation with very long title - may fail due to length limit"""
        task_data = {
            "title": "x" * 200,  # Very long title - may exceed database limit
            "description": "Testing long title",
            "priority": "low",
        }
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        # This might fail due to the 100 character limit in the model
        # Response could be 500 (database error) or 422 (validation error)
        assert response.status_code in [201, 422, 500]

    def test_create_task_minimal_data(self, client, auth_headers):
        """Test creating task with only required fields"""
        task_data = {
            "title": "Minimal Task"
            # No description, priority should default to "medium"
        }
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["priority"] == "medium"  # Default value


class TestTaskRetrieval:
    """Test task retrieval functionality"""

    def test_get_tasks_success(self, client, auth_headers, sample_task):
        """Test getting user's tasks"""
        response = client.get("/api/v1/tasks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert data["total"] >= 1  # At least the sample task
        assert len(data["tasks"]) >= 1

    def test_get_tasks_without_auth(self, client):
        """Test that getting tasks requires authentication"""
        response = client.get("/api/v1/tasks/")
        assert response.status_code == 401

    def test_get_tasks_with_filters(self, client, auth_headers, sample_task):
        """Test task filtering functionality"""
        # Test completion filter
        response = client.get("/api/v1/tasks/?completed=false", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["is_completed"] is False

    def test_get_tasks_pagination(self, client, auth_headers, sample_task):
        """Test pagination parameters"""
        response = client.get("/api/v1/tasks/?skip=0&limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) <= 10

    def test_get_task_by_id(self, client, auth_headers, sample_task):
        """Test getting a specific task by ID"""
        response = client.get(f"/api/v1/tasks/{sample_task.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title

    def test_get_nonexistent_task(self, client, auth_headers):
        """Test getting a task that doesn't exist"""
        response = client.get("/api/v1/tasks/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_other_users_task(self, client, db_session):
        """Test that users can't access other users' tasks"""
        # Create another user and their task
        from app.models.user import User
        from app.models.task import Task
        from app.core.security import hash_password

        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=hash_password("password123"),
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        other_task = Task(
            title="Other User's Task",
            description="This belongs to someone else",
            priority="medium",
            owner_id=other_user.id,
        )
        db_session.add(other_task)
        db_session.commit()

        # Try to access other user's task with our auth
        response = client.get(f"/api/v1/tasks/{other_task.id}", headers=auth_headers)
        assert response.status_code == 404  # Should not be found (good security)


class TestTaskUpdating:
    """Test task update functionality"""

    def test_update_task_success(self, client, auth_headers, sample_task):
        """Test successful task update"""
        update_data = {"title": "Updated Task Title", "is_completed": True}
        response = client.put(
            f"/api/v1/tasks/{sample_task.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["is_completed"] is True
        assert data["description"] == sample_task.description  # Should remain unchanged

    def test_update_task_partial(self, client, auth_headers, sample_task):
        """Test partial task update"""
        update_data = {
            "is_completed": True
            # Only updating completion status
        }
        response = client.put(
            f"/api/v1/tasks/{sample_task.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        assert data["title"] == sample_task.title  # Should remain unchanged

    def test_update_nonexistent_task(self, client, auth_headers):
        """Test updating a task that doesn't exist"""
        update_data = {"title": "New Title"}
        response = client.put(
            "/api/v1/tasks/99999", json=update_data, headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_task_without_auth(self, client, sample_task):
        """Test that updating requires authentication"""
        update_data = {"title": "Should Fail"}
        response = client.put(f"/api/v1/tasks/{sample_task.id}", json=update_data)
        assert response.status_code == 401


class TestTaskDeletion:
    """Test task deletion functionality"""

    def test_delete_task_success(self, client, auth_headers, sample_task):
        """Test successful task deletion"""
        response = client.delete(
            f"/api/v1/tasks/{sample_task.id}", headers=auth_headers
        )
        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(
            f"/api/v1/tasks/{sample_task.id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_task(self, client, auth_headers):
        """Test deleting a task that doesn't exist"""
        response = client.delete("/api/v1/tasks/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_task_without_auth(self, client, sample_task):
        """Test that deletion requires authentication"""
        response = client.delete(f"/api/v1/tasks/{sample_task.id}")
        assert response.status_code == 401


class TestTaskSearch:
    """Test task search functionality"""

    def test_search_tasks(self, client, auth_headers, sample_task):
        """Test searching tasks by title"""
        response = client.get("/api/v1/tasks/?search=Test", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should find the sample task which has "Test" in title
        assert any("Test" in task["title"] for task in data["tasks"])

    def test_search_no_results(self, client, auth_headers):
        """Test search with no matching results"""
        response = client.get("/api/v1/tasks/?search=NONEXISTENT", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["tasks"]) == 0


class TestTaskListResponse:
    """Test the TaskListResponse schema"""

    def test_task_list_response_format(self, client, auth_headers, sample_task):
        """Test that the response has the correct format"""
        response = client.get("/api/v1/tasks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "tasks" in data
        assert "total" in data

        # Candidates should add these fields to TaskListResponse
        assert "page" in data  # Will fail - not implemented
        assert "size" in data  # Will fail - not implemented
        assert "pages" in data  # Will fail - not implemented


class TestBuggyTests:
    """Tests that demonstrate test bugs vs application bugs"""

    def test_wrong_assertion_example(self, client, auth_headers, sample_task):
        """This test has a bug - wrong assertion"""
        response = client.get(f"/api/v1/tasks/{sample_task.id}", headers=auth_headers)
        data = response.json()

        assert data["priority"] == "low"  # Wrong! sample_task has priority "high"

    def test_wrong_endpoint_example(self, client, auth_headers):
        """This test has a bug - wrong endpoint"""
        task_data = {"title": "Test Task"}

        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201  # Will fail - endpoint doesn't exist
