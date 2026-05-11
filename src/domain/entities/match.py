from dataclasses import dataclass
from datetime import datetime

try:
    from src.domain.enums.match_phase import MatchPhase
except ModuleNotFoundError:
    from domain.enums.match_phase import MatchPhase


@dataclass(frozen=True)
class Match:
    id: int
    phase: MatchPhase
    home_team_id: int
    away_team_id: int
    home_team_name: str
    away_team_name: str
    home_team_weight: float
    away_team_weight: float
    scheduled_at: datetime
