try:
    from src.domain.enums.permission import Permission
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.city_models import CreateCityDTO, CityResponseDTO, UpdateCityDTO
    from src.repositories.city_repository import CityRepository
    from src.services.authorization_service import AuthorizationService
    from src.utils.validators import validate_not_blank
except ModuleNotFoundError:
    from domain.enums.permission import Permission
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.city_models import CreateCityDTO, CityResponseDTO, UpdateCityDTO
    from repositories.city_repository import CityRepository
    from services.authorization_service import AuthorizationService
    from utils.validators import validate_not_blank


class CityService:
    def __init__(
        self,
        city_repository: CityRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._city_repository = city_repository
        self._authorization_service = authorization_service

    def create_city(
        self,
        requester_role: UserRole,
        city_data: CreateCityDTO,
    ) -> CityResponseDTO:
        """Create a new city."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        self._validate_city_data(city_data)

        if not self._city_repository.country_exists(city_data.country_id):
            raise ValidationError(f"Country with ID {city_data.country_id} does not exist.")

        if self._city_repository.name_exists(city_data.name):
            raise ValidationError(f"City '{city_data.name}' already exists.")

        city_id = self._city_repository.create(
            country_id=city_data.country_id,
            name=city_data.name,
        )

        return CityResponseDTO(
            id=city_id,
            country_id=city_data.country_id,
            name=city_data.name,
        )

    def get_city(self, city_id: int) -> CityResponseDTO:
        """Retrieve a city by ID."""
        city_data = self._city_repository.find_by_id(city_id)
        if not city_data:
            raise ValidationError(f"City with ID {city_id} not found.")

        return self._map_to_response_dto(city_data)

    def get_all_cities(self) -> list[CityResponseDTO]:
        """Retrieve all cities."""
        cities = self._city_repository.find_all()
        return [self._map_to_response_dto(city) for city in cities]

    def get_cities_by_country(self, country_id: int) -> list[CityResponseDTO]:
        """Retrieve all cities in a country."""
        cities = self._city_repository.find_by_country(country_id)
        return [self._map_to_response_dto(city) for city in cities]

    def get_cities_in_host_countries(self) -> list[CityResponseDTO]:
        """Retrieve all cities in host countries."""
        cities = self._city_repository.find_in_host_countries()
        return [self._map_to_response_dto(city) for city in cities]

    def update_city(
        self,
        requester_role: UserRole,
        city_id: int,
        city_data: UpdateCityDTO,
    ) -> CityResponseDTO:
        """Update city information."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        existing_city = self._city_repository.find_by_id(city_id)
        if not existing_city:
            raise ValidationError(f"City with ID {city_id} not found.")

        self._validate_city_data(city_data)

        if city_data.name != existing_city["name"] and self._city_repository.name_exists(city_data.name):
            raise ValidationError(f"City '{city_data.name}' already exists.")

        self._city_repository.update(city_id=city_id, name=city_data.name)

        updated_city = self._city_repository.find_by_id(city_id)
        return self._map_to_response_dto(updated_city)

    def delete_city(self, requester_role: UserRole, city_id: int) -> None:
        """Delete a city. City must not have stadiums."""
        self._authorization_service.authorize(requester_role, Permission.MANAGE_TEAMS)

        city = self._city_repository.find_by_id(city_id)
        if not city:
            raise ValidationError(f"City with ID {city_id} not found.")

        if self._city_repository.has_stadiums(city_id):
            raise ValidationError(f"Cannot delete city '{city['name']}'. It has stadiums assigned.")

        self._city_repository.delete(city_id)

    def _validate_city_data(self, city_data: CreateCityDTO | UpdateCityDTO) -> None:
        """Validate city data."""
        validate_not_blank(city_data.name, "City name")

        if hasattr(city_data, "country_id") and city_data.country_id <= 0:
            raise ValidationError("Country ID must be positive.")

    @staticmethod
    def _map_to_response_dto(city_data: dict) -> CityResponseDTO:
        """Map repository row to response DTO."""
        return CityResponseDTO(
            id=city_data["id"],
            country_id=city_data["country_id"],
            name=city_data["name"],
        )
