from datetime import datetime

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.domain.entities.match import Match
    from src.domain.enums.match_phase import MatchPhase
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from domain.entities.match import Match
    from domain.enums.match_phase import MatchPhase
    from repositories.base_repository import BaseRepository


class MatchRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_all(self) -> list[dict]:
        """Fetch all matches."""
        return self.fetch_all(
            """
SELECT
    m.id,
    m.stadium_id,
    m.group_id,
    m.phase,
    m.home_team_id,
    m.away_team_id,
    m.scheduled_at
FROM matches AS m
ORDER BY m.scheduled_at;
""".strip()
        )

    def find_by_id(self, match_id: int) -> dict | None:
        """Find match by ID."""
        return self.fetch_one(
            """
SELECT
    m.id,
    m.stadium_id,
    m.group_id,
    m.phase,
    m.home_team_id,
    m.away_team_id,
    m.scheduled_at
FROM matches AS m
WHERE m.id = ?;
""".strip(),
            (match_id,),
        )

    def find_by_stadium(self, stadium_id: int) -> list[dict]:
        """Find all matches in a stadium."""
        return self.fetch_all(
            """
SELECT
    m.id,
    m.stadium_id,
    m.group_id,
    m.phase,
    m.home_team_id,
    m.away_team_id,
    m.scheduled_at
FROM matches AS m
WHERE m.stadium_id = ?
ORDER BY m.scheduled_at;
""".strip(),
            (stadium_id,),
        )

    def find_by_group(self, group_id: int) -> list[dict]:
        """Find all matches in a group."""
        return self.fetch_all(
            """
SELECT
    m.id,
    m.stadium_id,
    m.group_id,
    m.phase,
    m.home_team_id,
    m.away_team_id,
    m.scheduled_at
FROM matches AS m
WHERE m.group_id = ? AND m.phase = ?
ORDER BY m.scheduled_at;
""".strip(),
            (group_id, MatchPhase.GROUP_STAGE.value),
        )

    def find_by_phase(self, phase: str) -> list[dict]:
        """Find all matches in a specific phase."""
        return self.fetch_all(
            """
SELECT
    m.id,
    m.stadium_id,
    m.group_id,
    m.phase,
    m.home_team_id,
    m.away_team_id,
    m.scheduled_at
FROM matches AS m
WHERE m.phase = ?
ORDER BY m.scheduled_at;
""".strip(),
            (phase,),
        )

    def find_by_team(self, team_id: int) -> list[dict]:
        """Find all matches for a team."""
        return self.fetch_all(
            """
SELECT
    m.id,
    m.stadium_id,
    m.group_id,
    m.phase,
    m.home_team_id,
    m.away_team_id,
    m.scheduled_at
FROM matches AS m
WHERE m.home_team_id = ? OR m.away_team_id = ?
ORDER BY m.scheduled_at;
""".strip(),
            (team_id, team_id),
        )

    def create(
        self,
        stadium_id: int,
        group_id: int | None,
        phase: str,
        home_team_id: int,
        away_team_id: int,
        scheduled_at: datetime,
    ) -> int:
        """Create a new match. Returns the match ID."""
        self.execute_non_query(
            """
INSERT INTO matches (stadium_id, group_id, phase, home_team_id, away_team_id, scheduled_at)
VALUES (?, ?, ?, ?, ?, ?);
""".strip(),
            (stadium_id, group_id, phase, home_team_id, away_team_id, scheduled_at),
        )
        row = self.fetch_one("SELECT SCOPE_IDENTITY() AS id;")
        return int(row["id"]) if row else 0

    def update(
        self,
        match_id: int,
        stadium_id: int,
        scheduled_at: datetime,
    ) -> None:
        """Update match information (before playing)."""
        self.execute_non_query(
            """
UPDATE matches
SET stadium_id = ?,
    scheduled_at = ?
WHERE id = ?;
""".strip(),
            (stadium_id, scheduled_at, match_id),
        )

    def delete(self, match_id: int) -> None:
        """Delete a match (only if not yet played)."""
        self.execute_non_query("DELETE FROM matches WHERE id = ?;", (match_id,))

    def stadium_exists(self, stadium_id: int) -> bool:
        """Check if stadium exists."""
        row = self.fetch_one("SELECT 1 FROM stadiums WHERE id = ?;", (stadium_id,))
        return row is not None

    def team_exists(self, team_id: int) -> bool:
        """Check if team exists."""
        row = self.fetch_one("SELECT 1 FROM teams WHERE id = ?;", (team_id,))
        return row is not None

    def group_exists(self, group_id: int) -> bool:
        """Check if group exists."""
        row = self.fetch_one("SELECT 1 FROM groups WHERE id = ?;", (group_id,))
        return row is not None

    def has_result(self, match_id: int) -> bool:
        """Check if match has been played."""
        row = self.fetch_one("SELECT 1 FROM match_results WHERE match_id = ?;", (match_id,))
        return row is not None

    def find_match_for_simulation(self, match_id: int) -> Match | None:
        row = self.fetch_one(
            """
SELECT
    match.id,
    match.phase,
    match.home_team_id,
    match.away_team_id,
    home_team.name AS home_team_name,
    away_team.name AS away_team_name,
    CAST(home_team.team_weight AS FLOAT) AS home_team_weight,
    CAST(away_team.team_weight AS FLOAT) AS away_team_weight,
    match.scheduled_at
FROM matches AS match
INNER JOIN teams AS home_team
    ON home_team.id = match.home_team_id
INNER JOIN teams AS away_team
    ON away_team.id = match.away_team_id
WHERE match.id = ?;
""".strip(),
            (match_id,),
        )
        if row is None:
            return None

        return Match(
            id=row["id"],
            phase=MatchPhase(row["phase"]),
            home_team_id=row["home_team_id"],
            away_team_id=row["away_team_id"],
            home_team_name=row["home_team_name"],
            away_team_name=row["away_team_name"],
            home_team_weight=float(row["home_team_weight"]),
            away_team_weight=float(row["away_team_weight"]),
            scheduled_at=row["scheduled_at"],
        )

    def save_match_result(
        self,
        match_id: int,
        home_goals: int,
        away_goals: int,
        played_at: datetime,
    ) -> None:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM match_results WHERE match_id = ?;",
                (match_id,),
            )
            existing_row = cursor.fetchone()

            if existing_row is None:
                cursor.execute(
                    """
INSERT INTO match_results (
    match_id,
    home_goals,
    away_goals,
    played_at
)
VALUES (?, ?, ?, ?);
""".strip(),
                    (match_id, home_goals, away_goals, played_at),
                )
            else:
                cursor.execute(
                    """
UPDATE match_results
SET home_goals = ?,
    away_goals = ?,
    played_at = ?
WHERE match_id = ?;
""".strip(),
                    (home_goals, away_goals, played_at, match_id),
                )

            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
