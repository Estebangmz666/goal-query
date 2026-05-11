try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.auth_models import CreatedUserDTO
    from src.repositories.user_repository import UserRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.password_hasher import PasswordHasher
    from src.utils.validators import validate_not_blank
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.auth_models import CreatedUserDTO
    from repositories.user_repository import UserRepository
    from services.authorization_service import AuthorizationService
    from utils.password_hasher import PasswordHasher
    from utils.validators import validate_not_blank


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._authorization_service = authorization_service
        self._password_hasher = password_hasher

    def create_user(
        self,
        requester_role: UserRole,
        username: str,
        full_name: str,
        raw_password: str,
        role: UserRole,
    ) -> CreatedUserDTO:
        self._authorization_service.authorize(requester_role, Permission.CREATE_USER)
        validate_not_blank(username, "Username")
        validate_not_blank(full_name, "Full name")
        validate_not_blank(raw_password, "Password")

        if len(raw_password) < 8:
            raise ValidationError("Password must contain at least 8 characters.")

        if self._user_repository.username_exists(username):
            raise ValidationError("Username already exists.")

        is_system_administrator = role == UserRole.ADMINISTRATOR
        if is_system_administrator and self._user_repository.administrator_exists():
            raise ValidationError("Only one administrator user is allowed.")

        password_hash = self._password_hasher.hash_password(raw_password)
        user_id = self._user_repository.create_user(
            username=username,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
            is_system_administrator=is_system_administrator,
        )
        return CreatedUserDTO(
            user_id=user_id,
            username=username,
            full_name=full_name,
            role=role,
            is_active=True,
        )
