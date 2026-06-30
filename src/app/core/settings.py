from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings


class DbSettings(BaseModel):
    user: str
    password: SecretStr
    name: str
    host: str = "localhost"
    port: int = 5432

    override_url: PostgresDsn | None = None

    @property
    def url(self) -> str:
        if self.override_url:
            return str(self.override_url)
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    rate_limiter_db: int = 1
    celery_db: int = 2

    @property
    def cache_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"

    @property
    def rate_limiter_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.rate_limiter_db}"

    @property
    def celery_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.celery_db}"


class JwtSettings(BaseModel):
    private_key_path: Path
    public_key_path: Path


class AppSettings(BaseModel):
    log_level: Literal["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"] = "INFO"
    cors_origins: List[str] = ["http://localhost:3000"]
    base_url: str = "http://localhost:8000"



class Settings(BaseSettings):
    db: DbSettings
    jwt: JwtSettings
    redis: RedisSettings
    app: AppSettings

    model_config = {"env_file": ".env", "env_nested_delimiter": "__"}


settings = Settings()  # type: ignore
