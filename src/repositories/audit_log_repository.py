from datetime import datetime

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def create_login_record(
        self,
        user_id: int,
        login_at: datetime,
        machine_name: str | None,
        application_name: str | None,
    ) -> int:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
INSERT INTO audit_logs (
    user_id,
    login_at,
    logout_at,
    session_status,
    machine_name,
    application_name
)
OUTPUT INSERTED.id
VALUES (?, ?, NULL, 'OPEN', ?, ?);
""".strip(),
                (user_id, login_at, machine_name, application_name),
            )
            inserted_row = cursor.fetchone()
            connection.commit()
            return int(inserted_row[0])
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def close_session(
        self,
        audit_log_id: int,
        logout_at: datetime,
    ) -> None:
        self.execute_non_query(
            """
UPDATE audit_logs
SET logout_at = ?, session_status = 'CLOSED'
WHERE id = ?;
""".strip(),
            (logout_at, audit_log_id),
        )
