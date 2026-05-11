try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.stadium_models import CreateStadiumDTO, StadiumResponseDTO, UpdateStadiumDTO
    from src.repositories.stadium_repository import StadiumRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank, validate_positive_number
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.stadium_models import CreateStadiumDTO, StadiumResponseDTO, UpdateStadiumDTO
    from repositories.stadium_repository import StadiumRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank, validate_positive_number


class StadiumService:
    def __init__(
        self,
        stadium_repository: StadiumRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._stadium_repository = stadium_repository
        self._authorization_service = authorization_service

    def create_stadium(
        self,
        requester_role: UserRole,
        stadium_data: CreateStadiumDTO,
    ) -> StadiumResponseDTO:
        """Create a new stadium."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        self._validate_stadium_data(stadium_data)

        if not self._stadium_repository.city_exists(stadium_data.city_id):
            raise ValidationError(f"City with ID {stadium_data.city_id} does not exist.")

        if self._stadium_repository.name_exists(stadium_data.name):
            raise ValidationError(f"Stadium '{stadium_data.name}' already exists.")

        stadium_id = self._stadium_repository.create(
            city_id=stadium_data.city_id,
            name=stadium_data.name,
            capacity=stadium_data.capacity,
        )

        return StadiumResponseDTO(
            id=stadium_id,
            city_id=stadium_data.city_id,
            name=stadium_data.name,
            capacity=stadium_data.capacity,
        )

    def get_stadium(self, stadium_id: int) -> StadiumResponseDTO:
        """Retrieve a stadium by ID."""
        stadium_data = self._stadium_repository.find_by_id(stadium_id)
        if not stadium_data:
            raise ValidationError(f"Stadium with ID {stadium_id} not found.")

        return self._map_to_response_dto(stadium_data)

    def get_all_stadiums(self) -> list[StadiumResponseDTO]:
        """Retrieve all stadiums."""
        stadiums = self._stadium_repository.find_all()
        return [self._map_to_response_dto(stadium) for stadium in stadiums]

    def get_stadiums_by_city(self, city_id: int) -> list[StadiumResponseDTO]:
        """Retrieve all stadiums in a city."""
        stadiums = self._stadium_repository.find_by_city(city_id)
        return [self._map_to_response_dto(stadium) for stadium in stadiums]

    def update_stadium(
        self,
        requester_role: UserRole,
        stadium_id: int,
        stadium_data: UpdateStadiumDTO,
    ) -> StadiumResponseDTO:
        """Update stadium information."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        existing_stadium = self._stadium_repository.find_by_id(stadium_id)
        if not existing_stadium:
            raise ValidationError(f"Stadium with ID {stadium_id} not found.")

        self._validate_stadium_data(stadium_data)

        if stadium_data.name != existing_stadium["name"] and self._stadium_repository.name_exists(
            stadium_data.name
        ):
            raise ValidationError(f"Stadium '{stadium_data.name}' already exists.")

        self._stadium_repository.update(
            stadium_id=stadium_id,
            name=stadium_data.name,
            capacity=stadium_data.capacity,
        )

        updated_stadium = self._stadium_repository.find_by_id(stadium_id)
        return self._map_to_response_dto(updated_stadium)

    def delete_stadium(self, requester_role: UserRole, stadium_id: int) -> None:
        """Delete a stadium. Stadium must not have matches."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        stadium = self._stadium_repository.find_by_id(stadium_id)
        if not stadium:
            raise ValidationError(f"Stadium with ID {stadium_id} not found.")

        if self._stadium_repository.has_matches(stadium_id):
            raise ValidationError(f"Cannot delete stadium '{stadium['name']}'. It has matches scheduled or played.")

        self._stadium_repository.delete(stadium_id)

    def _validate_stadium_data(self, stadium_data: CreateStadiumDTO | UpdateStadiumDTO) -> None:
        """Validate stadium data."""
        validate_not_blank(stadium_data.name, "Stadium name")
        validate_positive_number(stadium_data.capacity, "Capacity")

        if hasattr(stadium_data, "city_id") and stadium_data.city_id <= 0:
            raise ValidationError("City ID must be positive.")

    @staticmethod
    def _map_to_response_dto(stadium_data: dict) -> StadiumResponseDTO:
        """Map repository row to response DTO."""
        return StadiumResponseDTO(
            id=stadium_data["id"],
            city_id=stadium_data["city_id"],
            name=stadium_data["name"],
            capacity=stadium_data["capacity"],
        )
