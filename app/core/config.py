from pydantic import BaseConfig


class Settings(BaseConfig):
    PROJECT_NAME: str = "FastAPI Book Manager"
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./bookstore.db"
    # JWT
    SECRET_KEY: str = "change-me-to-a-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24


class Config:
    env_file = ".env"


settings = Settings()