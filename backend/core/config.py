from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_ENV: str = "development"  # development | staging | production
    APP_NAME: str = "ModKit"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database — auto-derived from APP_ENV if not set explicitly
    # development → SQLite   |   staging/production → PostgreSQL
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def derive_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            if self.APP_ENV == "development":
                self.DATABASE_URL = "sqlite+aiosqlite:///./modkit.db"
            else:
                self.DATABASE_URL = (
                    "postgresql+asyncpg://postgres:postgres@localhost:5432/modkit"
                )
        return self

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Cookie
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False  # True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
