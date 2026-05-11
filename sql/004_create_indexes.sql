USE GoalQuery;
GO

CREATE INDEX ix_countries_confederation_id
ON countries (confederation_id);
GO

CREATE INDEX ix_cities_country_id
ON cities (country_id);
GO

CREATE INDEX ix_stadiums_city_id
ON stadiums (city_id);
GO

CREATE INDEX ix_teams_confederation_group
ON teams (confederation_id, group_id);
GO

CREATE INDEX ix_players_team_id
ON players (team_id);
GO

CREATE INDEX ix_players_market_value
ON players (market_value DESC);
GO

CREATE INDEX ix_matches_stadium_phase_scheduled_at
ON matches (stadium_id, phase, scheduled_at);
GO

CREATE INDEX ix_matches_home_team_id
ON matches (home_team_id);
GO

CREATE INDEX ix_matches_away_team_id
ON matches (away_team_id);
GO

CREATE UNIQUE INDEX ux_users_single_administrator
ON users (is_system_administrator)
WHERE is_system_administrator = 1;
GO

CREATE INDEX ix_users_username_active
ON users (username, is_active);
GO

CREATE INDEX ix_audit_logs_user_login_at
ON audit_logs (user_id, login_at DESC);
GO
