USE GoalQuery;
GO

INSERT INTO confederations (name, code)
SELECT source.name, source.code
FROM (
    VALUES
        (N'CONMEBOL', N'CONMEBOL'),
        (N'UEFA', N'UEFA'),
        (N'CONCACAF', N'CONCACAF'),
        (N'AFC', N'AFC'),
        (N'CAF', N'CAF'),
        (N'OFC', N'OFC')
) AS source(name, code)
WHERE NOT EXISTS (
    SELECT 1
    FROM confederations AS existing
    WHERE existing.code = source.code
);
GO

INSERT INTO countries (name, fifa_code, confederation_id)
SELECT source.name, source.fifa_code, confederation.id
FROM (
    VALUES
        (N'Mexico', 'MEX', N'CONCACAF'),
        (N'United States', 'USA', N'CONCACAF'),
        (N'Canada', 'CAN', N'CONCACAF')
) AS source(name, fifa_code, confederation_code)
INNER JOIN confederations AS confederation
    ON confederation.code = source.confederation_code
WHERE NOT EXISTS (
    SELECT 1
    FROM countries AS existing
    WHERE existing.fifa_code = source.fifa_code
);
GO

INSERT INTO host_countries (country_id)
SELECT country_source.id
FROM countries AS country_source
WHERE country_source.fifa_code IN ('MEX', 'USA', 'CAN')
  AND NOT EXISTS (
      SELECT 1
      FROM host_countries AS existing
      WHERE existing.country_id = country_source.id
  );
GO

INSERT INTO groups (name)
SELECT source.name
FROM (
    VALUES
        (N'A'), (N'B'), (N'C'), (N'D'),
        (N'E'), (N'F'), (N'G'), (N'H'),
        (N'I'), (N'J'), (N'K'), (N'L')
) AS source(name)
WHERE NOT EXISTS (
    SELECT 1
    FROM groups AS existing
    WHERE existing.name = source.name
);
GO

INSERT INTO roles (name, code)
SELECT source.name, source.code
FROM (
    VALUES
        (N'Administrator', N'ADMINISTRATOR'),
        (N'Traditional User', N'TRADITIONAL_USER'),
        (N'Sporadic User', N'SPORADIC_USER')
) AS source(name, code)
WHERE NOT EXISTS (
    SELECT 1
    FROM roles AS existing
    WHERE existing.code = source.code
);
GO
