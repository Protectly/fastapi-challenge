#!/usr/bin/env python3
"""
Simple test script to verify the API is working correctly.
This script tests basic functionality after bugs are fixed.
"""

import requests
import json
import sys
from time import sleep

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
        }
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/register", json=user_data
        )
        if response.status_code == 201:
            print("✅ User registration passed")
            return True, response.json()
        else:
            print(f"❌ User registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return False, None


def test_login():
    """Test user login"""
    print("Testing user login...")
    try:
        login_data = {"email": "test@example.com", "password": "testpassword123"}
        response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login passed")
            return True, response.json()
        else:
            print(f"❌ User login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ User login failed: {e}")
        return False, None


def test_create_task(token):
    """Test task creation"""
    print("Testing task creation...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high",
        }
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/tasks/", json=task_data, headers=headers
        )
        if response.status_code == 201:
            print("✅ Task creation passed")
            return True, response.json()
        else:
            print(f"❌ Task creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return False, None


def test_get_tasks(token):
    """Test getting tasks"""
    print("Testing get tasks...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{API_PREFIX}/tasks/", headers=headers)
        if response.status_code == 200:
            print("✅ Get tasks passed")
            return True, response.json()
        else:
            print(f"❌ Get tasks failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Get tasks failed: {e}")
        return False, None


def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print("=" * 50)

    # Test health endpoint
    if not test_health():
        print("❌ Basic health check failed. Is the server running?")
        sys.exit(1)

    # Test registration
    success, user_data = test_registration()
    if not success:
        print("❌ User registration failed")
        sys.exit(1)

    # Test login
    success, login_data = test_login()
    if not success:
        print("❌ User login failed")
        sys.exit(1)

    token = login_data.get("access_token")
    if not token:
        print("❌ No access token received")
        sys.exit(1)

    # Test task creation
    success, task_data = test_create_task(token)
    if not success:
        print("❌ Task creation failed")
        sys.exit(1)

    # Test getting tasks
    success, tasks_data = test_get_tasks(token)
    if not success:
        print("❌ Getting tasks failed")
        sys.exit(1)

    print("=" * 50)
    print("🎉 All tests passed! The API is working correctly.")
    print(f"✅ Created user: {user_data.get('username')}")
    print(f"✅ Created task: {task_data.get('title')}")
    print(f"✅ Found {tasks_data.get('total', 0)} tasks")


if __name__ == "__main__":
    main()
