from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALEMBIC_DATABASE_URL: str = os.getenv("ALEMBIC_DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    class Config:
        env_file = ".env"

settings = Settings()
