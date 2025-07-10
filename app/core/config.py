from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    app_name: str = "Pokemon API"
    debug: bool = False

    # Database Settings
    database_url: str = "sqlite:///./pokemon_api.db"

    # JWT Settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Settings
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"

    class Config:
        env_file = ".env"


settings = Settings()
