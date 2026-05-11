from datetime import UTC, datetime

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.domain.entities.user import User
    from src.domain.enums.user_role import UserRole
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from domain.entities.user import User
    from domain.enums.user_role import UserRole
    from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_by_username(self, username: str) -> User | None:
        row = self.fetch_one(
            """
SELECT
    [user].id,
    role.code AS role_code,
    [user].username,
    [user].full_name,
    [user].password_hash,
    [user].is_active,
    [user].is_system_administrator,
    [user].created_at
FROM users AS [user]
INNER JOIN roles AS role
    ON role.id = [user].role_id
WHERE [user].username = ?;
""".strip(),
            (username,),
        )
        return self._map_to_user(row)

    def find_by_id(self, user_id: int) -> User | None:
        row = self.fetch_one(
            """
SELECT
    [user].id,
    role.code AS role_code,
    [user].username,
    [user].full_name,
    [user].password_hash,
    [user].is_active,
    [user].is_system_administrator,
    [user].created_at
FROM users AS [user]
INNER JOIN roles AS role
    ON role.id = [user].role_id
WHERE [user].id = ?;
""".strip(),
            (user_id,),
        )
        return self._map_to_user(row)

    def username_exists(self, username: str) -> bool:
        row = self.fetch_one(
            "SELECT 1 AS existing_value FROM users WHERE username = ?;",
            (username,),
        )
        return row is not None

    def administrator_exists(self) -> bool:
        row = self.fetch_one(
            """
SELECT 1 AS existing_value
FROM users
WHERE is_system_administrator = 1;
""".strip()
        )
        return row is not None

    def create_user(
        self,
        username: str,
        full_name: str,
        password_hash: str,
        role: UserRole,
        is_system_administrator: bool,
    ) -> int:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
INSERT INTO users (
    role_id,
    username,
    full_name,
    password_hash,
    is_active,
    is_system_administrator,
    created_at
)
OUTPUT INSERTED.id
SELECT
    role.id,
    ?,
    ?,
    ?,
    1,
    ?,
    ?
FROM roles AS role
WHERE role.code = ?;
""".strip(),
                (
                    username,
                    full_name,
                    password_hash,
                    1 if is_system_administrator else 0,
                    datetime.now(UTC),
                    role.value,
                ),
            )
            inserted_row = cursor.fetchone()
            connection.commit()
            return int(inserted_row[0])
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _map_to_user(row: dict | None) -> User | None:
        if row is None:
            return None

        return User(
            id=row["id"],
            role=UserRole(row["role_code"]),
            username=row["username"],
            full_name=row["full_name"],
            password_hash=row["password_hash"],
            is_active=bool(row["is_active"]),
            is_system_administrator=bool(row["is_system_administrator"]),
            created_at=row["created_at"],
        )
