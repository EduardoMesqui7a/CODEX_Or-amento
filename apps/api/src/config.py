from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "Orcamento IA API"
    app_env: str = "development"
    app_debug: bool = True
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./local.db"
    redis_url: str = "redis://localhost:6379/0"

    storage_dir: Path = Field(default=Path("./storage"))
    max_upload_size_mb: int = 30

    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    clerk_audience: str = ""

    cors_origins: str = "http://localhost:3000"

    s3_enabled: bool = False
    s3_bucket: str = ""
    s3_region: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_endpoint_url: str = ""

    celery_task_always_eager: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

