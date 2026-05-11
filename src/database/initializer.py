from pathlib import Path
from typing import TYPE_CHECKING, Iterable

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.database.exceptions import DatabaseExecutionError
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from database.exceptions import DatabaseExecutionError

if TYPE_CHECKING:
    import pyodbc


class DatabaseInitializer:
    def __init__(
        self,
        connection_factory: DatabaseConnectionFactory,
        scripts_directory: str = "sql",
    ) -> None:
        self._connection_factory = connection_factory
        self._scripts_directory = Path(scripts_directory)

    def get_script_paths(self) -> list[Path]:
        if not self._scripts_directory.exists():
            return []

        return sorted(
            path
            for path in self._scripts_directory.iterdir()
            if path.is_file() and path.suffix.lower() == ".sql"
        )

    def initialize_database(self) -> list[str]:
        executed_scripts = []

        with self._connection_factory.create_connection() as connection:
            cursor = connection.cursor()
            try:
                for script_path in self.get_script_paths():
                    self._execute_script(cursor, script_path)
                    executed_scripts.append(script_path.name)

                connection.commit()
            except Exception as error:
                connection.rollback()
                raise DatabaseExecutionError(
                    "Database initialization failed."
                ) from error

        return executed_scripts

    def _execute_script(self, cursor: "pyodbc.Cursor", script_path: Path) -> None:
        script_content = script_path.read_text(encoding="utf-8").strip()
        if not script_content:
            return

        for statement in self._split_script_statements(script_content):
            cursor.execute(statement)

    @staticmethod
    def _split_script_statements(script_content: str) -> Iterable[str]:
        normalized_script = script_content.replace("\r\n", "\n")
        for statement in normalized_script.split("\nGO\n"):
            normalized_statement = statement.strip()
            if normalized_statement:
                yield normalized_statement
