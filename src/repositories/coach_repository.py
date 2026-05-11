try:
    from src.database.connection import DatabaseConnectionFactory
    from src.domain.entities.coach import Coach
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from domain.entities.coach import Coach
    from repositories.base_repository import BaseRepository


class CoachRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_all(self) -> list[dict]:
        """Fetch all coaches."""
        return self.fetch_all(
            """
SELECT
    c.id,
    c.team_id,
    c.first_name,
    c.last_name,
    c.nationality_country_id
FROM coaches AS c
ORDER BY c.first_name, c.last_name;
""".strip()
        )

    def find_by_id(self, coach_id: int) -> dict | None:
        """Find coach by ID."""
        return self.fetch_one(
            """
SELECT
    c.id,
    c.team_id,
    c.first_name,
    c.last_name,
    c.nationality_country_id
FROM coaches AS c
WHERE c.id = ?;
""".strip(),
            (coach_id,),
        )

    def find_by_team_id(self, team_id: int) -> dict | None:
        """Find coach by team ID."""
        return self.fetch_one(
            """
SELECT
    c.id,
    c.team_id,
    c.first_name,
    c.last_name,
    c.nationality_country_id
FROM coaches AS c
WHERE c.team_id = ?;
""".strip(),
            (team_id,),
        )

    def find_all_by_nationality(self, country_id: int) -> list[dict]:
        """Find all coaches from a specific country."""
        return self.fetch_all(
            """
SELECT
    c.id,
    c.team_id,
    c.first_name,
    c.last_name,
    c.nationality_country_id
FROM coaches AS c
WHERE c.nationality_country_id = ?
ORDER BY c.first_name, c.last_name;
""".strip(),
            (country_id,),
        )

    def create(
        self,
        team_id: int,
        first_name: str,
        last_name: str,
        nationality_country_id: int,
    ) -> int:
        """Create a new coach. Returns the coach ID."""
        self.execute_non_query(
            """
INSERT INTO coaches (team_id, first_name, last_name, nationality_country_id)
VALUES (?, ?, ?, ?);
""".strip(),
            (team_id, first_name, last_name, nationality_country_id),
        )
        row = self.fetch_one("SELECT SCOPE_IDENTITY() AS id;")
        return int(row["id"]) if row else 0

    def update(
        self,
        coach_id: int,
        first_name: str,
        last_name: str,
        nationality_country_id: int,
    ) -> None:
        """Update coach information."""
        self.execute_non_query(
            """
UPDATE coaches
SET first_name = ?,
    last_name = ?,
    nationality_country_id = ?
WHERE id = ?;
""".strip(),
            (first_name, last_name, nationality_country_id, coach_id),
        )

    def delete(self, coach_id: int) -> None:
        """Delete a coach."""
        self.execute_non_query("DELETE FROM coaches WHERE id = ?;", (coach_id,))

    def coach_exists_for_team(self, team_id: int) -> bool:
        """Check if a team already has a coach."""
        row = self.fetch_one("SELECT 1 FROM coaches WHERE team_id = ?;", (team_id,))
        return row is not None

    def team_exists(self, team_id: int) -> bool:
        """Check if team exists."""
        row = self.fetch_one("SELECT 1 FROM teams WHERE id = ?;", (team_id,))
        return row is not None

    def country_exists(self, country_id: int) -> bool:
        """Check if country exists."""
        row = self.fetch_one("SELECT 1 FROM countries WHERE id = ?;", (country_id,))
        return row is not None
