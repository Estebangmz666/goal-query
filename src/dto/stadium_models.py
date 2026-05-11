from dataclasses import dataclass


@dataclass(frozen=True)
class CreateStadiumDTO:
    city_id: int
    name: str
    capacity: int


@dataclass(frozen=True)
class StadiumResponseDTO:
    id: int
    city_id: int
    name: str
    capacity: int


@dataclass(frozen=True)
class UpdateStadiumDTO:
    name: str
    capacity: int
