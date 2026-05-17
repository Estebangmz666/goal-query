from dataclasses import dataclass

try:
    from src.app.environment import load_environment_file
    from src.app.settings import ApplicationSettings, load_application_settings
    from src.database.connection import create_connection_factory
    from src.repositories.audit_log_repository import AuditLogRepository
    from src.repositories.player_repository import PlayerRepository
    from src.repositories.query_repository import QueryRepository
    from src.repositories.report_repository import ReportRepository
    from src.repositories.team_repository import TeamRepository
    from src.repositories.user_repository import UserRepository
    from src.services.auth_service import AuthService
    from src.services.authorization_service import AuthorizationService
    from src.services.player_service import PlayerService
    from src.services.query_service import QueryService
    from src.services.report_service import ReportService
    from src.services.team_service import TeamService
    from src.services.user_service import UserService
    from src.utils.password_hasher import PasswordHasher
except ModuleNotFoundError:
    from app.environment import load_environment_file
    from app.settings import ApplicationSettings, load_application_settings
    from database.connection import create_connection_factory
    from repositories.audit_log_repository import AuditLogRepository
    from repositories.player_repository import PlayerRepository
    from repositories.query_repository import QueryRepository
    from repositories.report_repository import ReportRepository
    from repositories.team_repository import TeamRepository
    from repositories.user_repository import UserRepository
    from services.auth_service import AuthService
    from services.authorization_service import AuthorizationService
    from services.player_service import PlayerService
    from services.query_service import QueryService
    from services.report_service import ReportService
    from services.team_service import TeamService
    from services.user_service import UserService
    from utils.password_hasher import PasswordHasher


@dataclass(frozen=True)
class ApplicationContext:
    settings: ApplicationSettings
    services: "ApplicationServices"


@dataclass(frozen=True)
class ApplicationServices:
    auth_service: AuthService
    authorization_service: AuthorizationService
    user_service: UserService
    team_service: TeamService
    player_service: PlayerService
    query_service: QueryService
    report_service: ReportService


def build_application() -> ApplicationContext:
    load_environment_file()
    settings = load_application_settings()
    connection_factory = create_connection_factory(settings.database)
    authorization_service = AuthorizationService()
    password_hasher = PasswordHasher()

    user_repository = UserRepository(connection_factory)
    audit_log_repository = AuditLogRepository(connection_factory)
    team_repository = TeamRepository(connection_factory)
    player_repository = PlayerRepository(connection_factory)
    query_repository = QueryRepository(connection_factory)
    report_repository = ReportRepository(connection_factory)

    services = ApplicationServices(
        auth_service=AuthService(user_repository, audit_log_repository, password_hasher),
        authorization_service=authorization_service,
        user_service=UserService(user_repository, authorization_service, password_hasher),
        team_service=TeamService(team_repository, authorization_service),
        player_service=PlayerService(player_repository, authorization_service),
        query_service=QueryService(query_repository),
        report_service=ReportService(report_repository, authorization_service),
    )
    return ApplicationContext(settings=settings, services=services)
