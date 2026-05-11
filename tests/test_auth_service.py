from datetime import UTC, datetime
import unittest

try:
    from src.domain.entities.user import User
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.authentication_error import AuthenticationError
    from src.services.auth_service import AuthService
    from src.utils.password_hasher import PasswordHasher
except ModuleNotFoundError:
    from domain.entities.user import User
    from domain.enums.user_role import UserRole
    from domain.exceptions.authentication_error import AuthenticationError
    from services.auth_service import AuthService
    from utils.password_hasher import PasswordHasher


class FakeUserRepository:
    def __init__(self, user: User | None) -> None:
        self._user = user

    def find_by_username(self, username: str) -> User | None:
        return self._user


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.received_user_id = None
        self.closed_audit_log_id = None

    def create_login_record(self, user_id, login_at, machine_name, application_name):
        self.received_user_id = user_id
        return 55

    def close_session(self, audit_log_id, logout_at):
        self.closed_audit_log_id = audit_log_id


class AuthServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.password_hasher = PasswordHasher()
        self.user = User(
            id=7,
            role=UserRole.ADMINISTRATOR,
            username="admin",
            full_name="System Admin",
            password_hash=self.password_hasher.hash_password("strongpass"),
            is_active=True,
            is_system_administrator=True,
            created_at=datetime.now(UTC),
        )

    def test_login_creates_audit_log_for_valid_credentials(self) -> None:
        audit_repository = FakeAuditLogRepository()
        service = AuthService(
            user_repository=FakeUserRepository(self.user),
            audit_log_repository=audit_repository,
            password_hasher=self.password_hasher,
        )

        session = service.login("admin", "strongpass", "lab-1", "GoalQuery")

        self.assertEqual(55, session.audit_log_id)
        self.assertEqual(7, audit_repository.received_user_id)

    def test_login_rejects_invalid_password(self) -> None:
        service = AuthService(
            user_repository=FakeUserRepository(self.user),
            audit_log_repository=FakeAuditLogRepository(),
            password_hasher=self.password_hasher,
        )

        with self.assertRaises(AuthenticationError):
            service.login("admin", "wrongpass")

    def test_logout_closes_existing_session(self) -> None:
        audit_repository = FakeAuditLogRepository()
        service = AuthService(
            user_repository=FakeUserRepository(self.user),
            audit_log_repository=audit_repository,
            password_hasher=self.password_hasher,
        )

        service.logout(99)

        self.assertEqual(99, audit_repository.closed_audit_log_id)


if __name__ == "__main__":
    unittest.main()
