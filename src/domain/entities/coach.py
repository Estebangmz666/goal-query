from dataclasses import dataclass


@dataclass(frozen=True)
class Coach:
    id: int
    team_id: int
    first_name: str
    last_name: str
    nationality_country_id: int
