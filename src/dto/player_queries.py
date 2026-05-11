from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MostExpensivePlayerByConfederationDTO:
    confederation_id: int
    confederation_name: str
    player_id: int
    player_first_name: str
    player_last_name: str
    player_position: str
    player_date_of_birth: date
    player_market_value: float
    team_id: int
    team_name: str
    country_name: str


@dataclass(frozen=True)
class UnderTwentyOnePlayersByTeamDTO:
    team_id: int
    team_name: str
    under_twenty_one_player_count: int
