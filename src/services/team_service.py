try:
    from src.database.connection import DatabaseConnectionFactory
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.team_models import CreateTeamDTO, TeamResponseDTO, UpdateTeamDTO
    from src.repositories.team_repository import TeamRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank, validate_positive_number
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.team_models import CreateTeamDTO, TeamResponseDTO, UpdateTeamDTO
    from repositories.team_repository import TeamRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank, validate_positive_number


class TeamService:
    def __init__(
        self,
        team_repository: TeamRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._team_repository = team_repository
        self._authorization_service = authorization_service

    def create_team(
        self,
        requester_role: UserRole,
        team_data: CreateTeamDTO,
    ) -> TeamResponseDTO:
        """Create a new team. Only ADMINISTRATOR and TRADITIONAL_USER can create teams."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        self._validate_create_team_data(team_data)

        if self._team_repository.name_exists(team_data.name):
            raise ValidationError(f"Team '{team_data.name}' already exists.")

        if self._team_repository.fifa_code_exists(team_data.fifa_code):
            raise ValidationError(f"FIFA code '{team_data.fifa_code}' is already in use.")

        team_id = self._team_repository.create(
            name=team_data.name,
            fifa_code=team_data.fifa_code,
            country_id=team_data.country_id,
            confederation_id=team_data.confederation_id,
            team_weight=team_data.team_weight,
            market_value=team_data.market_value,
            group_id=team_data.group_id,
        )

        return TeamResponseDTO(
            id=team_id,
            name=team_data.name,
            fifa_code=team_data.fifa_code,
            country_id=team_data.country_id,
            confederation_id=team_data.confederation_id,
            team_weight=team_data.team_weight,
            market_value=team_data.market_value,
            group_id=team_data.group_id,
        )

    def get_team(self, team_id: int) -> TeamResponseDTO:
        """Retrieve a team by ID."""
        team_data = self._team_repository.find_by_id(team_id)
        if not team_data:
            raise ValidationError(f"Team with ID {team_id} not found.")

        return self._map_to_response_dto(team_data)

    def get_all_teams(self) -> list[TeamResponseDTO]:
        """Retrieve all teams."""
        teams = self._team_repository.find_all()
        return [self._map_to_response_dto(team) for team in teams]

    def get_teams_by_group(self, group_id: int) -> list[TeamResponseDTO]:
        """Retrieve all teams in a specific group."""
        teams = self._team_repository.find_by_group_id(group_id)
        return [self._map_to_response_dto(team) for team in teams]

    def update_team(
        self,
        requester_role: UserRole,
        team_id: int,
        team_data: UpdateTeamDTO,
    ) -> TeamResponseDTO:
        """Update team information."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        existing_team = self._team_repository.find_by_id(team_id)
        if not existing_team:
            raise ValidationError(f"Team with ID {team_id} not found.")

        self._validate_update_team_data(team_data)

        if team_data.name != existing_team["name"] and self._team_repository.name_exists(team_data.name):
            raise ValidationError(f"Team '{team_data.name}' already exists.")

        if team_data.fifa_code != existing_team["fifa_code"] and self._team_repository.fifa_code_exists(
            team_data.fifa_code
        ):
            raise ValidationError(f"FIFA code '{team_data.fifa_code}' is already in use.")

        self._team_repository.update(
            team_id=team_id,
            name=team_data.name,
            fifa_code=team_data.fifa_code,
            team_weight=team_data.team_weight,
            market_value=team_data.market_value,
            group_id=team_data.group_id,
        )

        updated_team = self._team_repository.find_by_id(team_id)
        return self._map_to_response_dto(updated_team)

    def delete_team(self, requester_role: UserRole, team_id: int) -> None:
        """Delete a team. Team must not have players, coaches, or matches."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        team = self._team_repository.find_by_id(team_id)
        if not team:
            raise ValidationError(f"Team with ID {team_id} not found.")

        if self._team_repository.has_players(team_id):
            raise ValidationError(f"Cannot delete team '{team['name']}'. It has players assigned.")

        if self._team_repository.has_coach(team_id):
            raise ValidationError(f"Cannot delete team '{team['name']}'. It has a coach assigned.")

        if self._team_repository.has_matches(team_id):
            raise ValidationError(f"Cannot delete team '{team['name']}'. It has matches scheduled or played.")

        self._team_repository.delete(team_id)

    def _validate_base_team_data(self, team_data: CreateTeamDTO | UpdateTeamDTO) -> None:
        """Validate fields shared by team create and update flows."""
        validate_not_blank(team_data.name, "Team name")
        validate_not_blank(team_data.fifa_code, "FIFA code")

        if len(team_data.fifa_code) != 3:
            raise ValidationError("FIFA code must be exactly 3 characters.")

        validate_positive_number(team_data.team_weight, "Team weight")
        validate_positive_number(team_data.market_value, "Market value")

    def _validate_create_team_data(self, team_data: CreateTeamDTO) -> None:
        """Validate create team data, including immutable relationships."""
        self._validate_base_team_data(team_data)

        if team_data.country_id <= 0:
            raise ValidationError("Country ID must be positive.")

        if team_data.confederation_id <= 0:
            raise ValidationError("Confederation ID must be positive.")

    def _validate_update_team_data(self, team_data: UpdateTeamDTO) -> None:
        """Validate update team data without requiring immutable foreign keys."""
        self._validate_base_team_data(team_data)

    @staticmethod
    def _map_to_response_dto(team_data: dict) -> TeamResponseDTO:
        """Map repository row to response DTO."""
        return TeamResponseDTO(
            id=team_data["id"],
            name=team_data["name"],
            fifa_code=team_data["fifa_code"],
            country_id=team_data["country_id"],
            confederation_id=team_data["confederation_id"],
            team_weight=team_data["team_weight"],
            market_value=team_data["market_value"],
            group_id=team_data.get("group_id"),
        )
