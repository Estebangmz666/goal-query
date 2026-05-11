from dataclasses import dataclass
import os

try:
    from src.config.database_config import DatabaseConfig, load_database_config
except ModuleNotFoundError:
    from config.database_config import DatabaseConfig, load_database_config


@dataclass(frozen=True)
class ApplicationSettings:
    app_name: str
    app_env: str
    debug: bool
    database: DatabaseConfig


def load_application_settings() -> ApplicationSettings:
    return ApplicationSettings(
        app_name=os.getenv("APP_NAME", "GoalQuery"),
        app_env=os.getenv("APP_ENV", "development"),
        debug=_parse_bool(os.getenv("APP_DEBUG", "false")),
        database=load_database_config(),
    )


def _parse_bool(raw_value: str) -> bool:
    normalized_value = raw_value.strip().lower()
    return normalized_value in {"1", "true", "yes", "on"}
