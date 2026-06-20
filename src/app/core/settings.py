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


class Settings(BaseSettings):
    db: DbSettings

    model_config = {"env_file": ".env", "env_nested_delimiter": "__"}


settings = Settings()  # type: ignore
