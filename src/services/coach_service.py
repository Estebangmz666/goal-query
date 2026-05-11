try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.coach_models import CreateCoachDTO, CoachResponseDTO, UpdateCoachDTO
    from src.repositories.coach_repository import CoachRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.coach_models import CreateCoachDTO, CoachResponseDTO, UpdateCoachDTO
    from repositories.coach_repository import CoachRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank


class CoachService:
    def __init__(
        self,
        coach_repository: CoachRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._coach_repository = coach_repository
        self._authorization_service = authorization_service

    def create_coach(
        self,
        requester_role: UserRole,
        coach_data: CreateCoachDTO,
    ) -> CoachResponseDTO:
        """Create a new coach. Only ADMINISTRATOR and TRADITIONAL_USER can create coaches."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        self._validate_coach_data(coach_data)

        if not self._coach_repository.team_exists(coach_data.team_id):
            raise ValidationError(f"Team with ID {coach_data.team_id} does not exist.")

        if not self._coach_repository.country_exists(coach_data.nationality_country_id):
            raise ValidationError(f"Country with ID {coach_data.nationality_country_id} does not exist.")

        if self._coach_repository.coach_exists_for_team(coach_data.team_id):
            raise ValidationError(f"Team with ID {coach_data.team_id} already has a coach assigned.")

        coach_id = self._coach_repository.create(
            team_id=coach_data.team_id,
            first_name=coach_data.first_name,
            last_name=coach_data.last_name,
            nationality_country_id=coach_data.nationality_country_id,
        )

        return CoachResponseDTO(
            id=coach_id,
            team_id=coach_data.team_id,
            first_name=coach_data.first_name,
            last_name=coach_data.last_name,
            nationality_country_id=coach_data.nationality_country_id,
        )

    def get_coach(self, coach_id: int) -> CoachResponseDTO:
        """Retrieve a coach by ID."""
        coach_data = self._coach_repository.find_by_id(coach_id)
        if not coach_data:
            raise ValidationError(f"Coach with ID {coach_id} not found.")

        return self._map_to_response_dto(coach_data)

    def get_all_coaches(self) -> list[CoachResponseDTO]:
        """Retrieve all coaches."""
        coaches = self._coach_repository.find_all()
        return [self._map_to_response_dto(coach) for coach in coaches]

    def get_coach_by_team(self, team_id: int) -> CoachResponseDTO | None:
        """Retrieve coach for a specific team."""
        coach_data = self._coach_repository.find_by_team_id(team_id)
        return self._map_to_response_dto(coach_data) if coach_data else None

    def get_coaches_by_nationality(self, country_id: int) -> list[CoachResponseDTO]:
        """Retrieve all coaches from a specific country."""
        coaches = self._coach_repository.find_all_by_nationality(country_id)
        return [self._map_to_response_dto(coach) for coach in coaches]

    def update_coach(
        self,
        requester_role: UserRole,
        coach_id: int,
        coach_data: UpdateCoachDTO,
    ) -> CoachResponseDTO:
        """Update coach information."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        existing_coach = self._coach_repository.find_by_id(coach_id)
        if not existing_coach:
            raise ValidationError(f"Coach with ID {coach_id} not found.")

        self._validate_coach_data(coach_data)

        if not self._coach_repository.country_exists(coach_data.nationality_country_id):
            raise ValidationError(f"Country with ID {coach_data.nationality_country_id} does not exist.")

        self._coach_repository.update(
            coach_id=coach_id,
            first_name=coach_data.first_name,
            last_name=coach_data.last_name,
            nationality_country_id=coach_data.nationality_country_id,
        )

        updated_coach = self._coach_repository.find_by_id(coach_id)
        return self._map_to_response_dto(updated_coach)

    def delete_coach(self, requester_role: UserRole, coach_id: int) -> None:
        """Delete a coach."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        coach = self._coach_repository.find_by_id(coach_id)
        if not coach:
            raise ValidationError(f"Coach with ID {coach_id} not found.")

        self._coach_repository.delete(coach_id)

    def _validate_coach_data(self, coach_data: CreateCoachDTO | UpdateCoachDTO) -> None:
        """Validate coach data."""
        validate_not_blank(coach_data.first_name, "First name")
        validate_not_blank(coach_data.last_name, "Last name")

        if hasattr(coach_data, "team_id") and coach_data.team_id <= 0:
            raise ValidationError("Team ID must be positive.")

        if coach_data.nationality_country_id <= 0:
            raise ValidationError("Nationality country ID must be positive.")

    @staticmethod
    def _map_to_response_dto(coach_data: dict) -> CoachResponseDTO:
        """Map repository row to response DTO."""
        return CoachResponseDTO(
            id=coach_data["id"],
            team_id=coach_data["team_id"],
            first_name=coach_data["first_name"],
            last_name=coach_data["last_name"],
            nationality_country_id=coach_data["nationality_country_id"],
        )
