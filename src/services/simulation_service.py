from datetime import UTC, datetime
import math
import random

try:
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.simulation_models import MatchSimulationResultDTO
    from src.repositories.match_repository import MatchRepository
except ModuleNotFoundError:
    from domain.exceptions.validation_error import ValidationError
    from dto.simulation_models import MatchSimulationResultDTO
    from repositories.match_repository import MatchRepository


class SimulationService:
    def __init__(self, match_repository: MatchRepository) -> None:
        self._match_repository = match_repository

    def simulate_match(
        self,
        match_id: int,
        random_seed: int | None = None,
    ) -> MatchSimulationResultDTO:
        if match_id <= 0:
            raise ValidationError("Match id must be greater than zero.")

        match = self._match_repository.find_match_for_simulation(match_id)
        if match is None:
            raise ValidationError("Match was not found.")

        generator = random.Random(random_seed)
        home_expected_goals, away_expected_goals = self._calculate_expected_goals(
            match.home_team_weight,
            match.away_team_weight,
        )
        home_goals = self._generate_poisson_goals(home_expected_goals, generator)
        away_goals = self._generate_poisson_goals(away_expected_goals, generator)
        played_at = datetime.now(UTC)

        self._match_repository.save_match_result(
            match_id=match.id,
            home_goals=home_goals,
            away_goals=away_goals,
            played_at=played_at,
        )
        return MatchSimulationResultDTO(
            match_id=match.id,
            home_team_name=match.home_team_name,
            away_team_name=match.away_team_name,
            home_goals=home_goals,
            away_goals=away_goals,
            played_at=played_at,
        )

    @staticmethod
    def _calculate_expected_goals(
        home_team_weight: float,
        away_team_weight: float,
    ) -> tuple[float, float]:
        total_weight = home_team_weight + away_team_weight
        if total_weight <= 0:
            raise ValidationError("Team weights must be greater than zero.")

        base_goal_rate = 2.6
        home_ratio = home_team_weight / total_weight
        away_ratio = away_team_weight / total_weight
        home_expected_goals = max(0.2, base_goal_rate * home_ratio + 0.15)
        away_expected_goals = max(0.2, base_goal_rate * away_ratio)
        return home_expected_goals, away_expected_goals

    @staticmethod
    def _generate_poisson_goals(expected_goals: float, generator: random.Random) -> int:
        threshold = math.exp(-expected_goals)
        probability_product = 1.0
        generated_goals = 0

        while probability_product > threshold and generated_goals < 8:
            generated_goals += 1
            probability_product *= generator.random()

        return max(0, generated_goals - 1)
