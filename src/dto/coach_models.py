from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCoachDTO:
    team_id: int
    first_name: str
    last_name: str
    nationality_country_id: int


@dataclass(frozen=True)
class CoachResponseDTO:
    id: int
    team_id: int
    first_name: str
    last_name: str
    nationality_country_id: int


@dataclass(frozen=True)
class UpdateCoachDTO:
    first_name: str
    last_name: str
    nationality_country_id: int
