try:
    from src.database.connection import DatabaseConnectionFactory
    from src.repositories.base_repository import BaseRepository
except ModuleNotFoundError:
    from database.connection import DatabaseConnectionFactory
    from repositories.base_repository import BaseRepository


class StandingsRepository(BaseRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory) -> None:
        super().__init__(connection_factory)

    def get_group_standings(self, group_id: int) -> list[dict]:
        """Get current standings for a group."""
        return self.fetch_all(
            """
SELECT
    t.id AS team_id,
    t.name AS team_name,
    COUNT(CASE WHEN mr.home_goals IS NOT NULL THEN 1 END) AS matches_played,
    SUM(CASE
        WHEN m.home_team_id = t.id AND mr.home_goals > mr.away_goals THEN 3
        WHEN m.away_team_id = t.id AND mr.away_goals > mr.home_goals THEN 3
        WHEN mr.home_goals = mr.away_goals AND mr.home_goals IS NOT NULL THEN 1
        ELSE 0
    END) AS points,
    SUM(CASE WHEN m.home_team_id = t.id THEN mr.home_goals ELSE 0 END +
        CASE WHEN m.away_team_id = t.id THEN mr.away_goals ELSE 0 END) AS goals_for,
    SUM(CASE WHEN m.home_team_id = t.id THEN mr.away_goals ELSE 0 END +
        CASE WHEN m.away_team_id = t.id THEN mr.home_goals ELSE 0 END) AS goals_against
FROM teams AS t
LEFT JOIN matches AS m ON (m.home_team_id = t.id OR m.away_team_id = t.id) AND m.group_id = ? AND m.phase = ?
LEFT JOIN match_results AS mr ON mr.match_id = m.id
WHERE t.group_id = ?
GROUP BY t.id, t.name
ORDER BY points DESC, (
    SUM(CASE WHEN m.home_team_id = t.id THEN mr.home_goals ELSE 0 END +
        CASE WHEN m.away_team_id = t.id THEN mr.away_goals ELSE 0 END) -
    SUM(CASE WHEN m.home_team_id = t.id THEN mr.away_goals ELSE 0 END +
        CASE WHEN m.away_team_id = t.id THEN mr.home_goals ELSE 0 END)
) DESC;
""".strip(),
            (group_id, "GROUP_STAGE", group_id),
        )

    def get_qualified_teams_from_group(self, group_id: int, limit: int = 2) -> list[dict]:
        """Get top teams from a group (usually top 2)."""
        standings = self.get_group_standings(group_id)
        return standings[:limit]

    def get_all_qualified_teams(self, limit_per_group: int = 2) -> list[dict]:
        """Get all qualified teams from all groups."""
        return self.fetch_all(
            """
WITH group_standings AS (
    SELECT
        t.id AS team_id,
        t.name AS team_name,
        t.group_id,
        SUM(CASE
            WHEN m.home_team_id = t.id AND mr.home_goals > mr.away_goals THEN 3
            WHEN m.away_team_id = t.id AND mr.away_goals > mr.home_goals THEN 3
            WHEN mr.home_goals = mr.away_goals AND mr.home_goals IS NOT NULL THEN 1
            ELSE 0
        END) AS points,
        ROW_NUMBER() OVER (PARTITION BY t.group_id ORDER BY
            SUM(CASE
                WHEN m.home_team_id = t.id AND mr.home_goals > mr.away_goals THEN 3
                WHEN m.away_team_id = t.id AND mr.away_goals > mr.home_goals THEN 3
                WHEN mr.home_goals = mr.away_goals AND mr.home_goals IS NOT NULL THEN 1
                ELSE 0
            END) DESC,
            (SUM(CASE WHEN m.home_team_id = t.id THEN mr.home_goals ELSE 0 END +
                 CASE WHEN m.away_team_id = t.id THEN mr.away_goals ELSE 0 END) -
             SUM(CASE WHEN m.home_team_id = t.id THEN mr.away_goals ELSE 0 END +
                 CASE WHEN m.away_team_id = t.id THEN mr.home_goals ELSE 0 END)) DESC
        ) AS rank_in_group
    FROM teams AS t
    LEFT JOIN matches AS m ON (m.home_team_id = t.id OR m.away_team_id = t.id) AND m.phase = ?
    LEFT JOIN match_results AS mr ON mr.match_id = m.id
    WHERE t.group_id IS NOT NULL
    GROUP BY t.id, t.name, t.group_id
)
SELECT team_id, team_name, group_id, points
FROM group_standings
WHERE rank_in_group <= ?
ORDER BY group_id, rank_in_group;
""".strip(),
            ("GROUP_STAGE", limit_per_group),
        )

    def create_standings_record(
        self,
        team_id: int,
        group_id: int,
        matches_played: int,
        points: int,
        goals_for: int,
        goals_against: int,
    ) -> None:
        """Create or update standings record for a team."""
        self.execute_non_query(
            """
MERGE INTO standings AS target
USING (SELECT ? AS team_id, ? AS group_id) AS source
ON target.team_id = source.team_id AND target.group_id = source.group_id
WHEN MATCHED THEN
    UPDATE SET matches_played = ?, points = ?, goals_for = ?, goals_against = ?
WHEN NOT MATCHED THEN
    INSERT (team_id, group_id, matches_played, points, goals_for, goals_against)
    VALUES (?, ?, ?, ?, ?, ?);
""".strip(),
            (team_id, group_id, matches_played, points, goals_for, goals_against,
             team_id, group_id, matches_played, points, goals_for, goals_against),
        )
