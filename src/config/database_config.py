from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatabaseConfig:
    server: str
    port: int
    database_name: str
    user: str
    password: str
    driver: str
    trust_server_certificate: bool


def load_database_config() -> DatabaseConfig:
    return DatabaseConfig(
        server=os.getenv("DB_SERVER", "localhost"),
        port=int(os.getenv("DB_PORT", "1433")),
        database_name=os.getenv("DB_NAME", "GoalQuery"),
        user=os.getenv("DB_USER", "sa"),
        password=os.getenv("DB_PASSWORD", ""),
        driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
        trust_server_certificate=_parse_bool(
            os.getenv("DB_TRUST_SERVER_CERTIFICATE", "true")
        ),
    )


def _parse_bool(raw_value: str) -> bool:
    normalized_value = raw_value.strip().lower()
    return normalized_value in {"1", "true", "yes", "on"}
