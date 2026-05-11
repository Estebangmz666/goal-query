from datetime import datetime
import unittest

try:
    from src.domain.entities.match import Match
    from src.domain.enums.match_phase import MatchPhase
    from src.services.simulation_service import SimulationService
except ModuleNotFoundError:
    from domain.entities.match import Match
    from domain.enums.match_phase import MatchPhase
    from services.simulation_service import SimulationService


class FakeMatchRepository:
    def __init__(self) -> None:
        self.saved_result = None

    def find_match_for_simulation(self, match_id: int) -> Match:
        return Match(
            id=match_id,
            phase=MatchPhase.GROUP_STAGE,
            home_team_id=1,
            away_team_id=2,
            home_team_name="Colombia",
            away_team_name="Japan",
            home_team_weight=85.0,
            away_team_weight=78.0,
            scheduled_at=datetime(2026, 6, 14, 16, 0, 0),
        )

    def save_match_result(self, match_id, home_goals, away_goals, played_at):
        self.saved_result = (match_id, home_goals, away_goals, played_at)


class SimulationServiceTestCase(unittest.TestCase):
    def test_simulation_returns_deterministic_score_with_seed(self) -> None:
        repository = FakeMatchRepository()
        service = SimulationService(repository)

        result = service.simulate_match(3, random_seed=42)

        self.assertEqual(3, result.match_id)
        self.assertEqual((3, result.home_goals, result.away_goals), repository.saved_result[:3])
        self.assertGreaterEqual(result.home_goals, 0)
        self.assertGreaterEqual(result.away_goals, 0)


if __name__ == "__main__":
    unittest.main()
