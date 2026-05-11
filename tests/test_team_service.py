import unittest

try:
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.team_models import CreateTeamDTO, TeamResponseDTO, UpdateTeamDTO
    from src.services.team_service import TeamService
except ModuleNotFoundError:
    from domain.enums.user_role import UserRole
    from domain.exceptions.validation_error import ValidationError
    from dto.team_models import CreateTeamDTO, TeamResponseDTO, UpdateTeamDTO
    from services.team_service import TeamService


class FakeTeamRepository:
    def __init__(self) -> None:
        self._teams = {}
        self._next_id = 1

    def find_by_id(self, team_id: int) -> dict | None:
        return self._teams.get(team_id)

    def find_all(self) -> list[dict]:
        return list(self._teams.values())

    def find_by_group_id(self, group_id: int) -> list[dict]:
        return [t for t in self._teams.values() if t.get("group_id") == group_id]

    def create(
        self,
        name: str,
        fifa_code: str,
        country_id: int,
        confederation_id: int,
        team_weight: float,
        market_value: float,
        group_id: int | None,
    ) -> int:
        team_id = self._next_id
        self._next_id += 1
        self._teams[team_id] = {
            "id": team_id,
            "name": name,
            "fifa_code": fifa_code,
            "country_id": country_id,
            "confederation_id": confederation_id,
            "team_weight": team_weight,
            "market_value": market_value,
            "group_id": group_id,
        }
        return team_id

    def update(
        self,
        team_id: int,
        name: str,
        fifa_code: str,
        team_weight: float,
        market_value: float,
        group_id: int | None,
    ) -> None:
        if team_id in self._teams:
            self._teams[team_id].update(
                {
                    "name": name,
                    "fifa_code": fifa_code,
                    "team_weight": team_weight,
                    "market_value": market_value,
                    "group_id": group_id,
                }
            )

    def delete(self, team_id: int) -> None:
        if team_id in self._teams:
            del self._teams[team_id]

    def name_exists(self, name: str) -> bool:
        return any(t["name"] == name for t in self._teams.values())

    def fifa_code_exists(self, fifa_code: str) -> bool:
        return any(t["fifa_code"] == fifa_code for t in self._teams.values())

    def has_players(self, team_id: int) -> bool:
        return False

    def has_coach(self, team_id: int) -> bool:
        return False

    def has_matches(self, team_id: int) -> bool:
        return False


class FakeAuthorizationService:
    def authorize(self, role: UserRole, permission: str) -> None:
        if role == UserRole.SPORADIC_USER:
            raise ValidationError("Sporadic users cannot manage teams.")


class TeamServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.team_repository = FakeTeamRepository()
        self.authorization_service = FakeAuthorizationService()
        self.service = TeamService(self.team_repository, self.authorization_service)

    def test_create_team_success(self) -> None:
        """Test successful team creation."""
        team_data = CreateTeamDTO(
            name="Argentina",
            fifa_code="ARG",
            country_id=1,
            confederation_id=1,
            team_weight=8.5,
            market_value=500000000.0,
            group_id=1,
        )

        result = self.service.create_team(UserRole.ADMINISTRATOR, team_data)

        self.assertEqual(result.name, "Argentina")
        self.assertEqual(result.fifa_code, "ARG")
        self.assertEqual(result.country_id, 1)
        self.assertEqual(result.team_weight, 8.5)
        self.assertIsNotNone(result.id)

    def test_create_team_duplicate_name(self) -> None:
        """Test that duplicate team names are rejected."""
        team_data = CreateTeamDTO(
            name="Brazil",
            fifa_code="BRA",
            country_id=2,
            confederation_id=1,
            team_weight=8.0,
            market_value=450000000.0,
        )

        self.service.create_team(UserRole.ADMINISTRATOR, team_data)

        with self.assertRaises(ValidationError) as context:
            self.service.create_team(UserRole.ADMINISTRATOR, team_data)

        self.assertIn("already exists", str(context.exception))

    def test_create_team_duplicate_fifa_code(self) -> None:
        """Test that duplicate FIFA codes are rejected."""
        team1 = CreateTeamDTO(
            name="France",
            fifa_code="FRA",
            country_id=3,
            confederation_id=2,
            team_weight=7.8,
            market_value=400000000.0,
        )
        team2 = CreateTeamDTO(
            name="French Team",
            fifa_code="FRA",
            country_id=4,
            confederation_id=2,
            team_weight=7.0,
            market_value=350000000.0,
        )

        self.service.create_team(UserRole.ADMINISTRATOR, team1)

        with self.assertRaises(ValidationError) as context:
            self.service.create_team(UserRole.ADMINISTRATOR, team2)

        self.assertIn("FIFA code", str(context.exception))

    def test_create_team_blank_name(self) -> None:
        """Test that blank team names are rejected."""
        team_data = CreateTeamDTO(
            name="",
            fifa_code="XXX",
            country_id=5,
            confederation_id=2,
            team_weight=5.0,
            market_value=100000000.0,
        )

        with self.assertRaises(ValidationError):
            self.service.create_team(UserRole.ADMINISTRATOR, team_data)

    def test_create_team_invalid_fifa_code_length(self) -> None:
        """Test that FIFA codes must be 3 characters."""
        team_data = CreateTeamDTO(
            name="Germany",
            fifa_code="GER1",
            country_id=6,
            confederation_id=2,
            team_weight=7.5,
            market_value=380000000.0,
        )

        with self.assertRaises(ValidationError) as context:
            self.service.create_team(UserRole.ADMINISTRATOR, team_data)

        self.assertIn("3 characters", str(context.exception))

    def test_create_team_negative_weight(self) -> None:
        """Test that team weight must be positive."""
        team_data = CreateTeamDTO(
            name="Spain",
            fifa_code="ESP",
            country_id=7,
            confederation_id=2,
            team_weight=-5.0,
            market_value=300000000.0,
        )

        with self.assertRaises(ValidationError):
            self.service.create_team(UserRole.ADMINISTRATOR, team_data)

    def test_create_team_sporadic_user_denied(self) -> None:
        """Test that sporadic users cannot create teams."""
        team_data = CreateTeamDTO(
            name="Italy",
            fifa_code="ITA",
            country_id=8,
            confederation_id=2,
            team_weight=7.2,
            market_value=320000000.0,
        )

        with self.assertRaises(ValidationError):
            self.service.create_team(UserRole.SPORADIC_USER, team_data)

    def test_get_team(self) -> None:
        """Test retrieving a team by ID."""
        team_data = CreateTeamDTO(
            name="Portugal",
            fifa_code="POR",
            country_id=9,
            confederation_id=2,
            team_weight=6.8,
            market_value=280000000.0,
        )

        created = self.service.create_team(UserRole.ADMINISTRATOR, team_data)
        retrieved = self.service.get_team(created.id)

        self.assertEqual(retrieved.name, "Portugal")
        self.assertEqual(retrieved.fifa_code, "POR")

    def test_get_team_not_found(self) -> None:
        """Test that retrieving non-existent team raises error."""
        with self.assertRaises(ValidationError) as context:
            self.service.get_team(999)

        self.assertIn("not found", str(context.exception))

    def test_update_team(self) -> None:
        """Test updating team information."""
        team_data = CreateTeamDTO(
            name="Netherlands",
            fifa_code="NED",
            country_id=10,
            confederation_id=2,
            team_weight=6.5,
            market_value=250000000.0,
            group_id=1,
        )

        created = self.service.create_team(UserRole.ADMINISTRATOR, team_data)

        update_data = UpdateTeamDTO(
            name="Netherlands Updated",
            fifa_code="NED",
            team_weight=7.0,
            market_value=260000000.0,
            group_id=2,
        )

        updated = self.service.update_team(UserRole.TRADITIONAL_USER, created.id, update_data)

        self.assertEqual(updated.name, "Netherlands Updated")
        self.assertEqual(updated.team_weight, 7.0)
        self.assertEqual(updated.group_id, 2)

    def test_get_all_teams(self) -> None:
        """Test retrieving all teams."""
        self.service.create_team(
            UserRole.ADMINISTRATOR,
            CreateTeamDTO(
                name="Team A",
                fifa_code="TEA",
                country_id=1,
                confederation_id=1,
                team_weight=5.0,
                market_value=100000000.0,
            ),
        )
        self.service.create_team(
            UserRole.ADMINISTRATOR,
            CreateTeamDTO(
                name="Team B",
                fifa_code="TEB",
                country_id=2,
                confederation_id=1,
                team_weight=6.0,
                market_value=150000000.0,
            ),
        )

        teams = self.service.get_all_teams()

        self.assertEqual(len(teams), 2)

    def test_delete_team(self) -> None:
        """Test deleting a team."""
        team_data = CreateTeamDTO(
            name="Test Team",
            fifa_code="TTE",
            country_id=11,
            confederation_id=3,
            team_weight=5.0,
            market_value=100000000.0,
        )

        created = self.service.create_team(UserRole.ADMINISTRATOR, team_data)
        self.service.delete_team(UserRole.ADMINISTRATOR, created.id)

        with self.assertRaises(ValidationError):
            self.service.get_team(created.id)


if __name__ == "__main__":
    unittest.main()
