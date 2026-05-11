from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditLog:
    id: int
    user_id: int
    login_at: datetime
    logout_at: datetime | None
    session_status: str | None
    machine_name: str | None
    application_name: str | None
