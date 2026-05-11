import unittest

try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.authorization_error import AuthorizationError
    from src.services.authorization_service import AuthorizationService
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.authorization_error import AuthorizationError
    from services.authorization_service import AuthorizationService


class AuthorizationServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AuthorizationService()

    def test_sporadic_user_cannot_create_user(self) -> None:
        with self.assertRaises(AuthorizationError):
            self.service.authorize(UserRole.SPORADIC_USER, Permission.CREATE_USER)

    def test_traditional_user_can_generate_reports(self) -> None:
        self.service.authorize(UserRole.TRADITIONAL_USER, Permission.GENERATE_REPORTS)

    def test_administrator_can_view_audit_logs(self) -> None:
        self.service.authorize(UserRole.ADMINISTRATOR, Permission.VIEW_AUDIT_LOGS)


if __name__ == "__main__":
    unittest.main()
