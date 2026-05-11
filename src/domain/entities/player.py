from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Player:
    id: int
    team_id: int
    first_name: str
    last_name: str
    position: str
    shirt_number: int
    date_of_birth: date
    height_cm: float
    weight_kg: float
    market_value: float
