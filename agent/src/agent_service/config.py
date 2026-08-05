"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    llm_provider: str = "deepseek"
    llm_model: str = "deepseek-chat"
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    llm_timeout_seconds: float = 30.0

    clerk_issuer: str | None = None
    clerk_jwks_url: str | None = None
    clerk_audience: str | None = None
    clerk_authorized_parties: list[str] = []

    cors_origins: list[str] = ["http://localhost:3000"]
    max_file_size: int = 10 * 1024 * 1024
    upload_dir: str = "uploads"
    database_url: str = "sqlite+aiosqlite:///./ai_job_coach.db"
    database_echo: bool = False
    database_auto_create: bool = False

    object_storage_backend: str = "local"
    object_storage_root: str = "object-storage"
    object_storage_bucket: str | None = None
    object_storage_endpoint_url: str | None = None
    object_storage_region: str | None = None
    object_storage_access_key_id: str | None = None
    object_storage_secret_access_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RESUME_",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
