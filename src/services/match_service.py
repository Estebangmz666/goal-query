from datetime import datetime

try:
    from src.domain.enums.match_phase import MatchPhase
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.match_models import CreateMatchDTO, MatchResponseDTO, UpdateMatchDTO, MatchResultDTO
    from src.repositories.match_repository import MatchRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank
except ModuleNotFoundError:
    from domain.enums.match_phase import MatchPhase
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.match_models import CreateMatchDTO, MatchResponseDTO, UpdateMatchDTO, MatchResultDTO
    from repositories.match_repository import MatchRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank


class MatchService:
    def __init__(
        self,
        match_repository: MatchRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._match_repository = match_repository
        self._authorization_service = authorization_service

    def create_match(
        self,
        requester_role: UserRole,
        match_data: CreateMatchDTO,
    ) -> MatchResponseDTO:
        """Create a new match."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_MATCHES)

        self._validate_match_data(match_data)

        if not self._match_repository.stadium_exists(match_data.stadium_id):
            raise ValidationError(f"Stadium with ID {match_data.stadium_id} does not exist.")

        if not self._match_repository.team_exists(match_data.home_team_id):
            raise ValidationError(f"Team with ID {match_data.home_team_id} does not exist.")

        if not self._match_repository.team_exists(match_data.away_team_id):
            raise ValidationError(f"Team with ID {match_data.away_team_id} does not exist.")

        if match_data.home_team_id == match_data.away_team_id:
            raise ValidationError("Home and away teams cannot be the same.")

        if match_data.group_id is not None and not self._match_repository.group_exists(match_data.group_id):
            raise ValidationError(f"Group with ID {match_data.group_id} does not exist.")

        match_id = self._match_repository.create(
            stadium_id=match_data.stadium_id,
            group_id=match_data.group_id,
            phase=match_data.phase,
            home_team_id=match_data.home_team_id,
            away_team_id=match_data.away_team_id,
            scheduled_at=match_data.scheduled_at,
        )

        return MatchResponseDTO(
            id=match_id,
            stadium_id=match_data.stadium_id,
            group_id=match_data.group_id,
            phase=match_data.phase,
            home_team_id=match_data.home_team_id,
            away_team_id=match_data.away_team_id,
            scheduled_at=match_data.scheduled_at,
        )

    def get_match(self, match_id: int) -> MatchResponseDTO:
        """Retrieve a match by ID."""
        match_data = self._match_repository.find_by_id(match_id)
        if not match_data:
            raise ValidationError(f"Match with ID {match_id} not found.")

        return self._map_to_response_dto(match_data)

    def get_all_matches(self) -> list[MatchResponseDTO]:
        """Retrieve all matches."""
        matches = self._match_repository.find_all()
        return [self._map_to_response_dto(match) for match in matches]

    def get_matches_by_stadium(self, stadium_id: int) -> list[MatchResponseDTO]:
        """Retrieve all matches in a stadium."""
        matches = self._match_repository.find_by_stadium(stadium_id)
        return [self._map_to_response_dto(match) for match in matches]

    def get_matches_by_group(self, group_id: int) -> list[MatchResponseDTO]:
        """Retrieve all group stage matches in a group."""
        matches = self._match_repository.find_by_group(group_id)
        return [self._map_to_response_dto(match) for match in matches]

    def get_matches_by_phase(self, phase: str) -> list[MatchResponseDTO]:
        """Retrieve all matches in a specific phase."""
        matches = self._match_repository.find_by_phase(phase)
        return [self._map_to_response_dto(match) for match in matches]

    def get_matches_by_team(self, team_id: int) -> list[MatchResponseDTO]:
        """Retrieve all matches for a team."""
        matches = self._match_repository.find_by_team(team_id)
        return [self._map_to_response_dto(match) for match in matches]

    def update_match(
        self,
        requester_role: UserRole,
        match_id: int,
        match_data: UpdateMatchDTO,
    ) -> MatchResponseDTO:
        """Update match information (before playing)."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_MATCHES)

        existing_match = self._match_repository.find_by_id(match_id)
        if not existing_match:
            raise ValidationError(f"Match with ID {match_id} not found.")

        if self._match_repository.has_result(match_id):
            raise ValidationError("Cannot update a match that has already been played.")

        if not self._match_repository.stadium_exists(match_data.stadium_id):
            raise ValidationError(f"Stadium with ID {match_data.stadium_id} does not exist.")

        self._match_repository.update(
            match_id=match_id,
            stadium_id=match_data.stadium_id,
            scheduled_at=match_data.scheduled_at,
        )

        updated_match = self._match_repository.find_by_id(match_id)
        return self._map_to_response_dto(updated_match)

    def delete_match(self, requester_role: UserRole, match_id: int) -> None:
        """Delete a match. Can only delete if not yet played."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_MATCHES)

        match = self._match_repository.find_by_id(match_id)
        if not match:
            raise ValidationError(f"Match with ID {match_id} not found.")

        if self._match_repository.has_result(match_id):
            raise ValidationError("Cannot delete a match that has already been played.")

        self._match_repository.delete(match_id)

    def save_match_result(
        self,
        match_id: int,
        home_goals: int,
        away_goals: int,
        played_at: datetime | None = None,
    ) -> None:
        """Save or update match result."""
        match = self._match_repository.find_by_id(match_id)
        if not match:
            raise ValidationError(f"Match with ID {match_id} not found.")

        if home_goals < 0 or away_goals < 0:
            raise ValidationError("Goals cannot be negative.")

        played_at = played_at or datetime.now()
        self._match_repository.save_match_result(match_id, home_goals, away_goals, played_at)

    def _validate_match_data(self, match_data: CreateMatchDTO) -> None:
        """Validate match data."""
        if match_data.stadium_id <= 0:
            raise ValidationError("Stadium ID must be positive.")

        if match_data.home_team_id <= 0 or match_data.away_team_id <= 0:
            raise ValidationError("Team IDs must be positive.")

        if match_data.group_id is not None and match_data.group_id <= 0:
            raise ValidationError("Group ID must be positive.")

        try:
            MatchPhase(match_data.phase)
        except ValueError:
            raise ValidationError(f"Invalid match phase: {match_data.phase}")

        if match_data.scheduled_at < datetime.now():
            raise ValidationError("Match cannot be scheduled in the past.")

    @staticmethod
    def _map_to_response_dto(match_data: dict) -> MatchResponseDTO:
        """Map repository row to response DTO."""
        return MatchResponseDTO(
            id=match_data["id"],
            stadium_id=match_data["stadium_id"],
            group_id=match_data.get("group_id"),
            phase=match_data["phase"],
            home_team_id=match_data["home_team_id"],
            away_team_id=match_data["away_team_id"],
            scheduled_at=match_data["scheduled_at"],
        )
