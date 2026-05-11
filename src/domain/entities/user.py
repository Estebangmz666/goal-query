from dataclasses import dataclass
from datetime import datetime

try:
    from src.domain.enums.user_role import UserRole
except ModuleNotFoundError:
    from domain.enums.user_role import UserRole


@dataclass(frozen=True)
class User:
    id: int
    role: UserRole
    username: str
    full_name: str
    password_hash: str
    is_active: bool
    is_system_administrator: bool
    created_at: datetime
