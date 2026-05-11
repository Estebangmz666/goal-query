USE GoalQuery;
GO

IF OBJECT_ID(N'dbo.standings', N'U') IS NULL
BEGIN
    CREATE TABLE standings (
        team_id INT NOT NULL,
        group_id INT NOT NULL,
        matches_played INT NOT NULL CONSTRAINT df_standings_matches_played DEFAULT 0,
        points INT NOT NULL CONSTRAINT df_standings_points DEFAULT 0,
        goals_for INT NOT NULL CONSTRAINT df_standings_goals_for DEFAULT 0,
        goals_against INT NOT NULL CONSTRAINT df_standings_goals_against DEFAULT 0,
        CONSTRAINT pk_standings PRIMARY KEY (team_id, group_id),
        CONSTRAINT fk_standings_teams FOREIGN KEY (team_id) REFERENCES teams (id),
        CONSTRAINT fk_standings_groups FOREIGN KEY (group_id) REFERENCES groups (id),
        CONSTRAINT ck_standings_matches_played_non_negative CHECK (matches_played >= 0),
        CONSTRAINT ck_standings_points_non_negative CHECK (points >= 0),
        CONSTRAINT ck_standings_goals_for_non_negative CHECK (goals_for >= 0),
        CONSTRAINT ck_standings_goals_against_non_negative CHECK (goals_against >= 0)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'ix_standings_group_points'
      AND object_id = OBJECT_ID(N'dbo.standings')
)
BEGIN
    CREATE INDEX ix_standings_group_points
        ON standings (group_id, points DESC, goals_for DESC, goals_against ASC);
END;
GO
