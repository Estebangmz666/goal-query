from dataclasses import dataclass


@dataclass(frozen=True)
class City:
    id: int
    country_id: int
    name: str
