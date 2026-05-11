from datetime import date

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from repositories.base_repository import BaseRepository


class PlayerRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_all(self) -> list[dict]:
        """Fetch all players."""
        return self.fetch_all(
            """
SELECT
    p.id,
    p.team_id,
    p.first_name,
    p.last_name,
    p.position,
    p.shirt_number,
    p.date_of_birth,
    p.height_cm,
    p.weight_kg,
    p.market_value
FROM players AS p
ORDER BY p.first_name, p.last_name;
""".strip()
        )

    def find_by_id(self, player_id: int) -> dict | None:
        """Find player by ID."""
        return self.fetch_one(
            """
SELECT
    p.id,
    p.team_id,
    p.first_name,
    p.last_name,
    p.position,
    p.shirt_number,
    p.date_of_birth,
    p.height_cm,
    p.weight_kg,
    p.market_value
FROM players AS p
WHERE p.id = ?;
""".strip(),
            (player_id,),
        )

    def find_by_team(self, team_id: int) -> list[dict]:
        """Find all players in a team."""
        return self.fetch_all(
            """
SELECT
    p.id,
    p.team_id,
    p.first_name,
    p.last_name,
    p.position,
    p.shirt_number,
    p.date_of_birth,
    p.height_cm,
    p.weight_kg,
    p.market_value
FROM players AS p
WHERE p.team_id = ?
ORDER BY p.first_name, p.last_name;
""".strip(),
            (team_id,),
        )

    def count_by_team(self, team_id: int) -> int:
        """Count players in a team."""
        row = self.fetch_one("SELECT COUNT(*) AS count FROM players WHERE team_id = ?;", (team_id,))
        return row["count"] if row else 0

    def find_by_position(self, position: str) -> list[dict]:
        """Find all players with a specific position."""
        return self.fetch_all(
            """
SELECT
    p.id,
    p.team_id,
    p.first_name,
    p.last_name,
    p.position,
    p.shirt_number,
    p.date_of_birth,
    p.height_cm,
    p.weight_kg,
    p.market_value
FROM players AS p
WHERE p.position = ?
ORDER BY p.first_name, p.last_name;
""".strip(),
            (position,),
        )

    def find_under_age(self, max_age: int) -> list[dict]:
        """Find all players under a specific age."""
        return self.fetch_all(
            f"""
SELECT
    p.id,
    p.team_id,
    p.first_name,
    p.last_name,
    p.position,
    p.shirt_number,
    p.date_of_birth,
    p.height_cm,
    p.weight_kg,
    p.market_value
FROM players AS p
WHERE DATEDIFF(YEAR, p.date_of_birth, GETDATE()) < ?
ORDER BY p.first_name, p.last_name;
""".strip(),
            (max_age,),
        )

    def create(
        self,
        team_id: int,
        first_name: str,
        last_name: str,
        position: str,
        shirt_number: int,
        date_of_birth: date,
        height_cm: float,
        weight_kg: float,
        market_value: float,
    ) -> int:
        """Create a new player. Returns the player ID."""
        self.execute_non_query(
            """
INSERT INTO players (team_id, first_name, last_name, position, shirt_number, date_of_birth, height_cm, weight_kg, market_value)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
""".strip(),
            (
                team_id,
                first_name,
                last_name,
                position,
                shirt_number,
                date_of_birth,
                height_cm,
                weight_kg,
                market_value,
            ),
        )
        row = self.fetch_one("SELECT SCOPE_IDENTITY() AS id;")
        return int(row["id"]) if row else 0

    def update(
        self,
        player_id: int,
        position: str,
        shirt_number: int,
        height_cm: float,
        weight_kg: float,
        market_value: float,
    ) -> None:
        """Update player information."""
        self.execute_non_query(
            """
UPDATE players
SET position = ?,
    shirt_number = ?,
    height_cm = ?,
    weight_kg = ?,
    market_value = ?
WHERE id = ?;
""".strip(),
            (position, shirt_number, height_cm, weight_kg, market_value, player_id),
        )

    def delete(self, player_id: int) -> None:
        """Delete a player."""
        self.execute_non_query("DELETE FROM players WHERE id = ?;", (player_id,))

    def shirt_number_exists_in_team(self, team_id: int, shirt_number: int) -> bool:
        """Check if shirt number is already used in team."""
        row = self.fetch_one(
            "SELECT 1 FROM players WHERE team_id = ? AND shirt_number = ?;",
            (team_id, shirt_number),
        )
        return row is not None

    def team_exists(self, team_id: int) -> bool:
        """Check if team exists."""
        row = self.fetch_one("SELECT 1 FROM teams WHERE id = ?;", (team_id,))
        return row is not None
