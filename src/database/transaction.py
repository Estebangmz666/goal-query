from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.database.exceptions import DatabaseExecutionError
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from database.exceptions import DatabaseExecutionError

if TYPE_CHECKING:
    import pyodbc


class DatabaseTransactionManager:
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        self._connection_factory = connection_factory

    @contextmanager
    def transaction(self) -> Iterator["pyodbc.Connection"]:
        connection = self._connection_factory.create_connection()

        try:
            yield connection
            connection.commit()
        except Exception as error:
            connection.rollback()
            raise DatabaseExecutionError("Database transaction failed.") from error
        finally:
            connection.close()
