"""Environment-aware backend configuration."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"))


@dataclass(frozen=True)
class Settings:
    node_env: str
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    pipeline_enabled: bool
    pipeline_hour: int
    pipeline_minute: int


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    node_env = os.getenv("NODE_ENV", "development").strip().lower()
    if node_env == "prod":
        node_env = "production"
    if node_env not in {"development", "staging", "production"}:
        raise RuntimeError("NODE_ENV must be development, staging, or production")

    default_pipeline = node_env == "production"
    if node_env == "development":
        # Never inherit legacy office-database keys from an old .env in local
        # development. Compose overrides these values with DATABASE_* values.
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "sri_dev")
        db_user = os.getenv("DATABASE_USER", "sri")
        db_password = os.getenv("DATABASE_PASSWORD", "sri_dev_password")
    else:
        db_host = os.getenv("DATABASE_HOST", os.getenv("host", "localhost"))
        db_port = os.getenv("DATABASE_PORT", os.getenv("port", "5432"))
        db_name = os.getenv("DATABASE_NAME", os.getenv("dbname", "postgres"))
        db_user = os.getenv("DATABASE_USER", os.getenv("user", "postgres"))
        db_password = os.getenv(
            "DATABASE_PASSWORD",
            os.getenv("password", os.getenv("pass", "")),
        )

    return Settings(
        node_env=node_env,
        database_host=db_host,
        database_port=int(db_port),
        database_name=db_name,
        database_user=db_user,
        database_password=db_password,
        pipeline_enabled=_env_bool("ENABLE_PIPELINE", default_pipeline),
        pipeline_hour=int(os.getenv("PIPELINE_HOUR", "2")),
        pipeline_minute=int(os.getenv("PIPELINE_MINUTE", "0")),
    )


settings = load_settings()
