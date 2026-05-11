from typing import TYPE_CHECKING, Any

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.database.exceptions import DatabaseExecutionError
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from database.exceptions import DatabaseExecutionError

if TYPE_CHECKING:
    import pyodbc


class BaseRepository:
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def fetch_all(self, sql_query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql_query, parameters)

            column_names = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

            return [self._map_row_to_dictionary(column_names, row) for row in rows]
        except Exception as error:
            raise DatabaseExecutionError("Could not execute select query.") from error
        finally:
            connection.close()

    def fetch_one(
        self,
        sql_query: str,
        parameters: tuple[Any, ...] = (),
    ) -> dict[str, Any] | None:
        rows = self.fetch_all(sql_query, parameters)
        return rows[0] if rows else None

    def execute_non_query(
        self,
        sql_query: str,
        parameters: tuple[Any, ...] = (),
    ) -> None:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql_query, parameters)
            connection.commit()
        except Exception as error:
            connection.rollback()
            raise DatabaseExecutionError("Could not execute non-query statement.") from error
        finally:
            connection.close()

    @staticmethod
    def _map_row_to_dictionary(
        column_names: list[str],
        row: "pyodbc.Row",
    ) -> dict[str, Any]:
        return {
            column_name: row[index]
            for index, column_name in enumerate(column_names)
        }
