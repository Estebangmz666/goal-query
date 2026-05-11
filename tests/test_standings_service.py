import unittest

try:
    from src.dto.standings_models import QualifiedTeamDTO
    from src.services.standings_service import StandingsService
except ModuleNotFoundError:
    from dto.standings_models import QualifiedTeamDTO
    from services.standings_service import StandingsService


class FakeStandingsRepository:
    def __init__(self) -> None:
        self.saved_records = []

    def get_group_standings(self, group_id: int) -> list[dict]:
        return [
            {
                "team_id": 1,
                "team_name": "Argentina",
                "matches_played": 3,
                "points": 7,
                "goals_for": 5,
                "goals_against": 2,
            },
            {
                "team_id": 2,
                "team_name": "Poland",
                "matches_played": 3,
                "points": 4,
                "goals_for": 3,
                "goals_against": 3,
            },
        ]

    def get_all_qualified_teams(self, limit_per_group: int = 2) -> list[dict]:
        return [
            {"team_id": 1, "team_name": "Argentina", "group_id": 1, "points": 7},
            {"team_id": 2, "team_name": "Poland", "group_id": 1, "points": 4},
            {"team_id": 3, "team_name": "Brazil", "group_id": 2, "points": 9},
            {"team_id": 4, "team_name": "Japan", "group_id": 2, "points": 6},
        ]

    def create_standings_record(
        self,
        team_id: int,
        group_id: int,
        matches_played: int,
        points: int,
        goals_for: int,
        goals_against: int,
    ) -> None:
        self.saved_records.append(
            {
                "team_id": team_id,
                "group_id": group_id,
                "matches_played": matches_played,
                "points": points,
                "goals_for": goals_for,
                "goals_against": goals_against,
            }
        )


class FakeMatchRepository:
    def find_by_id(self, match_id: int) -> dict | None:
        return {"id": match_id, "group_id": 1}

    def has_result(self, match_id: int) -> bool:
        return True


class StandingsServiceTestCase(unittest.TestCase):
    def test_calculate_standings_after_match_persists_group_entries(self) -> None:
        standings_repository = FakeStandingsRepository()
        service = StandingsService(standings_repository, FakeMatchRepository())

        service.calculate_standings_after_match(10)

        self.assertEqual(2, len(standings_repository.saved_records))
        self.assertEqual(1, standings_repository.saved_records[0]["group_id"])

    def test_get_qualified_teams_preserves_group_positions(self) -> None:
        service = StandingsService(FakeStandingsRepository(), FakeMatchRepository())

        qualified_teams = service.get_qualified_teams()

        self.assertEqual(4, len(qualified_teams))
        self.assertEqual(1, qualified_teams[0].position_in_group)
        self.assertEqual(2, qualified_teams[1].position_in_group)
        self.assertEqual(1, qualified_teams[2].position_in_group)
        self.assertEqual(2, qualified_teams[3].position_in_group)

    def test_group_stage_team_statuses_mark_non_qualified_teams_as_eliminated(self) -> None:
        class ExpandedStandingsRepository(FakeStandingsRepository):
            def get_group_standings(self, group_id: int) -> list[dict]:
                if group_id == 1:
                    return [
                        {
                            "team_id": 1,
                            "team_name": "Argentina",
                            "matches_played": 3,
                            "points": 7,
                            "goals_for": 5,
                            "goals_against": 2,
                        },
                        {
                            "team_id": 2,
                            "team_name": "Poland",
                            "matches_played": 3,
                            "points": 4,
                            "goals_for": 3,
                            "goals_against": 3,
                        },
                        {
                            "team_id": 5,
                            "team_name": "Mexico",
                            "matches_played": 3,
                            "points": 2,
                            "goals_for": 1,
                            "goals_against": 4,
                        },
                    ]

                return []

        service = StandingsService(ExpandedStandingsRepository(), FakeMatchRepository())

        statuses = service.get_group_stage_team_statuses(limit_per_group=2)

        self.assertEqual(3, len(statuses))
        self.assertTrue(statuses[0].is_qualified_to_knockout)
        self.assertFalse(statuses[0].is_eliminated_from_tournament)
        self.assertTrue(statuses[2].is_eliminated_from_tournament)
        self.assertFalse(statuses[2].is_qualified_to_knockout)


if __name__ == "__main__":
    unittest.main()
