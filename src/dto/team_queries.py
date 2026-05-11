from dataclasses import dataclass


@dataclass(frozen=True)
class MostExpensiveTeamByHostCountryDTO:
    host_country_id: int
    host_country_name: str
    team_id: int
    team_name: str
    team_market_value: float
    confederation_name: str
