from dataclasses import dataclass
from datetime import datetime

try:
    from src.domain.enums.user_role import UserRole
except ModuleNotFoundError:
    from domain.enums.user_role import UserRole


@dataclass(frozen=True)
class AuthenticatedSessionDTO:
    audit_log_id: int
    user_id: int
    username: str
    full_name: str
    role: UserRole
    login_at: datetime


@dataclass(frozen=True)
class CreatedUserDTO:
    user_id: int
    username: str
    full_name: str
    role: UserRole
    is_active: bool
