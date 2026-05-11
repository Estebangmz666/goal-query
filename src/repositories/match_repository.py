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
