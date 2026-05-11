from datetime import date
import unittest

try:
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.player_models import CreatePlayerDTO
    from src.services.player_service import MAX_PLAYERS_PER_TEAM, PlayerService
except ModuleNotFoundError:
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.player_models import CreatePlayerDTO
    from services.player_service import MAX_PLAYERS_PER_TEAM, PlayerService


class FakePlayerRepository:
    def __init__(self, existing_count: int = 0, duplicate_shirt_number: bool = False) -> None:
        self._existing_count = existing_count
        self._duplicate_shirt_number = duplicate_shirt_number
        self.created_payload = None

    def team_exists(self, team_id: int) -> bool:
        return team_id == 1

    def count_by_team(self, team_id: int) -> int:
        return self._existing_count

    def shirt_number_exists_in_team(self, team_id: int, shirt_number: int) -> bool:
        return self._duplicate_shirt_number

    def create(
        self,
        team_id: int,
        first_name: str,
        last_name: str,
        position: str,
        shirt_number: int,
        date_of_birth: date,
        height_cm: float,
        weight_kg: float,
        market_value: float,
    ) -> int:
        self.created_payload = {
            "team_id": team_id,
            "first_name": first_name,
            "last_name": last_name,
            "position": position,
            "shirt_number": shirt_number,
            "date_of_birth": date_of_birth,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "market_value": market_value,
        }
        return 99


class FakeAuthorizationService:
    def authorize(self, role: UserRole, permission) -> None:
        if role == UserRole.SPORADIC_USER:
            raise ValidationError("Sporadic users cannot manage players.")


class PlayerServiceTestCase(unittest.TestCase):
    def _build_player_data(self) -> CreatePlayerDTO:
        return CreatePlayerDTO(
            team_id=1,
            first_name="Luis",
            last_name="Diaz",
            position="Forward",
            shirt_number=7,
            date_of_birth=date(1998, 1, 13),
            height_cm=178.0,
            weight_kg=72.0,
            market_value=75000000.0,
        )

    def test_create_player_accepts_twenty_third_slot(self) -> None:
        repository = FakePlayerRepository(existing_count=MAX_PLAYERS_PER_TEAM - 1)
        service = PlayerService(repository, FakeAuthorizationService())

        result = service.create_player(UserRole.ADMINISTRATOR, self._build_player_data())

        self.assertEqual(99, result.id)
        self.assertEqual(1, repository.created_payload["team_id"])

    def test_create_player_rejects_twenty_fourth_player(self) -> None:
        repository = FakePlayerRepository(existing_count=MAX_PLAYERS_PER_TEAM)
        service = PlayerService(repository, FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.create_player(UserRole.ADMINISTRATOR, self._build_player_data())

        self.assertIn(str(MAX_PLAYERS_PER_TEAM), str(context.exception))

    def test_create_player_rejects_duplicate_shirt_number(self) -> None:
        repository = FakePlayerRepository(existing_count=5, duplicate_shirt_number=True)
        service = PlayerService(repository, FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.create_player(UserRole.ADMINISTRATOR, self._build_player_data())

        self.assertIn("Shirt number", str(context.exception))


if __name__ == "__main__":
    unittest.main()
