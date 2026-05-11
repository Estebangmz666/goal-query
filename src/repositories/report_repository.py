from decimal import Decimal

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.dto.report_models import (
        AuditLogReportItemDTO,
        CountriesByHostCountryReportItemDTO,
        FilteredPlayerReportItemDTO,
        TeamValueByConfederationReportItemDTO,
    )
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from dto.report_models import (
        AuditLogReportItemDTO,
        CountriesByHostCountryReportItemDTO,
        FilteredPlayerReportItemDTO,
        TeamValueByConfederationReportItemDTO,
    )
    from repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def get_user_sessions_by_datetime_range(
        self,
        start_datetime,
        end_datetime,
    ) -> list[AuditLogReportItemDTO]:
        rows = self.fetch_all(
            """
SELECT
    [user].username,
    [user].full_name,
    audit_log.login_at,
    audit_log.logout_at,
    audit_log.session_status
FROM audit_logs AS audit_log
INNER JOIN users AS [user]
    ON [user].id = audit_log.user_id
WHERE audit_log.login_at >= ?
  AND audit_log.login_at <= ?
ORDER BY audit_log.login_at ASC;
""".strip(),
            (start_datetime, end_datetime),
        )
        return [
            AuditLogReportItemDTO(
                username=row["username"],
                full_name=row["full_name"],
                login_at=row["login_at"],
                logout_at=row["logout_at"],
                session_status=row["session_status"],
            )
            for row in rows
        ]

    def get_players_by_filters(
        self,
        minimum_weight_kg: float,
        maximum_weight_kg: float,
        minimum_height_cm: float,
        maximum_height_cm: float,
        team_name: str,
    ) -> list[FilteredPlayerReportItemDTO]:
        rows = self.fetch_all(
            """
SELECT
    player.id AS player_id,
    CONCAT(player.first_name, ' ', player.last_name) AS player_full_name,
    team.name AS team_name,
    player.weight_kg,
    player.height_cm,
    player.market_value
FROM players AS player
INNER JOIN teams AS team
    ON team.id = player.team_id
WHERE player.weight_kg BETWEEN ? AND ?
  AND player.height_cm BETWEEN ? AND ?
  AND team.name = ?
ORDER BY team.name, player.last_name, player.first_name;
""".strip(),
            (
                minimum_weight_kg,
                maximum_weight_kg,
                minimum_height_cm,
                maximum_height_cm,
                team_name,
            ),
        )
        return [
            FilteredPlayerReportItemDTO(
                player_id=row["player_id"],
                player_full_name=row["player_full_name"],
                team_name=row["team_name"],
                weight_kg=float(row["weight_kg"]),
                height_cm=float(row["height_cm"]),
                market_value=Decimal(row["market_value"]),
            )
            for row in rows
        ]

    def get_total_player_value_by_confederation(
        self,
        confederation_code: str,
    ) -> list[TeamValueByConfederationReportItemDTO]:
        rows = self.fetch_all(
            """
SELECT
    confederation.name AS confederation_name,
    team.name AS team_name,
    SUM(player.market_value) AS total_player_market_value
FROM confederations AS confederation
INNER JOIN teams AS team
    ON team.confederation_id = confederation.id
INNER JOIN players AS player
    ON player.team_id = team.id
WHERE confederation.code = ?
GROUP BY confederation.name, team.name
ORDER BY total_player_market_value DESC, team.name ASC;
""".strip(),
            (confederation_code,),
        )
        return [
            TeamValueByConfederationReportItemDTO(
                confederation_name=row["confederation_name"],
                team_name=row["team_name"],
                total_player_market_value=Decimal(row["total_player_market_value"]),
            )
            for row in rows
        ]

    def get_countries_playing_by_host_country(self) -> list[CountriesByHostCountryReportItemDTO]:
        rows = self.fetch_all(
            """
WITH host_country_countries AS (
    SELECT
        host_country.name AS host_country_name,
        home_country.name AS country_name
    FROM matches AS match
    INNER JOIN stadiums AS stadium
        ON stadium.id = match.stadium_id
    INNER JOIN cities AS city
        ON city.id = stadium.city_id
    INNER JOIN countries AS host_country
        ON host_country.id = city.country_id
    INNER JOIN teams AS home_team
        ON home_team.id = match.home_team_id
    INNER JOIN countries AS home_country
        ON home_country.id = home_team.country_id
    UNION
    SELECT
        host_country.name AS host_country_name,
        away_country.name AS country_name
    FROM matches AS match
    INNER JOIN stadiums AS stadium
        ON stadium.id = match.stadium_id
    INNER JOIN cities AS city
        ON city.id = stadium.city_id
    INNER JOIN countries AS host_country
        ON host_country.id = city.country_id
    INNER JOIN teams AS away_team
        ON away_team.id = match.away_team_id
    INNER JOIN countries AS away_country
        ON away_country.id = away_team.country_id
)
SELECT
    host_country_name,
    country_name
FROM host_country_countries
ORDER BY host_country_name, country_name;
""".strip()
        )
        return [
            CountriesByHostCountryReportItemDTO(
                host_country_name=row["host_country_name"],
                country_name=row["country_name"],
            )
            for row in rows
        ]
