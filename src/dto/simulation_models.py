from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MatchSimulationResultDTO:
    match_id: int
    home_team_name: str
    away_team_name: str
    home_goals: int
    away_goals: int
    played_at: datetime
