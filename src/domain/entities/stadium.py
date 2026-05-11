from dataclasses import dataclass


@dataclass(frozen=True)
class Stadium:
    id: int
    city_id: int
    name: str
    capacity: int
