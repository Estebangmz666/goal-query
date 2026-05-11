try:
    from src.database.connection import DatabaseConnectionFactory
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from repositories.base_repository import BaseRepository


class StadiumRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_all(self) -> list[dict]:
        """Fetch all stadiums."""
        return self.fetch_all(
            """
SELECT
    s.id,
    s.city_id,
    s.name,
    s.capacity
FROM stadiums AS s
ORDER BY s.name;
""".strip()
        )

    def find_by_id(self, stadium_id: int) -> dict | None:
        """Find stadium by ID."""
        return self.fetch_one(
            """
SELECT
    s.id,
    s.city_id,
    s.name,
    s.capacity
FROM stadiums AS s
WHERE s.id = ?;
""".strip(),
            (stadium_id,),
        )

    def find_by_name(self, name: str) -> dict | None:
        """Find stadium by name."""
        return self.fetch_one(
            """
SELECT
    s.id,
    s.city_id,
    s.name,
    s.capacity
FROM stadiums AS s
WHERE s.name = ?;
""".strip(),
            (name,),
        )

    def find_by_city(self, city_id: int) -> list[dict]:
        """Find all stadiums in a city."""
        return self.fetch_all(
            """
SELECT
    s.id,
    s.city_id,
    s.name,
    s.capacity
FROM stadiums AS s
WHERE s.city_id = ?
ORDER BY s.name;
""".strip(),
            (city_id,),
        )

    def create(self, city_id: int, name: str, capacity: int) -> int:
        """Create a new stadium. Returns the stadium ID."""
        self.execute_non_query(
            """
INSERT INTO stadiums (city_id, name, capacity)
VALUES (?, ?, ?);
""".strip(),
            (city_id, name, capacity),
        )
        row = self.fetch_one("SELECT SCOPE_IDENTITY() AS id;")
        return int(row["id"]) if row else 0

    def update(self, stadium_id: int, name: str, capacity: int) -> None:
        """Update stadium information."""
        self.execute_non_query(
            """
UPDATE stadiums
SET name = ?,
    capacity = ?
WHERE id = ?;
""".strip(),
            (name, capacity, stadium_id),
        )

    def delete(self, stadium_id: int) -> None:
        """Delete a stadium."""
        self.execute_non_query("DELETE FROM stadiums WHERE id = ?;", (stadium_id,))

    def name_exists(self, name: str) -> bool:
        """Check if stadium name already exists."""
        row = self.fetch_one("SELECT 1 FROM stadiums WHERE name = ?;", (name,))
        return row is not None

    def city_exists(self, city_id: int) -> bool:
        """Check if city exists."""
        row = self.fetch_one("SELECT 1 FROM cities WHERE id = ?;", (city_id,))
        return row is not None

    def has_matches(self, stadium_id: int) -> bool:
        """Check if stadium has matches scheduled or played."""
        row = self.fetch_one("SELECT 1 FROM matches WHERE stadium_id = ?;", (stadium_id,))
        return row is not None
