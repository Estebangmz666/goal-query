from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCityDTO:
    country_id: int
    name: str


@dataclass(frozen=True)
class CityResponseDTO:
    id: int
    country_id: int
    name: str


@dataclass(frozen=True)
class UpdateCityDTO:
    name: str
