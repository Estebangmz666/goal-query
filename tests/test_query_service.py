from datetime import date
import unittest

try:
    from src.domain.exceptions.validation_error import ValidationError
    from src.services.query_service import QueryService
except ModuleNotFoundError:
    from domain.exceptions.validation_error import ValidationError
    from services.query_service import QueryService


class FakeQueryRepository:
    def __init__(self) -> None:
        self.received_stadium_id = None
        self.received_reference_date = None

    def get_most_expensive_player_by_confederation(self):
        return ["players"]

    def get_matches_by_stadium(self, stadium_id: int):
        self.received_stadium_id = stadium_id
        return ["matches"]

    def get_most_expensive_team_by_host_country(self):
        return ["teams"]

    def get_under_twenty_one_players_by_team(self, reference_date: date):
        self.received_reference_date = reference_date
        return ["young_players"]


class QueryServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = FakeQueryRepository()
        self.service = QueryService(self.repository)

    def test_get_matches_by_stadium_requires_positive_stadium_id(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.get_matches_by_stadium(0)

    def test_get_matches_by_stadium_delegates_to_repository(self) -> None:
        result = self.service.get_matches_by_stadium(7)

        self.assertEqual(["matches"], result)
        self.assertEqual(7, self.repository.received_stadium_id)

    def test_get_under_twenty_one_players_by_team_requires_reference_date(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.get_under_twenty_one_players_by_team(None)

    def test_get_under_twenty_one_players_by_team_delegates_to_repository(self) -> None:
        reference_date = date(2026, 6, 1)

        result = self.service.get_under_twenty_one_players_by_team(reference_date)

        self.assertEqual(["young_players"], result)
        self.assertEqual(reference_date, self.repository.received_reference_date)

    def test_get_most_expensive_player_by_confederation_delegates_to_repository(self) -> None:
        result = self.service.get_most_expensive_player_by_confederation()

        self.assertEqual(["players"], result)

    def test_get_most_expensive_team_by_host_country_delegates_to_repository(self) -> None:
        result = self.service.get_most_expensive_team_by_host_country()

        self.assertEqual(["teams"], result)


if __name__ == "__main__":
    unittest.main()
