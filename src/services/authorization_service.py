try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.authorization_error import AuthorizationError
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.authorization_error import AuthorizationError


class AuthorizationService:
    _permissions_by_role = {
        UserRole.ADMINISTRATOR: {
            Permission.CREATE_USER,
            Permission.MANAGE_TEAMS,
            Permission.MANAGE_PLAYERS,
            Permission.MANAGE_MATCHES,
            Permission.RUN_QUERIES,
            Permission.GENERATE_REPORTS,
            Permission.VIEW_AUDIT_LOGS,
        },
        UserRole.TRADITIONAL_USER: {
            Permission.MANAGE_TEAMS,
            Permission.MANAGE_PLAYERS,
            Permission.MANAGE_MATCHES,
            Permission.RUN_QUERIES,
            Permission.GENERATE_REPORTS,
        },
        UserRole.SPORADIC_USER: {
            Permission.RUN_QUERIES,
        },
    }

    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        return permission in self._permissions_by_role.get(role, set())

    def authorize(self, role: UserRole, permission: Permission) -> None:
        if not self.has_permission(role, permission):
            raise AuthorizationError("You do not have permission to perform this action.")
