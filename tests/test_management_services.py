from datetime import datetime, timedelta
import unittest

try:
    from src.domain.enums.match_phase import MatchPhase
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.city_models import CreateCityDTO
    from src.dto.coach_models import CreateCoachDTO
    from src.dto.match_models import CreateMatchDTO
    from src.dto.stadium_models import CreateStadiumDTO
    from src.services.city_service import CityService
    from src.services.coach_service import CoachService
    from src.services.match_service import MatchService
    from src.services.stadium_service import StadiumService
except ModuleNotFoundError:
    from domain.enums.match_phase import MatchPhase
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.city_models import CreateCityDTO
    from dto.coach_models import CreateCoachDTO
    from dto.match_models import CreateMatchDTO
    from dto.stadium_models import CreateStadiumDTO
    from services.city_service import CityService
    from services.coach_service import CoachService
    from services.match_service import MatchService
    from services.stadium_service import StadiumService


class FakeAuthorizationService:
    def authorize(self, role: UserRole, permission) -> None:
        if role == UserRole.SPORADIC_USER:
            raise ValidationError("Role not allowed.")


class FakeCoachRepository:
    def team_exists(self, team_id: int) -> bool:
        return True

    def country_exists(self, country_id: int) -> bool:
        return True

    def coach_exists_for_team(self, team_id: int) -> bool:
        return True


class FakeCityRepository:
    def find_by_id(self, city_id: int) -> dict | None:
        return {"id": city_id, "country_id": 1, "name": "Bogota"}

    def has_stadiums(self, city_id: int) -> bool:
        return True


class FakeStadiumRepository:
    def find_by_id(self, stadium_id: int) -> dict | None:
        return {"id": stadium_id, "city_id": 1, "name": "Metropolitano", "capacity": 46000}

    def has_matches(self, stadium_id: int) -> bool:
        return True


class FakeMatchRepository:
    def stadium_exists(self, stadium_id: int) -> bool:
        return stadium_id == 1

    def team_exists(self, team_id: int) -> bool:
        return team_id in {10, 11}

    def group_exists(self, group_id: int) -> bool:
        return group_id == 2

    def create(
        self,
        stadium_id: int,
        group_id: int | None,
        phase: str,
        home_team_id: int,
        away_team_id: int,
        scheduled_at: datetime,
    ) -> int:
        return 5

    def find_by_id(self, match_id: int) -> dict | None:
        return {
            "id": match_id,
            "stadium_id": 1,
            "group_id": 2,
            "phase": MatchPhase.GROUP_STAGE.value,
            "home_team_id": 10,
            "away_team_id": 11,
            "scheduled_at": datetime.now() + timedelta(days=3),
        }

    def has_result(self, match_id: int) -> bool:
        return True


class ManagementServicesTestCase(unittest.TestCase):
    def test_create_coach_rejects_second_coach_for_team(self) -> None:
        service = CoachService(FakeCoachRepository(), FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.create_coach(
                UserRole.ADMINISTRATOR,
                CreateCoachDTO(
                    team_id=1,
                    first_name="Nestor",
                    last_name="Lorenzo",
                    nationality_country_id=1,
                ),
            )

        self.assertIn("already has a coach", str(context.exception))

    def test_delete_city_rejects_when_city_has_stadiums(self) -> None:
        service = CityService(FakeCityRepository(), FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.delete_city(UserRole.ADMINISTRATOR, 1)

        self.assertIn("has stadiums", str(context.exception))

    def test_delete_stadium_rejects_when_stadium_has_matches(self) -> None:
        service = StadiumService(FakeStadiumRepository(), FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.delete_stadium(UserRole.ADMINISTRATOR, 1)

        self.assertIn("has matches", str(context.exception))

    def test_create_match_rejects_same_team_for_home_and_away(self) -> None:
        service = MatchService(FakeMatchRepository(), FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.create_match(
                UserRole.ADMINISTRATOR,
                CreateMatchDTO(
                    stadium_id=1,
                    group_id=2,
                    phase=MatchPhase.GROUP_STAGE.value,
                    home_team_id=10,
                    away_team_id=10,
                    scheduled_at=datetime.now() + timedelta(days=1),
                ),
            )

        self.assertIn("cannot be the same", str(context.exception))

    def test_delete_match_rejects_when_result_exists(self) -> None:
        service = MatchService(FakeMatchRepository(), FakeAuthorizationService())

        with self.assertRaises(ValidationError) as context:
            service.delete_match(UserRole.ADMINISTRATOR, 3)

        self.assertIn("already been played", str(context.exception))


if __name__ == "__main__":
    unittest.main()
