from datetime import date

try:
    from src.database.connection import DatabaseConnectionFactory
    from src.dto.match_queries import MatchesByStadiumDTO
    from src.dto.player_queries import (
        MostExpensivePlayerByConfederationDTO,
        UnderTwentyOnePlayersByTeamDTO,
    )
    from src.dto.team_queries import MostExpensiveTeamByHostCountryDTO
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from dto.match_queries import MatchesByStadiumDTO
    from dto.player_queries import (
        MostExpensivePlayerByConfederationDTO,
        UnderTwentyOnePlayersByTeamDTO,
    )
    from dto.team_queries import MostExpensiveTeamByHostCountryDTO
    from repositories.base_repository import BaseRepository


class QueryRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def get_most_expensive_player_by_confederation(
        self,
    ) -> list[MostExpensivePlayerByConfederationDTO]:
        rows = self.fetch_all(self._build_most_expensive_player_by_confederation_query())
        return [
            MostExpensivePlayerByConfederationDTO(
                confederation_id=row["confederation_id"],
                confederation_name=row["confederation_name"],
                player_id=row["player_id"],
                player_first_name=row["player_first_name"],
                player_last_name=row["player_last_name"],
                player_position=row["player_position"],
                player_date_of_birth=row["player_date_of_birth"],
                player_market_value=float(row["player_market_value"]),
                team_id=row["team_id"],
                team_name=row["team_name"],
                country_name=row["country_name"],
            )
            for row in rows
        ]

    def get_matches_by_stadium(self, stadium_id: int) -> list[MatchesByStadiumDTO]:
        rows = self.fetch_all(
            self._build_matches_by_stadium_query(),
            (stadium_id,),
        )
        return [
            MatchesByStadiumDTO(
                match_id=row["match_id"],
                stadium_id=row["stadium_id"],
                stadium_name=row["stadium_name"],
                city_name=row["city_name"],
                host_country_name=row["host_country_name"],
                phase=row["phase"],
                group_name=row["group_name"],
                home_team_name=row["home_team_name"],
                away_team_name=row["away_team_name"],
                scheduled_at=row["scheduled_at"],
            )
            for row in rows
        ]

    def get_most_expensive_team_by_host_country(
        self,
    ) -> list[MostExpensiveTeamByHostCountryDTO]:
        rows = self.fetch_all(self._build_most_expensive_team_by_host_country_query())
        return [
            MostExpensiveTeamByHostCountryDTO(
                host_country_id=row["host_country_id"],
                host_country_name=row["host_country_name"],
                team_id=row["team_id"],
                team_name=row["team_name"],
                team_market_value=float(row["team_market_value"]),
                confederation_name=row["confederation_name"],
            )
            for row in rows
        ]

    def get_under_twenty_one_players_by_team(
        self,
        reference_date: date,
    ) -> list[UnderTwentyOnePlayersByTeamDTO]:
        rows = self.fetch_all(
            self._build_under_twenty_one_players_by_team_query(),
            (reference_date, reference_date, reference_date),
        )
        return [
            UnderTwentyOnePlayersByTeamDTO(
                team_id=row["team_id"],
                team_name=row["team_name"],
                under_twenty_one_player_count=row["under_twenty_one_player_count"],
            )
            for row in rows
        ]

    @staticmethod
    def _build_most_expensive_player_by_confederation_query() -> str:
        return """
WITH ranked_players AS (
    SELECT
        confederation.id AS confederation_id,
        confederation.name AS confederation_name,
        player.id AS player_id,
        player.first_name AS player_first_name,
        player.last_name AS player_last_name,
        player.position AS player_position,
        player.date_of_birth AS player_date_of_birth,
        player.market_value AS player_market_value,
        team.id AS team_id,
        team.name AS team_name,
        country.name AS country_name,
        ROW_NUMBER() OVER (
            PARTITION BY confederation.id
            ORDER BY player.market_value DESC, player.id ASC
        ) AS player_rank
    FROM confederations AS confederation
    INNER JOIN teams AS team
        ON team.confederation_id = confederation.id
    INNER JOIN players AS player
        ON player.team_id = team.id
    INNER JOIN countries AS country
        ON country.id = team.country_id
)
SELECT
    ranked_players.confederation_id,
    ranked_players.confederation_name,
    ranked_players.player_id,
    ranked_players.player_first_name,
    ranked_players.player_last_name,
    ranked_players.player_position,
    ranked_players.player_date_of_birth,
    ranked_players.player_market_value,
    ranked_players.team_id,
    ranked_players.team_name,
    ranked_players.country_name
FROM ranked_players
WHERE ranked_players.player_rank = 1
ORDER BY ranked_players.confederation_name;
""".strip()

    @staticmethod
    def _build_matches_by_stadium_query() -> str:
        return """
SELECT
    match.id AS match_id,
    stadium.id AS stadium_id,
    stadium.name AS stadium_name,
    city.name AS city_name,
    host_country.name AS host_country_name,
    match.phase AS phase,
    [group].name AS group_name,
    home_team.name AS home_team_name,
    away_team.name AS away_team_name,
    match.scheduled_at AS scheduled_at
FROM matches AS match
INNER JOIN stadiums AS stadium
    ON stadium.id = match.stadium_id
INNER JOIN cities AS city
    ON city.id = stadium.city_id
INNER JOIN countries AS host_country
    ON host_country.id = city.country_id
LEFT JOIN groups AS [group]
    ON [group].id = match.group_id
INNER JOIN teams AS home_team
    ON home_team.id = match.home_team_id
INNER JOIN teams AS away_team
    ON away_team.id = match.away_team_id
WHERE stadium.id = ?
ORDER BY match.scheduled_at ASC, match.id ASC;
""".strip()

    @staticmethod
    def _build_most_expensive_team_by_host_country_query() -> str:
        return """
WITH host_country_participants AS (
    SELECT DISTINCT
        host_country.id AS host_country_id,
        host_country.name AS host_country_name,
        team.id AS team_id,
        team.name AS team_name,
        team.market_value AS team_market_value,
        confederation.name AS confederation_name
    FROM matches AS match
    INNER JOIN stadiums AS stadium
        ON stadium.id = match.stadium_id
    INNER JOIN cities AS city
        ON city.id = stadium.city_id
    INNER JOIN countries AS host_country
        ON host_country.id = city.country_id
    INNER JOIN host_countries AS host_reference
        ON host_reference.country_id = host_country.id
    INNER JOIN teams AS home_team
        ON home_team.id = match.home_team_id
    INNER JOIN teams AS away_team
        ON away_team.id = match.away_team_id
    CROSS APPLY (
        VALUES
            (home_team.id, home_team.name, home_team.market_value, home_team.confederation_id),
            (away_team.id, away_team.name, away_team.market_value, away_team.confederation_id)
    ) AS team(id, name, market_value, confederation_id)
    INNER JOIN confederations AS confederation
        ON confederation.id = team.confederation_id
    WHERE match.phase = 'GROUP_STAGE'
),
ranked_teams AS (
    SELECT
        host_country_participants.host_country_id,
        host_country_participants.host_country_name,
        host_country_participants.team_id,
        host_country_participants.team_name,
        host_country_participants.team_market_value,
        host_country_participants.confederation_name,
        ROW_NUMBER() OVER (
            PARTITION BY host_country_participants.host_country_id
            ORDER BY host_country_participants.team_market_value DESC,
                     host_country_participants.team_id ASC
        ) AS team_rank
    FROM host_country_participants
)
SELECT
    ranked_teams.host_country_id,
    ranked_teams.host_country_name,
    ranked_teams.team_id,
    ranked_teams.team_name,
    ranked_teams.team_market_value,
    ranked_teams.confederation_name
FROM ranked_teams
WHERE ranked_teams.team_rank = 1
ORDER BY ranked_teams.host_country_name;
""".strip()

    @staticmethod
    def _build_under_twenty_one_players_by_team_query() -> str:
        return """
SELECT
    team.id AS team_id,
    team.name AS team_name,
    COUNT(player.id) AS under_twenty_one_player_count
FROM teams AS team
LEFT JOIN players AS player
    ON player.team_id = team.id
   AND DATEDIFF(YEAR, player.date_of_birth, ?) 
       - CASE
           WHEN DATEFROMPARTS(
               YEAR(?),
               MONTH(player.date_of_birth),
               DAY(player.date_of_birth)
           ) > ?
           THEN 1
           ELSE 0
         END < 21
GROUP BY team.id, team.name
ORDER BY team.name;
""".strip()
