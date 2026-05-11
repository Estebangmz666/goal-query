USE GoalQuery;
GO

CREATE TABLE confederations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    code NVARCHAR(10) NOT NULL
);
GO

CREATE TABLE countries (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    fifa_code CHAR(3) NOT NULL,
    confederation_id INT NOT NULL
);
GO

CREATE TABLE host_countries (
    country_id INT PRIMARY KEY
);
GO

CREATE TABLE cities (
    id INT IDENTITY(1,1) PRIMARY KEY,
    country_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE stadiums (
    id INT IDENTITY(1,1) PRIMARY KEY,
    city_id INT NOT NULL,
    name NVARCHAR(150) NOT NULL,
    capacity INT NOT NULL
);
GO

CREATE TABLE groups (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(10) NOT NULL
);
GO

CREATE TABLE teams (
    id INT IDENTITY(1,1) PRIMARY KEY,
    country_id INT NOT NULL,
    confederation_id INT NOT NULL,
    group_id INT NULL,
    name NVARCHAR(100) NOT NULL,
    fifa_code CHAR(3) NOT NULL,
    team_weight DECIMAL(6,2) NOT NULL,
    market_value DECIMAL(18,2) NOT NULL
);
GO

CREATE TABLE coaches (
    id INT IDENTITY(1,1) PRIMARY KEY,
    team_id INT NOT NULL,
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    nationality_country_id INT NOT NULL
);
GO

CREATE TABLE players (
    id INT IDENTITY(1,1) PRIMARY KEY,
    team_id INT NOT NULL,
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    position NVARCHAR(50) NOT NULL,
    shirt_number INT NOT NULL,
    date_of_birth DATE NOT NULL,
    height_cm DECIMAL(5,2) NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    market_value DECIMAL(18,2) NOT NULL
);
GO

CREATE TABLE matches (
    id INT IDENTITY(1,1) PRIMARY KEY,
    stadium_id INT NOT NULL,
    group_id INT NULL,
    phase NVARCHAR(30) NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    scheduled_at DATETIME2 NOT NULL
);
GO

CREATE TABLE match_results (
    match_id INT PRIMARY KEY,
    home_goals INT NOT NULL,
    away_goals INT NOT NULL,
    played_at DATETIME2 NOT NULL
);
GO

CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    code NVARCHAR(50) NOT NULL
);
GO

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role_id INT NOT NULL,
    username NVARCHAR(100) NOT NULL,
    full_name NVARCHAR(150) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    is_system_administrator BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL
);
GO

CREATE TABLE audit_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    login_at DATETIME2 NOT NULL,
    logout_at DATETIME2 NULL,
    session_status NVARCHAR(20) NULL,
    machine_name NVARCHAR(100) NULL,
    application_name NVARCHAR(100) NULL
);
GO
