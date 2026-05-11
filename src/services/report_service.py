from datetime import datetime

try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.report_models import (
        AuditLogReportItemDTO,
        CountriesByHostCountryReportItemDTO,
        FilteredPlayerReportItemDTO,
        TeamValueByConfederationReportItemDTO,
    )
    from src.repositories.report_repository import ReportRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.report_models import (
        AuditLogReportItemDTO,
        CountriesByHostCountryReportItemDTO,
        FilteredPlayerReportItemDTO,
        TeamValueByConfederationReportItemDTO,
    )
    from repositories.report_repository import ReportRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank


class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._report_repository = report_repository
        self._authorization_service = authorization_service

    def get_user_sessions_by_datetime_range(
        self,
        requester_role: UserRole,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> list[AuditLogReportItemDTO]:
        self._authorization_service.authorize(requester_role, Permission.VIEW_AUDIT_LOGS)
        if start_datetime > end_datetime:
            raise ValidationError("Start datetime must be before end datetime.")

        return self._report_repository.get_user_sessions_by_datetime_range(
            start_datetime,
            end_datetime,
        )

    def get_players_by_filters(
        self,
        requester_role: UserRole,
        minimum_weight_kg: float,
        maximum_weight_kg: float,
        minimum_height_cm: float,
        maximum_height_cm: float,
        team_name: str,
    ) -> list[FilteredPlayerReportItemDTO]:
        self._authorization_service.authorize(requester_role, Permission.GENERATE_REPORTS)
        validate_not_blank(team_name, "Team name")
        if minimum_weight_kg > maximum_weight_kg:
            raise ValidationError("Minimum weight must be less than or equal to maximum weight.")
        if minimum_height_cm > maximum_height_cm:
            raise ValidationError("Minimum height must be less than or equal to maximum height.")

        return self._report_repository.get_players_by_filters(
            minimum_weight_kg,
            maximum_weight_kg,
            minimum_height_cm,
            maximum_height_cm,
            team_name,
        )

    def get_total_player_value_by_confederation(
        self,
        requester_role: UserRole,
        confederation_code: str,
    ) -> list[TeamValueByConfederationReportItemDTO]:
        self._authorization_service.authorize(requester_role, Permission.GENERATE_REPORTS)
        validate_not_blank(confederation_code, "Confederation code")
        return self._report_repository.get_total_player_value_by_confederation(
            confederation_code.strip().upper()
        )

    def get_countries_playing_by_host_country(
        self,
        requester_role: UserRole,
    ) -> list[CountriesByHostCountryReportItemDTO]:
        self._authorization_service.authorize(requester_role, Permission.GENERATE_REPORTS)
        return self._report_repository.get_countries_playing_by_host_country()
