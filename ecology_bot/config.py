from secrets import token_hex
from typing import Optional, Dict, Any, List

from pydantic import BaseSettings, Field, PostgresDsn, validator, RedisDsn


class DefaultSettings(BaseSettings):
    DEBUG: bool = Field(default=True)
    SECRET_KEY: str = Field(default=token_hex(16))

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f'/{values.get("POSTGRES_DB") or ""}',
            port=f'{values.get("POSTGRES_PORT") or ""}',
        )

    TELEGRAM_BOT_TOKEN: str

    TELEGRAM_BOT_ADMINS: List[int]

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str

    REDIS_URI: Optional[RedisDsn] = None

    @validator("REDIS_URI", pre=True)
    def assemble_redis_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_HOST"),
            port=values.get("REDIS_PORT"),
            password=values.get("REDIS_PASSWORD"),
            path="/1",
        )

    CELERY_DBURI: Optional[PostgresDsn] = None

    @validator("CELERY_DBURI", pre=True)
    def assemble_celery_dburi(cls, v: Optional[str], values: [str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
            port=f"{values.get('POSTGRES_PORT') or ''}",
        )
