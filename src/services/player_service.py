from datetime import date, datetime

try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.player_models import CreatePlayerDTO, PlayerResponseDTO, UpdatePlayerDTO
    from src.repositories.player_repository import PlayerRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank, validate_positive_number
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.player_models import CreatePlayerDTO, PlayerResponseDTO, UpdatePlayerDTO
    from repositories.player_repository import PlayerRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank, validate_positive_number


MAX_PLAYERS_PER_TEAM = 23
MIN_PLAYER_AGE = 16
MAX_PLAYER_AGE = 40


class PlayerService:
    def __init__(
        self,
        player_repository: PlayerRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._player_repository = player_repository
        self._authorization_service = authorization_service

    def create_player(
        self,
        requester_role: UserRole,
        player_data: CreatePlayerDTO,
    ) -> PlayerResponseDTO:
        """Create a new player."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_PLAYERS)

        self._validate_player_data(player_data)

        if not self._player_repository.team_exists(player_data.team_id):
            raise ValidationError(f"Team with ID {player_data.team_id} does not exist.")

        player_count = self._player_repository.count_by_team(player_data.team_id)
        if player_count >= MAX_PLAYERS_PER_TEAM:
            raise ValidationError(f"Team already has {MAX_PLAYERS_PER_TEAM} players. Cannot add more.")

        if self._player_repository.shirt_number_exists_in_team(player_data.team_id, player_data.shirt_number):
            raise ValidationError(f"Shirt number {player_data.shirt_number} is already used in this team.")

        player_id = self._player_repository.create(
            team_id=player_data.team_id,
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            position=player_data.position,
            shirt_number=player_data.shirt_number,
            date_of_birth=player_data.date_of_birth,
            height_cm=player_data.height_cm,
            weight_kg=player_data.weight_kg,
            market_value=player_data.market_value,
        )

        return PlayerResponseDTO(
            id=player_id,
            team_id=player_data.team_id,
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            position=player_data.position,
            shirt_number=player_data.shirt_number,
            date_of_birth=player_data.date_of_birth,
            height_cm=player_data.height_cm,
            weight_kg=player_data.weight_kg,
            market_value=player_data.market_value,
        )

    def get_player(self, player_id: int) -> PlayerResponseDTO:
        """Retrieve a player by ID."""
        player_data = self._player_repository.find_by_id(player_id)
        if not player_data:
            raise ValidationError(f"Player with ID {player_id} not found.")

        return self._map_to_response_dto(player_data)

    def get_all_players(self) -> list[PlayerResponseDTO]:
        """Retrieve all players."""
        players = self._player_repository.find_all()
        return [self._map_to_response_dto(player) for player in players]

    def get_players_by_team(self, team_id: int) -> list[PlayerResponseDTO]:
        """Retrieve all players in a team."""
        players = self._player_repository.find_by_team(team_id)
        return [self._map_to_response_dto(player) for player in players]

    def get_players_by_position(self, position: str) -> list[PlayerResponseDTO]:
        """Retrieve all players with a specific position."""
        players = self._player_repository.find_by_position(position)
        return [self._map_to_response_dto(player) for player in players]

    def get_team_player_count(self, team_id: int) -> int:
        """Get player count for a team."""
        return self._player_repository.count_by_team(team_id)

    def update_player(
        self,
        requester_role: UserRole,
        player_id: int,
        player_data: UpdatePlayerDTO,
    ) -> PlayerResponseDTO:
        """Update player information."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_PLAYERS)

        existing_player = self._player_repository.find_by_id(player_id)
        if not existing_player:
            raise ValidationError(f"Player with ID {player_id} not found.")

        self._validate_update_player_data(player_data)

        if player_data.shirt_number != existing_player["shirt_number"] and self._player_repository.shirt_number_exists_in_team(
            existing_player["team_id"], player_data.shirt_number
        ):
            raise ValidationError(f"Shirt number {player_data.shirt_number} is already used in this team.")

        self._player_repository.update(
            player_id=player_id,
            position=player_data.position,
            shirt_number=player_data.shirt_number,
            height_cm=player_data.height_cm,
            weight_kg=player_data.weight_kg,
            market_value=player_data.market_value,
        )

        updated_player = self._player_repository.find_by_id(player_id)
        return self._map_to_response_dto(updated_player)

    def delete_player(self, requester_role: UserRole, player_id: int) -> None:
        """Delete a player."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_PLAYERS)

        player = self._player_repository.find_by_id(player_id)
        if not player:
            raise ValidationError(f"Player with ID {player_id} not found.")

        self._player_repository.delete(player_id)

    def _validate_player_data(self, player_data: CreatePlayerDTO) -> None:
        """Validate player data."""
        validate_not_blank(player_data.first_name, "First name")
        validate_not_blank(player_data.last_name, "Last name")
        validate_not_blank(player_data.position, "Position")

        if player_data.team_id <= 0:
            raise ValidationError("Team ID must be positive.")

        if player_data.shirt_number < 1 or player_data.shirt_number > 99:
            raise ValidationError("Shirt number must be between 1 and 99.")

        validate_positive_number(player_data.height_cm, "Height")
        validate_positive_number(player_data.weight_kg, "Weight")
        validate_positive_number(player_data.market_value, "Market value")

        age = self._calculate_age(player_data.date_of_birth)
        if age < MIN_PLAYER_AGE:
            raise ValidationError(f"Player must be at least {MIN_PLAYER_AGE} years old.")

        if age > MAX_PLAYER_AGE:
            raise ValidationError(f"Player cannot be older than {MAX_PLAYER_AGE} years old.")

    def _validate_update_player_data(self, player_data: UpdatePlayerDTO) -> None:
        """Validate update player data."""
        validate_not_blank(player_data.position, "Position")

        if player_data.shirt_number < 1 or player_data.shirt_number > 99:
            raise ValidationError("Shirt number must be between 1 and 99.")

        validate_positive_number(player_data.height_cm, "Height")
        validate_positive_number(player_data.weight_kg, "Weight")
        validate_positive_number(player_data.market_value, "Market value")

    @staticmethod
    def _calculate_age(date_of_birth: date) -> int:
        """Calculate age from date of birth."""
        today = date.today()
        age = today.year - date_of_birth.year
        if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
            age -= 1
        return age

    @staticmethod
    def _map_to_response_dto(player_data: dict) -> PlayerResponseDTO:
        """Map repository row to response DTO."""
        return PlayerResponseDTO(
            id=player_data["id"],
            team_id=player_data["team_id"],
            first_name=player_data["first_name"],
            last_name=player_data["last_name"],
            position=player_data["position"],
            shirt_number=player_data["shirt_number"],
            date_of_birth=player_data["date_of_birth"],
            height_cm=player_data["height_cm"],
            weight_kg=player_data["weight_kg"],
            market_value=player_data["market_value"],
        )
