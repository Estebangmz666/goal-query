from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTeamDTO:
    name: str
    fifa_code: str
    country_id: int
    confederation_id: int
    team_weight: float
    market_value: float
    group_id: int | None = None


@dataclass(frozen=True)
class TeamResponseDTO:
    id: int
    name: str
    fifa_code: str
    country_id: int
    confederation_id: int
    team_weight: float
    market_value: float
    group_id: int | None = None


@dataclass(frozen=True)
class UpdateTeamDTO:
    name: str
    fifa_code: str
    team_weight: float
    market_value: float
    group_id: int | None = None
