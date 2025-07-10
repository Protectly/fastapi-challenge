# Pokemon API - FastAPI Interview Project

A FastAPI application that integrates with the Pokemon API to provide Pokemon data and user favorites functionality.

## Features

- Fetch Pokemon data from PokeAPI
- User authentication with JWT tokens
- Save favorite Pokemon to database
- Search and filter Pokemon
- User profile management

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Initialize the database:
```bash
alembic upgrade head
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user

### Pokemon
- `GET /pokemon/` - List Pokemon with pagination
- `GET /pokemon/{pokemon_id}` - Get specific Pokemon details
- `GET /pokemon/search/{name}` - Search Pokemon by name

### Favorites
- `GET /favorites/` - Get user's favorite Pokemon
- `POST /favorites/{pokemon_id}` - Add Pokemon to favorites
- `DELETE /favorites/{pokemon_id}` - Remove Pokemon from favorites

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile

## Testing

Run tests:
```bash
python -m pytest
python -m pytest -v  # Verbose output
```

## Task

Your task is to:
1. Get the application running
2. Identify and fix any bugs you encounter
3. Ensure all tests pass
4. Document the issues you found

Time allocation: 45-60 minutes 