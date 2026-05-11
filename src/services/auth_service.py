from datetime import UTC, datetime

try:
    from src.domain.exceptions.authentication_error import AuthenticationError
    from src.dto.auth_models import AuthenticatedSessionDTO
    from src.repositories.audit_log_repository import AuditLogRepository
    from src.repositories.user_repository import UserRepository
    from src.utils.password_hasher import PasswordHasher
    from src.utils.validators import validate_not_blank
except ModuleNotFoundError:
    from domain.exceptions.authentication_error import AuthenticationError
    from dto.auth_models import AuthenticatedSessionDTO
    from repositories.audit_log_repository import AuditLogRepository
    from repositories.user_repository import UserRepository
    from utils.password_hasher import PasswordHasher
    from utils.validators import validate_not_blank


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        audit_log_repository: AuditLogRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._audit_log_repository = audit_log_repository
        self._password_hasher = password_hasher

    def login(
        self,
        username: str,
        password: str,
        machine_name: str | None = None,
        application_name: str | None = None,
    ) -> AuthenticatedSessionDTO:
        validate_not_blank(username, "Username")
        validate_not_blank(password, "Password")

        user = self._user_repository.find_by_username(username)
        if user is None or not user.is_active:
            raise AuthenticationError("The username or password is incorrect.")

        if not self._password_hasher.verify_password(password, user.password_hash):
            raise AuthenticationError("The username or password is incorrect.")

        login_at = datetime.now(UTC)
        audit_log_id = self._audit_log_repository.create_login_record(
            user_id=user.id,
            login_at=login_at,
            machine_name=machine_name,
            application_name=application_name,
        )
        return AuthenticatedSessionDTO(
            audit_log_id=audit_log_id,
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            login_at=login_at,
        )

    def logout(self, audit_log_id: int) -> None:
        self._audit_log_repository.close_session(
            audit_log_id=audit_log_id,
            logout_at=datetime.now(UTC),
        )
