import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.task import Favorite


client = TestClient(app)


class TestTaskValidation:
    def test_create_task_with_invalid_priority(self, auth_headers):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "super_ultra_mega_high",
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_task_with_very_long_title(self, auth_headers):
        task_data = {
            "title": "x" * 200,
            "description": "Test Description",
            "priority": "high",
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers)

    def test_create_task_with_minimal_data(self, auth_headers):
        task_data = {"title": "Minimal Task"}

        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["priority"] == "medium"


class TestTaskList:
    def test_get_tasks_list(self, auth_headers, sample_task):
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_tasks_with_pagination(self, auth_headers):
        response = client.get("/tasks/?limit=5&skip=0", headers=auth_headers)
        assert response.status_code == 200

    def test_filter_tasks_by_completion(self, auth_headers, sample_task):
        response = client.get("/tasks/?completed=false", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for task in data["tasks"]:
            assert task["is_completed"] == False


class TestTaskSecurity:
    def test_user_can_only_see_own_tasks(self, db_session):
        user1 = User(
            username="user1", email="user1@example.com", hashed_password="hashedpass"
        )
        user2 = User(
            username="user2", email="user2@example.com", hashed_password="hashedpass"
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        task1 = Task(title="User 1 Task", owner_id=user1.id)
        task2 = Task(title="User 2 Task", owner_id=user2.id)
        db_session.add_all([task1, task2])
        db_session.commit()

        login_data = {"email": user1.email, "password": "testpass123"}
        auth_response = client.post("/api/v1/auth/login", json=login_data)
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/tasks/{task2.id}", headers=headers)
        assert response.status_code == 404


class TestTaskUpdates:
    def test_partial_task_update(self, auth_headers, sample_task):
        update_data = {"description": "Updated description"}

        response = client.put(
            f"/tasks/{sample_task.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["description"] == "Updated description"
        assert data["description"] == sample_task.description

    def test_update_task_completion_status(self, auth_headers, sample_task):
        update_data = {"is_completed": True}

        response = client.put(
            f"/tasks/{sample_task.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["is_completed"] == True
        assert data["title"] == sample_task.title


class TestTaskDeletion:
    def test_delete_task(self, auth_headers, sample_task):
        task_id = sample_task.id

        response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 204

        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404


class TestTaskSearch:
    def test_search_tasks_by_title(self, auth_headers, sample_task):
        response = client.get("/tasks/?search=Test", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["tasks"]) >= 1


class TestTaskListPagination:
    def test_task_list_pagination_fields(self, auth_headers):
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data


class TestTaskBugs:
    def test_task_priority_assertion_bug(self, auth_headers, sample_task):
        response = client.get(f"/tasks/{sample_task.id}", headers=auth_headers)
        data = response.json()
        assert data["priority"] == "low"

    def test_wrong_endpoint_bug(self, auth_headers):
        task_data = {"title": "Test Task"}
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
