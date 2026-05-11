try:
    from src.database.connection import DatabaseConnectionFactory
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from repositories.base_repository import BaseRepository


class CityRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def find_all(self) -> list[dict]:
        """Fetch all cities."""
        return self.fetch_all(
            """
SELECT
    c.id,
    c.country_id,
    c.name
FROM cities AS c
ORDER BY c.name;
""".strip()
        )

    def find_by_id(self, city_id: int) -> dict | None:
        """Find city by ID."""
        return self.fetch_one(
            """
SELECT
    c.id,
    c.country_id,
    c.name
FROM cities AS c
WHERE c.id = ?;
""".strip(),
            (city_id,),
        )

    def find_by_name(self, name: str) -> dict | None:
        """Find city by name."""
        return self.fetch_one(
            """
SELECT
    c.id,
    c.country_id,
    c.name
FROM cities AS c
WHERE c.name = ?;
""".strip(),
            (name,),
        )

    def find_by_country(self, country_id: int) -> list[dict]:
        """Find all cities in a country."""
        return self.fetch_all(
            """
SELECT
    c.id,
    c.country_id,
    c.name
FROM cities AS c
WHERE c.country_id = ?
ORDER BY c.name;
""".strip(),
            (country_id,),
        )

    def find_in_host_countries(self) -> list[dict]:
        """Find all cities in host countries."""
        return self.fetch_all(
            """
SELECT
    c.id,
    c.country_id,
    c.name
FROM cities AS c
INNER JOIN host_countries AS hc ON c.country_id = hc.country_id
ORDER BY c.name;
""".strip()
        )

    def create(self, country_id: int, name: str) -> int:
        """Create a new city. Returns the city ID."""
        self.execute_non_query(
            """
INSERT INTO cities (country_id, name)
VALUES (?, ?);
""".strip(),
            (country_id, name),
        )
        row = self.fetch_one("SELECT SCOPE_IDENTITY() AS id;")
        return int(row["id"]) if row else 0

    def update(self, city_id: int, name: str) -> None:
        """Update city name."""
        self.execute_non_query(
            "UPDATE cities SET name = ? WHERE id = ?;",
            (name, city_id),
        )

    def delete(self, city_id: int) -> None:
        """Delete a city."""
        self.execute_non_query("DELETE FROM cities WHERE id = ?;", (city_id,))

    def name_exists(self, name: str) -> bool:
        """Check if city name already exists."""
        row = self.fetch_one("SELECT 1 FROM cities WHERE name = ?;", (name,))
        return row is not None

    def country_exists(self, country_id: int) -> bool:
        """Check if country exists."""
        row = self.fetch_one("SELECT 1 FROM countries WHERE id = ?;", (country_id,))
        return row is not None

    def has_stadiums(self, city_id: int) -> bool:
        """Check if city has stadiums."""
        row = self.fetch_one("SELECT 1 FROM stadiums WHERE city_id = ?;", (city_id,))
        return row is not None
