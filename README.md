# FastAPI Interview Project

## Overview

Welcome to our FastAPI technical interview project! This is a task management API built with FastAPI, SQLAlchemy, and SQLite. 

**⚠️ Important: This codebase contains intentional bugs and issues that need to be identified and fixed as part of the interview process.**

## The Task

You are tasked with getting this FastAPI application running and fixing various issues you encounter. The application should provide a REST API for managing tasks and users with authentication.

## Expected Features

The application should support:
- User registration and authentication (JWT tokens)
- CRUD operations for tasks
- Task filtering and searching
- User profile management
- Proper error handling and validation
- Basic security measures

## Setup Instructions

1. **Install dependencies**:
   ```bash
   uv sync --dev
   ```

2. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate  
   ```

3. **Initialize the database**:
   ```bash
   alembic upgrade head
   ```


## Testing

**🚀 Quick Start**: Run the test analysis script to see what's broken:
```bash
uv run python run_tests.py
```

This will show you exactly what needs to be fixed, starting with the most critical issues.

**Manual Testing**: You can also run tests manually:
```bash
# Run all tests
uv run python -m pytest

# Run tests with more verbose output
uv run python -m pytest -v

# Run specific test files
uv run python -m pytest app/tests/test_auth.py
uv run python -m pytest app/tests/test_tasks.py

# Run tests and see coverage
uv run python -m pytest --cov=app
```

**What to expect**: Many tests will fail initially! This is intentional. The failing tests will help you identify:
- 🔴 **Import errors** - These cause immediate failures and prevent the app from starting
- 🟡 **Logic bugs** - Tests that fail due to missing validation or business logic
- 🟢 **Test bugs** - Some tests themselves have bugs to help you distinguish between test issues and application issues

**Quick API Test**: After fixing bugs, you can run a quick end-to-end test:
```bash
# Make sure the server is running first
python test_api.py
```

## Your Mission

1. **Get the application running** - Fix any setup or startup issues
2. **Identify and fix bugs** - The application has intentional bugs of varying complexity
3. **Ensure tests pass** - Make sure all tests are working correctly
4. **Improve the code** - Suggest or implement improvements where you see fit

## Time Allocation

- **Junior Developer**: Focus on getting the app running and fixing obvious syntax/logic errors (30-45 minutes)
- **Mid-Level Developer**: Fix all bugs and ensure proper functionality (45-60 minutes)  
- **Senior Developer**: Fix everything + optimize performance and security (60-90 minutes)

## Deliverables

Please document:
1. **Issues found** - List all bugs/issues you identified
2. **Fixes applied** - Describe how you fixed each issue
3. **Improvements made** - Any additional improvements you implemented
4. **Time spent** - How long did it take you?

Good luck! 🚀

## API Endpoints Overview

Once working, the API should provide these endpoints:

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Authenticate and get JWT token

### Tasks
- `GET /tasks/` - List tasks (with optional filtering)
- `POST /tasks/` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile 