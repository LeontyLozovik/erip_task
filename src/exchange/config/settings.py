import os
from typing import Annotated, Literal

from pydantic import Field, IPvAnyAddress, StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env.example"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: Literal["dev", "test", "prod"]

    APP_HOST: IPvAnyAddress | str

    APP_PORT: Annotated[int, Field(ge=1024, le=65535)] = 8000

    LOG_FILE: Annotated[str, StringConstraints(pattern=r".*\.log$")]

    LOG_MAX_BYTES: Annotated[int, Field(ge=100000, le=5_000_000)]

    LOG_BACKUP_COUNT: Annotated[int, Field(ge=1, le=10)]

    POSTGRES_USER: Annotated[str, Field(min_length=1, max_length=63)]

    POSTGRES_PASSWORD: Annotated[str, Field(min_length=8, max_length=128)]

    POSTGRES_DB: Annotated[str, Field(min_length=1, max_length=63)]

    DB_HOST: IPvAnyAddress | str

    DB_PORT: Annotated[int, Field(ge=1024, le=65535)] = 5432


settings = Settings()
