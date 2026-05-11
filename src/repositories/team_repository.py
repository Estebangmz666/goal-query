try:
    from src.database.connection import DatabaseConnectionFactory
    from src.domain.entities.team import Team
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from domain.entities.team import Team
    from repositories.base_repository import BaseRepository


class TeamRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_all(self) -> list[dict]:
        """Fetch all teams."""
        return self.fetch_all(
            """
SELECT
    t.id,
    t.name,
    t.fifa_code,
    t.country_id,
    t.confederation_id,
    t.group_id,
    t.team_weight,
    t.market_value
FROM teams AS t
ORDER BY t.name;
""".strip()
        )

    def find_by_id(self, team_id: int) -> dict | None:
        """Find team by ID."""
        return self.fetch_one(
            """
SELECT
    t.id,
    t.name,
    t.fifa_code,
    t.country_id,
    t.confederation_id,
    t.group_id,
    t.team_weight,
    t.market_value
FROM teams AS t
WHERE t.id = ?;
""".strip(),
            (team_id,),
        )

    def find_by_fifa_code(self, fifa_code: str) -> dict | None:
        """Find team by FIFA code."""
        return self.fetch_one(
            """
SELECT
    t.id,
    t.name,
    t.fifa_code,
    t.country_id,
    t.confederation_id,
    t.group_id,
    t.team_weight,
    t.market_value
FROM teams AS t
WHERE t.fifa_code = ?;
""".strip(),
            (fifa_code,),
        )

    def find_by_country_id(self, country_id: int) -> dict | None:
        """Find team by country ID."""
        return self.fetch_one(
            """
SELECT
    t.id,
    t.name,
    t.fifa_code,
    t.country_id,
    t.confederation_id,
    t.group_id,
    t.team_weight,
    t.market_value
FROM teams AS t
WHERE t.country_id = ?;
""".strip(),
            (country_id,),
        )

    def find_by_group_id(self, group_id: int) -> list[dict]:
        """Find all teams in a group."""
        return self.fetch_all(
            """
SELECT
    t.id,
    t.name,
    t.fifa_code,
    t.country_id,
    t.confederation_id,
    t.group_id,
    t.team_weight,
    t.market_value
FROM teams AS t
WHERE t.group_id = ?
ORDER BY t.name;
""".strip(),
            (group_id,),
        )

    def create(
        self,
        name: str,
        fifa_code: str,
        country_id: int,
        confederation_id: int,
        team_weight: float,
        market_value: float,
        group_id: int | None,
    ) -> int:
        """Create a new team. Returns the team ID."""
        self.execute_non_query(
            """
INSERT INTO teams (name, fifa_code, country_id, confederation_id, team_weight, market_value, group_id)
VALUES (?, ?, ?, ?, ?, ?, ?);
""".strip(),
            (name, fifa_code, country_id, confederation_id, team_weight, market_value, group_id),
        )
        row = self.fetch_one("SELECT SCOPE_IDENTITY() AS id;")
        return int(row["id"]) if row else 0

    def update(
        self,
        team_id: int,
        name: str,
        fifa_code: str,
        team_weight: float,
        market_value: float,
        group_id: int | None,
    ) -> None:
        """Update team information."""
        self.execute_non_query(
            """
UPDATE teams
SET name = ?,
    fifa_code = ?,
    team_weight = ?,
    market_value = ?,
    group_id = ?
WHERE id = ?;
""".strip(),
            (name, fifa_code, team_weight, market_value, group_id, team_id),
        )

    def delete(self, team_id: int) -> None:
        """Delete a team."""
        self.execute_non_query("DELETE FROM teams WHERE id = ?;", (team_id,))

    def name_exists(self, name: str) -> bool:
        """Check if team name already exists."""
        row = self.fetch_one("SELECT 1 FROM teams WHERE name = ?;", (name,))
        return row is not None

    def fifa_code_exists(self, fifa_code: str) -> bool:
        """Check if FIFA code already exists."""
        row = self.fetch_one("SELECT 1 FROM teams WHERE fifa_code = ?;", (fifa_code,))
        return row is not None

    def has_players(self, team_id: int) -> bool:
        """Check if team has players assigned."""
        row = self.fetch_one("SELECT 1 FROM players WHERE team_id = ?;", (team_id,))
        return row is not None

    def has_coach(self, team_id: int) -> bool:
        """Check if team has a coach assigned."""
        row = self.fetch_one("SELECT 1 FROM coaches WHERE team_id = ?;", (team_id,))
        return row is not None

    def has_matches(self, team_id: int) -> bool:
        """Check if team has matches scheduled or played."""
        row = self.fetch_one(
            "SELECT 1 FROM matches WHERE home_team_id = ? OR away_team_id = ?;",
            (team_id, team_id),
        )
        return row is not None
