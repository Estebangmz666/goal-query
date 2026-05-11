from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    id: int
    name: str
    fifa_code: str
    country_id: int
    confederation_id: int
    team_weight: float
    market_value: float
    group_id: int | None
