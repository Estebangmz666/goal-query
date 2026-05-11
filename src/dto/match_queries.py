from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MatchesByStadiumDTO:
    match_id: int
    stadium_id: int
    stadium_name: str
    city_name: str
    host_country_name: str
    phase: str
    group_name: str | None
    home_team_name: str
    away_team_name: str
    scheduled_at: datetime
