from pathlib import Path
from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings


class DbSettings(BaseModel):
    user: str
    password: SecretStr
    name: str
    host: str = "localhost"
    port: int = 5432

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    rate_limiter_db: int = 1

    @property
    def cache_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    @property
    def rate_limiter_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.rate_limiter_db}"


class JwtSettings(BaseModel):
    private_key_path: Path
    public_key_path: Path


class AppSettings(BaseModel):
    log_level: Literal["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"] = 'INFO'


class Settings(BaseSettings):
    db: DbSettings
    jwt: JwtSettings
    redis: RedisSettings
    app: AppSettings

    model_config = {"env_file": ".env", "env_nested_delimiter": "__"}


settings = Settings()  # type: ignore
