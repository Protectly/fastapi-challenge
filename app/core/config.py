from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./tasks.db"

    # JWT Settings
    secret_key: str = "super-secret-key-change-in-production"  # Bug: Hardcoded secret
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Task Management API"
    debug: bool = True

    # CORS Settings - Bug: Too permissive
    allowed_hosts: list = ["*"]

    class Config:
        env_file = ".env"


# Bug: Missing proper singleton pattern - creating multiple instances
settings = Settings()
