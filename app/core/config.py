"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings sourced from .env file and process env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "truck-showroom-be"
    app_version: str = "0.1.0"
    debug: bool = False

    # --- Database (mirrors .env.example) ---
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_user: str = "truck"
    postgres_password: str = Field(default="truck_dev_123")
    postgres_db: str = "truck_sales"

    # Optional override; nếu không set sẽ tự build từ các biến trên
    database_url: str | None = None

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Build SQLAlchemy URL nếu DATABASE_URL chưa được set."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (đọc .env 1 lần)."""
    return Settings()