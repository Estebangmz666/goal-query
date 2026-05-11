USE GoalQuery;
GO

ALTER TABLE confederations
ADD CONSTRAINT uq_confederations_name UNIQUE (name);
GO

ALTER TABLE confederations
ADD CONSTRAINT uq_confederations_code UNIQUE (code);
GO

ALTER TABLE countries
ADD CONSTRAINT uq_countries_name UNIQUE (name);
GO

ALTER TABLE countries
ADD CONSTRAINT uq_countries_fifa_code UNIQUE (fifa_code);
GO

ALTER TABLE countries
ADD CONSTRAINT fk_countries_confederations
FOREIGN KEY (confederation_id) REFERENCES confederations (id);
GO

ALTER TABLE host_countries
ADD CONSTRAINT fk_host_countries_countries
FOREIGN KEY (country_id) REFERENCES countries (id);
GO

ALTER TABLE cities
ADD CONSTRAINT fk_cities_countries
FOREIGN KEY (country_id) REFERENCES countries (id);
GO

ALTER TABLE stadiums
ADD CONSTRAINT fk_stadiums_cities
FOREIGN KEY (city_id) REFERENCES cities (id);
GO

ALTER TABLE groups
ADD CONSTRAINT uq_groups_name UNIQUE (name);
GO

ALTER TABLE teams
ADD CONSTRAINT uq_teams_name UNIQUE (name);
GO

ALTER TABLE teams
ADD CONSTRAINT uq_teams_fifa_code UNIQUE (fifa_code);
GO

ALTER TABLE teams
ADD CONSTRAINT fk_teams_countries
FOREIGN KEY (country_id) REFERENCES countries (id);
GO

ALTER TABLE teams
ADD CONSTRAINT fk_teams_confederations
FOREIGN KEY (confederation_id) REFERENCES confederations (id);
GO

ALTER TABLE teams
ADD CONSTRAINT fk_teams_groups
FOREIGN KEY (group_id) REFERENCES groups (id);
GO

ALTER TABLE teams
ADD CONSTRAINT ck_teams_weight_positive
CHECK (team_weight > 0);
GO

ALTER TABLE teams
ADD CONSTRAINT ck_teams_market_value_non_negative
CHECK (market_value >= 0);
GO

ALTER TABLE coaches
ADD CONSTRAINT fk_coaches_teams
FOREIGN KEY (team_id) REFERENCES teams (id);
GO

ALTER TABLE coaches
ADD CONSTRAINT fk_coaches_nationality_countries
FOREIGN KEY (nationality_country_id) REFERENCES countries (id);
GO

ALTER TABLE coaches
ADD CONSTRAINT uq_coaches_team_id UNIQUE (team_id);
GO

ALTER TABLE players
ADD CONSTRAINT fk_players_teams
FOREIGN KEY (team_id) REFERENCES teams (id);
GO

ALTER TABLE players
ADD CONSTRAINT uq_players_team_shirt_number UNIQUE (team_id, shirt_number);
GO

ALTER TABLE players
ADD CONSTRAINT ck_players_height_positive
CHECK (height_cm > 0);
GO

ALTER TABLE players
ADD CONSTRAINT ck_players_weight_positive
CHECK (weight_kg > 0);
GO

ALTER TABLE players
ADD CONSTRAINT ck_players_market_value_non_negative
CHECK (market_value >= 0);
GO

ALTER TABLE matches
ADD CONSTRAINT fk_matches_stadiums
FOREIGN KEY (stadium_id) REFERENCES stadiums (id);
GO

ALTER TABLE matches
ADD CONSTRAINT fk_matches_groups
FOREIGN KEY (group_id) REFERENCES groups (id);
GO

ALTER TABLE matches
ADD CONSTRAINT fk_matches_home_teams
FOREIGN KEY (home_team_id) REFERENCES teams (id);
GO

ALTER TABLE matches
ADD CONSTRAINT fk_matches_away_teams
FOREIGN KEY (away_team_id) REFERENCES teams (id);
GO

ALTER TABLE matches
ADD CONSTRAINT ck_matches_different_teams
CHECK (home_team_id <> away_team_id);
GO

ALTER TABLE match_results
ADD CONSTRAINT fk_match_results_matches
FOREIGN KEY (match_id) REFERENCES matches (id);
GO

ALTER TABLE match_results
ADD CONSTRAINT ck_match_results_home_goals_non_negative
CHECK (home_goals >= 0);
GO

ALTER TABLE match_results
ADD CONSTRAINT ck_match_results_away_goals_non_negative
CHECK (away_goals >= 0);
GO

ALTER TABLE roles
ADD CONSTRAINT uq_roles_name UNIQUE (name);
GO

ALTER TABLE roles
ADD CONSTRAINT uq_roles_code UNIQUE (code);
GO

ALTER TABLE users
ADD CONSTRAINT fk_users_roles
FOREIGN KEY (role_id) REFERENCES roles (id);
GO

ALTER TABLE users
ADD CONSTRAINT uq_users_username UNIQUE (username);
GO

ALTER TABLE audit_logs
ADD CONSTRAINT fk_audit_logs_users
FOREIGN KEY (user_id) REFERENCES users (id);
GO

ALTER TABLE audit_logs
ADD CONSTRAINT ck_audit_logs_dates_valid
CHECK (logout_at IS NULL OR logout_at >= login_at);
GO
