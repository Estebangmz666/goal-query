from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class AuditLogReportItemDTO:
    username: str
    full_name: str
    login_at: datetime
    logout_at: datetime | None
    session_status: str | None


@dataclass(frozen=True)
class FilteredPlayerReportItemDTO:
    player_id: int
    player_full_name: str
    team_name: str
    weight_kg: float
    height_cm: float
    market_value: Decimal


@dataclass(frozen=True)
class TeamValueByConfederationReportItemDTO:
    confederation_name: str
    team_name: str
    total_player_market_value: Decimal


@dataclass(frozen=True)
class CountriesByHostCountryReportItemDTO:
    host_country_name: str
    country_name: str
