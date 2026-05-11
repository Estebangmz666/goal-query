from datetime import UTC, date, datetime, timedelta
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from app.environment import load_environment_file
from config.database_config import load_database_config
from database.connection import create_connection_factory
from utils.password_hasher import PasswordHasher


TEAM_CATALOG = [
    ("Argentina", "ARG", "CONMEBOL", 94.0, 890000000),
    ("Brazil", "BRA", "CONMEBOL", 96.0, 980000000),
    ("Uruguay", "URU", "CONMEBOL", 84.0, 420000000),
    ("Colombia", "COL", "CONMEBOL", 83.0, 360000000),
    ("Ecuador", "ECU", "CONMEBOL", 78.0, 260000000),
    ("Chile", "CHI", "CONMEBOL", 74.0, 180000000),
    ("France", "FRA", "UEFA", 95.0, 1100000000),
    ("England", "ENG", "UEFA", 94.0, 1250000000),
    ("Spain", "ESP", "UEFA", 93.0, 960000000),
    ("Germany", "GER", "UEFA", 92.0, 910000000),
    ("Portugal", "POR", "UEFA", 90.0, 820000000),
    ("Italy", "ITA", "UEFA", 89.0, 770000000),
    ("Netherlands", "NED", "UEFA", 88.0, 730000000),
    ("Belgium", "BEL", "UEFA", 86.0, 560000000),
    ("Croatia", "CRO", "UEFA", 83.0, 410000000),
    ("Denmark", "DEN", "UEFA", 81.0, 360000000),
    ("Switzerland", "SUI", "UEFA", 80.0, 340000000),
    ("Serbia", "SRB", "UEFA", 79.0, 320000000),
    ("Mexico", "MEX", "CONCACAF", 80.0, 210000000),
    ("United States", "USA", "CONCACAF", 82.0, 390000000),
    ("Canada", "CAN", "CONCACAF", 76.0, 220000000),
    ("Costa Rica", "CRC", "CONCACAF", 68.0, 52000000),
    ("Panama", "PAN", "CONCACAF", 66.0, 47000000),
    ("Jamaica", "JAM", "CONCACAF", 67.0, 61000000),
    ("Japan", "JPN", "AFC", 81.0, 290000000),
    ("South Korea", "KOR", "AFC", 77.0, 180000000),
    ("Iran", "IRN", "AFC", 74.0, 90000000),
    ("Australia", "AUS", "AFC", 73.0, 82000000),
    ("Saudi Arabia", "KSA", "AFC", 69.0, 68000000),
    ("Qatar", "QAT", "AFC", 66.0, 41000000),
    ("Uzbekistan", "UZB", "AFC", 64.0, 38000000),
    ("United Arab Emirates", "UAE", "AFC", 63.0, 34000000),
    ("Senegal", "SEN", "CAF", 80.0, 260000000),
    ("Morocco", "MAR", "CAF", 84.0, 390000000),
    ("Nigeria", "NGA", "CAF", 78.0, 240000000),
    ("Egypt", "EGY", "CAF", 72.0, 120000000),
    ("Algeria", "ALG", "CAF", 74.0, 150000000),
    ("Tunisia", "TUN", "CAF", 68.0, 72000000),
    ("Cameroon", "CMR", "CAF", 70.0, 110000000),
    ("Ghana", "GHA", "CAF", 71.0, 130000000),
    ("New Zealand", "NZL", "OFC", 62.0, 24000000),
    ("Fiji", "FIJ", "OFC", 50.0, 8000000),
    ("Solomon Islands", "SOL", "OFC", 49.0, 6000000),
    ("Tahiti", "TAH", "OFC", 47.0, 5500000),
    ("Honduras", "HON", "CONCACAF", 65.0, 43000000),
    ("Paraguay", "PAR", "CONMEBOL", 75.0, 170000000),
    ("Poland", "POL", "UEFA", 78.0, 350000000),
    ("Ukraine", "UKR", "UEFA", 77.0, 300000000),
]

HOST_CITY_STADIUMS = [
    ("Mexico", "Mexico City", "Azteca Stadium", 87000),
    ("Mexico", "Guadalajara", "Jalisco Stadium", 55000),
    ("Mexico", "Monterrey", "Monterrey Stadium", 53000),
    ("United States", "Los Angeles", "Pacific Stadium", 70000),
    ("United States", "Dallas", "Lone Star Stadium", 76000),
    ("United States", "Miami", "Atlantic Stadium", 65000),
    ("Canada", "Toronto", "Maple Stadium", 48000),
    ("Canada", "Vancouver", "Pacific North Stadium", 50000),
    ("Canada", "Montreal", "Saint Lawrence Stadium", 46000),
]

GROUP_NAMES = list("ABCDEFGHIJKL")


def main() -> None:
    load_environment_file(str(PROJECT_ROOT / ".env"))
    connection_factory = create_connection_factory(load_database_config())
    password_hasher = PasswordHasher()

    with connection_factory.create_connection() as connection:
        cursor = connection.cursor()
        confederation_ids = _load_confederation_ids(cursor)
        country_ids = _ensure_countries(cursor, confederation_ids)
        _ensure_host_cities_and_stadiums(cursor, country_ids)
        group_ids = _load_group_ids(cursor)
        team_ids = _ensure_teams(cursor, country_ids, confederation_ids, group_ids)
        _ensure_coaches(cursor, country_ids, team_ids)
        _ensure_players(cursor, team_ids)
        stadium_ids = _load_stadium_ids(cursor)
        _ensure_group_stage_matches(cursor, group_ids, team_ids, stadium_ids)
        _ensure_initial_users(cursor, password_hasher)
        connection.commit()


def _load_confederation_ids(cursor) -> dict[str, int]:
    cursor.execute("SELECT id, code FROM confederations;")
    return {row.code: row.id for row in cursor.fetchall()}


def _load_group_ids(cursor) -> dict[str, int]:
    cursor.execute("SELECT id, name FROM groups;")
    return {row.name: row.id for row in cursor.fetchall()}


def _load_stadium_ids(cursor) -> list[int]:
    cursor.execute("SELECT id FROM stadiums ORDER BY id ASC;")
    return [row.id for row in cursor.fetchall()]


def _ensure_countries(cursor, confederation_ids: dict[str, int]) -> dict[str, int]:
    for country_name, fifa_code, confederation_code, _, _ in TEAM_CATALOG:
        cursor.execute(
            """
IF NOT EXISTS (SELECT 1 FROM countries WHERE fifa_code = ?)
BEGIN
    INSERT INTO countries (name, fifa_code, confederation_id)
    VALUES (?, ?, ?)
END;
""".strip(),
            (fifa_code, country_name, fifa_code, confederation_ids[confederation_code]),
        )

    cursor.execute("SELECT id, name FROM countries;")
    return {row.name: row.id for row in cursor.fetchall()}


def _ensure_host_cities_and_stadiums(cursor, country_ids: dict[str, int]) -> None:
    for country_name, city_name, stadium_name, capacity in HOST_CITY_STADIUMS:
        cursor.execute(
            """
IF NOT EXISTS (
    SELECT 1
    FROM cities
    WHERE country_id = ? AND name = ?
)
BEGIN
    INSERT INTO cities (country_id, name)
    VALUES (?, ?)
END;
""".strip(),
            (country_ids[country_name], city_name, country_ids[country_name], city_name),
        )
        cursor.execute(
            """
IF NOT EXISTS (
    SELECT 1
    FROM stadiums AS stadium
    INNER JOIN cities AS city
        ON city.id = stadium.city_id
    WHERE city.country_id = ? AND stadium.name = ?
)
BEGIN
    INSERT INTO stadiums (city_id, name, capacity)
    SELECT city.id, ?, ?
    FROM cities AS city
    WHERE city.country_id = ? AND city.name = ?
END;
""".strip(),
            (
                country_ids[country_name],
                stadium_name,
                stadium_name,
                capacity,
                country_ids[country_name],
                city_name,
            ),
        )


def _ensure_teams(cursor, country_ids, confederation_ids, group_ids) -> dict[str, int]:
    for index, (country_name, fifa_code, confederation_code, team_weight, market_value) in enumerate(TEAM_CATALOG):
        group_name = GROUP_NAMES[index // 4]
        cursor.execute(
            """
IF NOT EXISTS (SELECT 1 FROM teams WHERE fifa_code = ?)
BEGIN
    INSERT INTO teams (
        country_id,
        confederation_id,
        group_id,
        name,
        fifa_code,
        team_weight,
        market_value
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
END;
""".strip(),
            (
                fifa_code,
                country_ids[country_name],
                confederation_ids[confederation_code],
                group_ids[group_name],
                country_name,
                fifa_code,
                team_weight,
                market_value,
            ),
        )

    cursor.execute("SELECT id, name FROM teams;")
    return {row.name: row.id for row in cursor.fetchall()}


def _ensure_coaches(cursor, country_ids, team_ids) -> None:
    for country_name, _, _, _, _ in TEAM_CATALOG:
        coach_first_name = f"{country_name.split()[0]} Coach"
        coach_last_name = "Manager"
        cursor.execute(
            """
IF NOT EXISTS (
    SELECT 1
    FROM coaches
    WHERE team_id = ?
)
BEGIN
    INSERT INTO coaches (
        team_id,
        first_name,
        last_name,
        nationality_country_id
    )
    VALUES (?, ?, ?, ?)
END;
""".strip(),
            (
                team_ids[country_name],
                team_ids[country_name],
                coach_first_name,
                coach_last_name,
                country_ids[country_name],
            ),
        )


def _ensure_players(cursor, team_ids) -> None:
    positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
    for team_index, (country_name, _, _, _, team_market_value) in enumerate(TEAM_CATALOG):
        team_id = team_ids[country_name]
        for shirt_number in range(1, 24):
            first_name = f"{country_name.split()[0]}Player{shirt_number}"
            last_name = "Sample"
            position = positions[(shirt_number - 1) % len(positions)]
            birth_year = 1990 + ((team_index + shirt_number) % 15)
            market_value = round(team_market_value / 23, 2)
            height_cm = 170 + ((shirt_number * 2) % 24)
            weight_kg = 68 + ((shirt_number * 3) % 17)
            cursor.execute(
                """
IF NOT EXISTS (
    SELECT 1
    FROM players
    WHERE team_id = ? AND shirt_number = ?
)
BEGIN
    INSERT INTO players (
        team_id,
        first_name,
        last_name,
        position,
        shirt_number,
        date_of_birth,
        height_cm,
        weight_kg,
        market_value
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
END;
""".strip(),
                (
                    team_id,
                    shirt_number,
                    team_id,
                    first_name,
                    last_name,
                    position,
                    shirt_number,
                    date(birth_year, ((shirt_number - 1) % 12) + 1, ((shirt_number - 1) % 28) + 1),
                    height_cm,
                    weight_kg,
                    market_value,
                ),
            )


def _ensure_group_stage_matches(cursor, group_ids, team_ids, stadium_ids) -> None:
    team_names = [team_name for team_name, _, _, _, _ in TEAM_CATALOG]
    base_datetime = datetime(2026, 6, 11, 15, 0, 0)

    for group_index, group_name in enumerate(GROUP_NAMES):
        group_team_names = team_names[group_index * 4:(group_index + 1) * 4]
        pairings = [
            (group_team_names[0], group_team_names[1]),
            (group_team_names[2], group_team_names[3]),
            (group_team_names[0], group_team_names[2]),
            (group_team_names[1], group_team_names[3]),
            (group_team_names[0], group_team_names[3]),
            (group_team_names[1], group_team_names[2]),
        ]
        for pairing_index, pairing in enumerate(pairings):
            scheduled_at = base_datetime + timedelta(days=(group_index * 2) + pairing_index, hours=pairing_index)
            stadium_id = stadium_ids[(group_index + pairing_index) % len(stadium_ids)]
            cursor.execute(
                """
IF NOT EXISTS (
    SELECT 1
    FROM matches
    WHERE group_id = ?
      AND home_team_id = ?
      AND away_team_id = ?
)
BEGIN
    INSERT INTO matches (
        stadium_id,
        group_id,
        phase,
        home_team_id,
        away_team_id,
        scheduled_at
    )
    VALUES (?, ?, 'GROUP_STAGE', ?, ?, ?)
END;
""".strip(),
                (
                    group_ids[group_name],
                    team_ids[pairing[0]],
                    team_ids[pairing[1]],
                    stadium_id,
                    group_ids[group_name],
                    team_ids[pairing[0]],
                    team_ids[pairing[1]],
                    scheduled_at,
                ),
            )


def _ensure_initial_users(cursor, password_hasher: PasswordHasher) -> None:
    users = [
        ("admin.goalquery", "GoalQuery Administrator", "Admin1234", "ADMINISTRATOR", 1),
        ("traditional.ana", "Ana Traditional", "Trad1234", "TRADITIONAL_USER", 0),
        ("traditional.carlos", "Carlos Traditional", "Trad1234", "TRADITIONAL_USER", 0),
        ("sporadic.lina", "Lina Sporadic", "Spor1234", "SPORADIC_USER", 0),
    ]

    for username, full_name, raw_password, role_code, is_admin in users:
        cursor.execute(
            """
IF NOT EXISTS (SELECT 1 FROM users WHERE username = ?)
BEGIN
    INSERT INTO users (
        role_id,
        username,
        full_name,
        password_hash,
        is_active,
        is_system_administrator,
        created_at
    )
    SELECT
        role.id,
        ?,
        ?,
        ?,
        1,
        ?,
        ?
    FROM roles AS role
    WHERE role.code = ?
END;
""".strip(),
            (
                username,
                username,
                full_name,
                password_hasher.hash_password(raw_password),
                is_admin,
                datetime.now(UTC),
                role_code,
            ),
        )


if __name__ == "__main__":
    main()
