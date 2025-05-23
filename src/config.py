from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

if Path(".env").exists():
    env_file_path = ".env"
elif Path(".env.ci").exists():
    env_file_path = ".env.ci"


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    DEBUG: bool
    REDIRECT_URL: str
    TOKEN_EXPIRE_SECONDS: int

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str

    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8")


settings = Settings()  # type: ignore[call-arg]
