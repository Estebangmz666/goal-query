from typing import TYPE_CHECKING

try:
    from src.config.database_config import DatabaseConfig
    from src.database.exceptions import (
        DatabaseConfigurationError,
        DatabaseConnectionError,
    )
except ModuleNotFoundError:
    from config.database_config import DatabaseConfig
    from database.exceptions import (
        DatabaseConfigurationError,
        DatabaseConnectionError,
    )

if TYPE_CHECKING:
    import pyodbc


class DatabaseConnectionFactory:
    def __init__(self, database_config: DatabaseConfig) -> None:
        self._database_config = database_config

    def create_connection(self) -> "pyodbc.Connection":
        self._validate_configuration()
        pyodbc = self._load_pyodbc()

        try:
            return pyodbc.connect(self.build_connection_string(), autocommit=False)
        except pyodbc.Error as error:
            raise DatabaseConnectionError(
                "Could not establish a connection to SQL Server."
            ) from error

    def build_connection_string(self) -> str:
        connection_values = {
            "DRIVER": self._wrap_driver(self._database_config.driver),
            "SERVER": f"{self._database_config.server},{self._database_config.port}",
            "DATABASE": self._database_config.database_name,
            "UID": self._database_config.user,
            "PWD": self._database_config.password,
            "TrustServerCertificate": "yes"
            if self._database_config.trust_server_certificate
            else "no",
        }
        return ";".join(
            f"{key}={value}" for key, value in connection_values.items()
        )

    def _validate_configuration(self) -> None:
        missing_fields = []

        if not self._database_config.server:
            missing_fields.append("DB_SERVER")
        if not self._database_config.database_name:
            missing_fields.append("DB_NAME")
        if not self._database_config.user:
            missing_fields.append("DB_USER")
        if not self._database_config.password:
            missing_fields.append("DB_PASSWORD")
        if not self._database_config.driver:
            missing_fields.append("DB_DRIVER")

        if missing_fields:
            raise DatabaseConfigurationError(
                "Missing required database configuration values: "
                + ", ".join(missing_fields)
            )

    @staticmethod
    def _wrap_driver(driver_name: str) -> str:
        if driver_name.startswith("{") and driver_name.endswith("}"):
            return driver_name
        return "{" + driver_name + "}"

    @staticmethod
    def _load_pyodbc():
        try:
            import pyodbc
        except ModuleNotFoundError as error:
            raise DatabaseConnectionError(
                "pyodbc is not installed. Install dependencies before connecting to SQL Server."
            ) from error

        return pyodbc


def create_connection_factory(database_config: DatabaseConfig) -> DatabaseConnectionFactory:
    return DatabaseConnectionFactory(database_config=database_config)


def test_database_connection(database_config: DatabaseConfig) -> None:
    connection_factory = create_connection_factory(database_config)
    connection = connection_factory.create_connection()
    connection.close()
