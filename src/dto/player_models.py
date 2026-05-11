from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreatePlayerDTO:
    team_id: int
    first_name: str
    last_name: str
    position: str
    shirt_number: int
    date_of_birth: date
    height_cm: float
    weight_kg: float
    market_value: float


@dataclass(frozen=True)
class PlayerResponseDTO:
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


@dataclass(frozen=True)
class UpdatePlayerDTO:
    position: str
    shirt_number: int
    height_cm: float
    weight_kg: float
    market_value: float
