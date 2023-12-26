from functools import lru_cache
from typing import Any

from pydantic import BaseSettings, PostgresDsn, validator


class SettingsSchema(BaseSettings):
    DEBUG: bool = False

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str = '5432'

    SQLALCHEMY_DATABASE_URL: PostgresDsn | None = None
    SECRET_KEY: str = "&3l_-av%7g^a7y4@*+75vu@525w4sn(hz^lu@t03ds"
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TOKEN_URL: str = "/api/v1/auth/login"

    @validator("SQLALCHEMY_DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = '.env'


@lru_cache
def get_config() -> SettingsSchema:
    return SettingsSchema()


settings = get_config()
