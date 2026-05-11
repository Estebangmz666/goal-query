from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateMatchDTO:
    stadium_id: int
    group_id: int | None
    phase: str
    home_team_id: int
    away_team_id: int
    scheduled_at: datetime


@dataclass(frozen=True)
class MatchResponseDTO:
    id: int
    stadium_id: int
    group_id: int | None
    phase: str
    home_team_id: int
    away_team_id: int
    scheduled_at: datetime


@dataclass(frozen=True)
class UpdateMatchDTO:
    stadium_id: int
    scheduled_at: datetime


@dataclass(frozen=True)
class MatchResultDTO:
    match_id: int
    home_goals: int
    away_goals: int
    played_at: datetime
