<h1 align="center">GoalQuery</h1>

<p align="center">
  Python desktop application to manage and simulate a football world championship using SQL Server, raw SQL and a layered architecture without frameworks or ORM.
</p>

---

## 1. Project Overview

GoalQuery is an academic desktop application developed in Python for the final project of the Databases I course.

The application must manage the information of a football World Cup with 48 teams from different confederations, including teams, coaches, players, cities, stadiums, groups, matches, users, login sessions, queries and reports.

The system must connect to a SQL Server database and must be developed without frameworks. The project must not use an ORM. All database operations must be implemented with raw SQL queries, stored in the persistence layer and executed safely with parameters.

---

## 2. Main Objective

The main objective is to build a desktop application that allows users to:

- Manage World Cup data.
- Store teams, players, coaches, confederations, host countries, cities, stadiums, groups and matches.
- Simulate football matches using a Poisson distribution based on each team's weight.
- Execute CRUD operations according to the authenticated user's role.
- Execute the mandatory academic queries.
- Generate the mandatory academic reports.
- Register login and logout events in an audit log.
- Keep the codebase clean, maintainable and easy to explain in an academic presentation.

---

## 3. Hard Requirements

These rules are mandatory and must not be ignored.

### 3.1 Technology

- Use Python.
- Use SQL Server as the database engine.
- Build a desktop application.
- Do not use web frameworks.
- Do not use desktop frameworks unless the team and professor explicitly approve them.
- Prefer Python standard library tools when possible.
- For database connection, use a SQL Server driver such as `pyodbc` if allowed.
- For reports, use a PDF/reporting library only if allowed by the professor.
- Do not use ORM libraries such as SQLAlchemy, Peewee, Django ORM or similar.

### 3.2 Architecture

- Do not put business logic inside UI files.
- Do not put SQL queries inside UI files.
- Do not spread database connection code across the project.
- Do not duplicate SQL queries.
- Do not use global mutable state for business logic.
- Do not hardcode credentials in source code.
- Do not commit `.env`, database passwords, generated reports, cache files or virtual environments.
- Do not invent requirements that are not present in the project statement unless clearly marked as optional.

### 3.3 Code Language

- All source code must be written in English.
- Folder names, file names, classes, functions, methods, variables, constants and comments must be in English.
- User-facing labels, buttons, menus and messages may be in Spanish because the application is for an academic Colombian context.

---

## 4. Required Functional Scope

### 4.1 World Cup Data

The database must store at least:

- Confederations.
- Countries.
- Host countries: Mexico, USA and Canada.
- Cities.
- Stadiums.
- Teams.
- Coaches.
- Players.
- Groups.
- Group-stage matches.
- Match results.
- Users.
- User roles.
- Login/logout audit records.

### 4.2 Tournament Simulation

The application must simulate a football World Cup.

The initial data should be populated using:

```text
seeders/seed_data.py
```

The match simulation must use a Poisson distribution to generate realistic scores.

Each team must have a `weight` value. This value is a floating-point number that represents the relative strength of the team and affects the probability of winning or scoring more goals.

The simulation logic must be isolated in the service layer. It must not be placed inside repositories or UI files.

Recommended simulation responsibilities:

- Calculate expected goals from team weights.
- Generate goals using Poisson distribution.
- Save match results in the database.
- Update standings after each group-stage match.
- Determine qualified teams according to the tournament rules defined by the team.
- Simulate knockout matches if the application scope includes quarter-finals, semi-finals and final.

If the tournament rules are not fully defined, keep them configurable and avoid hardcoding assumptions that cannot be explained.

---

## 5. User Roles and Permissions

The application must include a basic security system with login.

There are three user types:

### 5.1 Administrator

There must be only one administrator user.

The administrator can:

- Log into the system.
- Create new users.
- Execute CRUD operations.
- Execute queries.
- Generate reports.
- Access audit log reports.

### 5.2 Traditional User

Traditional users can:

- Log into the system.
- Execute CRUD operations for data management.
- Execute queries.
- Generate reports if the project team allows it.

Traditional users cannot:

- Create users.
- Modify administrator data.
- Access restricted security configuration.

### 5.3 Sporadic User

Sporadic users can:

- Log into the system.
- Execute queries.

Sporadic users cannot:

- Create users.
- Execute CRUD operations.
- Modify system data.
- Delete data.
- Access restricted security configuration.

---

## 6. Audit Log

The system must keep an audit log for user sessions.

The audit log must store:

- User ID.
- Login date and time.
- Logout date and time.
- Optional session status.
- Optional machine or app metadata if useful.

Rules:

- A login event must be registered when the user successfully enters the system.
- A logout event must be updated when the user exits the system.
- If the application closes unexpectedly, the system may leave the logout field as `NULL` or update it using a controlled recovery strategy.
- Audit logic must be handled by an authentication/session service, not by the UI directly.

---

## 7. Mandatory Queries

The application must implement the following queries:

1. Determine the data of the most expensive player by confederation.
2. List the matches that will be played in a stadium selected by the user.
3. Determine the most expensive team playing in each host country during the group stage.
4. Determine the number of players under 21 years old per team.

Query implementation rules:

- Queries must be written in raw SQL.
- Queries must be parameterized.
- Queries must be stored in repositories or dedicated query classes.
- Queries must return DTOs or simple read models.
- UI files must only call services and display the result.
- Do not use `SELECT *` in final queries.
- Use clear aliases for computed columns.

---

## 8. Mandatory Reports

The application must implement the following reports:

1. List users who entered and exited the application at a specific date and time.
2. List players whose weight, height and team match the filters requested by the user.
3. Determine the total value of players per team belonging to a specific confederation.
4. List the countries that will play in each host country.

Report rules:

- Reports can be generated as PDF files or shown inside a form if the professor allows it.
- Report queries must be parameterized.
- Report generation must be handled in a report service.
- Generated files must be saved in a controlled output folder such as `outputs/reports/`.
- The report service must not contain UI code.
- The UI must ask for filters and then call the corresponding service.

---

## 9. Recommended Project Structure

Use this structure as the default guide:

```text
GoalQuery/
│
├── AGENTS.md
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── src/
│   ├── main.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── bootstrap.py
│   │   └── settings.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── database_config.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── transaction.py
│   │   └── initializer.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   ├── coach.py
│   │   │   ├── confederation.py
│   │   │   ├── country.py
│   │   │   ├── city.py
│   │   │   ├── stadium.py
│   │   │   ├── group.py
│   │   │   ├── match.py
│   │   │   ├── user.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── enums/
│   │   │   ├── __init__.py
│   │   │   ├── user_role.py
│   │   │   └── match_phase.py
│   │   │
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       ├── validation_error.py
│   │       ├── authentication_error.py
│   │       └── authorization_error.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── team_repository.py
│   │   ├── player_repository.py
│   │   ├── coach_repository.py
│   │   ├── confederation_repository.py
│   │   ├── country_repository.py
│   │   ├── city_repository.py
│   │   ├── stadium_repository.py
│   │   ├── group_repository.py
│   │   ├── match_repository.py
│   │   ├── user_repository.py
│   │   ├── audit_log_repository.py
│   │   ├── query_repository.py
│   │   └── report_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── authorization_service.py
│   │   ├── user_service.py
│   │   ├── team_service.py
│   │   ├── player_service.py
│   │   ├── match_service.py
│   │   ├── simulation_service.py
│   │   ├── query_service.py
│   │   └── report_service.py
│   │
│   ├── dto/
│   │   ├── __init__.py
│   │   ├── player_queries.py
│   │   ├── team_queries.py
│   │   ├── match_queries.py
│   │   └── report_models.py
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── login_window.py
│   │   ├── dashboard_window.py
│   │   ├── users_window.py
│   │   ├── teams_window.py
│   │   ├── players_window.py
│   │   ├── matches_window.py
│   │   ├── queries_window.py
│   │   └── reports_window.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── password_hasher.py
│   │   ├── validators.py
│   │   ├── date_utils.py
│   │   └── file_utils.py
│   │
│   └── seeders/
│       ├── __init__.py
│       └── seed_data.py
│
├── sql/
│   ├── 001_create_database.sql
│   ├── 002_create_tables.sql
│   ├── 003_create_constraints.sql
│   ├── 004_create_indexes.sql
│   ├── 005_seed_base_data.sql
│   └── 006_views_or_procedures.sql
│
├── tests/
│   ├── __init__.py
│   ├── test_simulation_service.py
│   ├── test_auth_service.py
│   ├── test_authorization_service.py
│   └── test_validators.py
│
├── outputs/
│   └── reports/
│
└── docs/
    ├── database_model.md
    ├── use_cases.md
    └── project_notes.md
```

This structure can be simplified if the team needs a smaller project, but the separation between UI, services, repositories, domain, database and SQL scripts must be preserved.

---

## 10. Layer Responsibilities

### 10.1 UI Layer

The UI layer is responsible only for:

- Showing forms.
- Reading user input.
- Calling services.
- Displaying success messages.
- Displaying validation errors.
- Displaying query/report results.

The UI layer must not:

- Execute SQL.
- Open database connections directly.
- Hash passwords directly.
- Decide complex business rules.
- Simulate matches directly.
- Generate reports directly.

### 10.2 Service Layer

The service layer is responsible for:

- Business rules.
- Validations.
- Authentication.
- Authorization.
- Tournament simulation.
- Report orchestration.
- Coordinating repositories.
- Managing transactions when a use case requires multiple database operations.

### 10.3 Repository Layer

The repository layer is responsible for:

- Raw SQL execution.
- Mapping database rows into entities or DTOs.
- Insert, update, delete and select operations.
- Query-specific methods.

Repositories must not:

- Contain UI code.
- Contain business decisions.
- Print messages to the console as final behavior.
- Read user input.

### 10.4 Domain Layer

The domain layer is responsible for:

- Entity definitions.
- Simple domain behavior.
- Domain-specific exceptions.
- Enums and constants.

Domain objects should not depend on the database driver or UI library.

### 10.5 Database Layer

The database layer is responsible for:

- Creating connections.
- Closing connections.
- Handling transactions.
- Initializing the database if needed.
- Loading database configuration.

---

## 11. Database Rules

### 11.1 SQL Style

- Use raw SQL.
- Use parameterized queries.
- Do not concatenate user input into SQL strings.
- Avoid `SELECT *` in final implementation.
- Use explicit column names.
- Use meaningful table aliases.
- Use constraints for data integrity.
- Use foreign keys.
- Use indexes for frequent filters and joins.
- Use transactions for multi-step operations.

### 11.2 Suggested Tables

The final model may vary, but it should include tables similar to:

- `confederations`
- `countries`
- `host_countries`
- `cities`
- `stadiums`
- `teams`
- `coaches`
- `players`
- `groups`
- `group_teams`
- `matches`
- `match_results`
- `users`
- `roles`
- `audit_logs`

### 11.3 Sensitive Data

- Passwords must never be stored in plain text.
- Store password hashes only.
- Use a secure hashing function from Python libraries.
- Do not log passwords.
- Do not show passwords in UI tables.
- Do not commit real database credentials.

---

## 12. Authentication and Authorization Rules

Authentication answers the question: Who is the user?

Authorization answers the question: What is the user allowed to do?

Implementation rules:

- `auth_service.py` handles login and logout.
- `authorization_service.py` checks permissions.
- UI windows must ask the authorization service before enabling restricted actions.
- Repositories must not decide permissions.
- The administrator role must be protected.
- Only the administrator can create new users.
- Sporadic users must be blocked from CRUD operations.

Recommended permission names:

```text
CREATE_USER
MANAGE_TEAMS
MANAGE_PLAYERS
MANAGE_MATCHES
RUN_QUERIES
GENERATE_REPORTS
VIEW_AUDIT_LOGS
```

---

## 13. Simulation Rules

The simulation must be deterministic only when a test seed is provided.

Recommended design:

- `SimulationService` receives teams and match data.
- It calculates each team's expected goals.
- It generates goals using a Poisson distribution.
- It saves the final score through `MatchRepository`.
- It updates standings through the proper service or repository.

Possible formula idea:

```text
expected_goals = base_goal_rate * team_weight_adjustment
```

The exact formula can evolve, but it must be understandable and easy to explain.

Rules:

- Do not simulate directly from the UI.
- Do not store random logic inside repositories.
- Keep the simulation testable.
- Allow fixed random seeds for tests.
- Avoid unrealistic scores by applying reasonable limits if needed.

---

## 14. Error Handling

Use custom exceptions for known business errors:

- `ValidationError`
- `AuthenticationError`
- `AuthorizationError`

Do not let raw database errors leak directly into the UI.

The UI should show friendly messages such as:

```text
No tienes permisos para realizar esta acción.
El usuario o la contraseña son incorrectos.
El campo nombre es obligatorio.
No se pudo guardar el registro. Revisa los datos ingresados.
```

---

## 15. Validation Rules

Validate data before sending it to repositories.

Examples:

- Required fields cannot be empty.
- Player age must be valid.
- Player market value must be greater than or equal to zero.
- Player height and weight must be greater than zero.
- Team weight must be greater than zero.
- A stadium must belong to a valid city.
- A city must belong to a valid host country when used for host matches.
- A group must not exceed the configured number of teams.
- A match cannot have the same team as home and away team.
- Usernames must be unique.
- Only one administrator user must exist.

---

## 16. Testing Expectations

Even if the project does not require a full test suite, write tests for important logic when possible.

Prioritize tests for:

- Password hashing.
- Login validation.
- Authorization rules.
- Poisson simulation.
- Match result generation.
- Validators.
- Critical query methods if the database test setup is available.

Use clear test names in English.

Example:

```text
test_sporadic_user_cannot_create_team
test_admin_can_create_user
test_simulation_returns_valid_score
test_player_age_validator_rejects_negative_age
```

---

## 17. Git and Version Control Rules

- Use small commits.
- Do not commit generated files.
- Do not commit `.env`.
- Do not commit virtual environments.
- Do not commit `__pycache__`.
- Do not commit local database backups.
- Keep `README.md` updated with setup instructions.
- Keep SQL scripts ordered and reproducible.

Recommended `.gitignore` entries:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
outputs/reports/*.pdf
*.log
.DS_Store
.idea/
.vscode/
```

---

## 18. Agent Behavior Rules

When working as an AI coding agent in this repository, follow these rules:

1. Read the existing files before modifying code.
2. Respect the current architecture.
3. Do not introduce frameworks.
4. Do not introduce an ORM.
5. Do not move files without a strong reason.
6. Do not rename public functions or classes without checking their usage.
7. Do not create unnecessary abstractions.
8. Prefer simple, readable and academic-friendly code.
9. Keep business logic in services.
10. Keep SQL in repositories or SQL-specific files.
11. Use parameterized SQL queries.
12. Preserve Spanish UI labels if they already exist.
13. Write source code identifiers in English.
14. Add tests when modifying important business logic.
15. Explain architectural decisions briefly when making non-trivial changes.
16. Do not hide errors with empty `except` blocks.
17. Do not use broad `except Exception` unless the error is logged or transformed properly.
18. Do not add dependencies unless they are clearly necessary and allowed.
19. Do not implement unrelated features.
20. Do not fake completed behavior. If something is incomplete, mark it clearly.

---

## 19. Development Workflow for Agents

Before implementing a feature:

1. Identify the required use case.
2. Locate the related UI, service, repository and SQL files.
3. Check user role permissions.
4. Check if database changes are needed.
5. Implement from the inside out:
   - Domain or DTOs.
   - Repository method.
   - Service method.
   - UI integration.
   - Tests if possible.
6. Run or explain the relevant verification steps.
7. Keep changes focused.

---

## 20. Definition of Done

A task is considered done only when:

- It respects the no-framework and no-ORM constraints.
- It keeps UI, services and repositories separated.
- It uses parameterized SQL.
- It validates user input.
- It handles authorization when required.
- It handles errors in a user-friendly way.
- It does not break existing functionality.
- It can be explained clearly to the professor.
- It is consistent with the project statement.
- It includes tests or manual verification steps when possible.

---

## 21. Mandatory Academic Checklist

Before the final delivery, verify that the application includes:

### Database

- [ ] 48 teams.
- [ ] Confederations.
- [ ] Coaches.
- [ ] Players.
- [ ] Cities.
- [ ] Stadiums.
- [ ] 12 groups.
- [ ] Group-stage matches.
- [ ] Host countries: Mexico, USA and Canada.
- [ ] Users.
- [ ] Roles.
- [ ] Audit log.

### Security

- [ ] Login.
- [ ] One administrator user.
- [ ] Traditional users.
- [ ] Sporadic users.
- [ ] Administrator can create users.
- [ ] Traditional users can execute CRUD operations.
- [ ] Sporadic users can only execute queries.
- [ ] Login time is saved.
- [ ] Logout time is saved.

### Queries

- [ ] Most expensive player by confederation.
- [ ] Matches by selected stadium.
- [ ] Most expensive team by host country during group stage.
- [ ] Number of players under 21 years old per team.

### Reports

- [ ] Users who entered and exited at a specific date and time.
- [ ] Players filtered by weight, height and team.
- [ ] Total player value per team for a selected confederation.
- [ ] Countries that will play in each host country.

### Simulation

- [ ] Seed data exists.
- [ ] Team weight exists.
- [ ] Poisson-based result generation exists.
- [ ] Match results are persisted.
- [ ] Simulation logic is not inside UI files.
- [ ] Simulation logic is not inside repositories.

---

## 22. Suggested README Setup Commands

The exact commands may vary depending on the environment.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

If the team uses Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

---

## 23. Final Notes

GoalQuery must be simple enough to explain, but organized enough to avoid messy code.

The priority is not to over-engineer. The priority is to deliver a clean academic desktop application that demonstrates:

- Good database design.
- Correct SQL usage.
- Clear separation of responsibilities.
- Basic security.
- Required queries and reports.
- A working tournament simulation.

---

## 24. Current Repository Status and Handoff Priorities

This section reflects the real repository status and is intended to guide the next agent working on the project.

### 24.1 What is already implemented

As of the current repository state, the backend already includes:

- SQL scripts for:
  - database creation
  - main tournament tables
  - roles, users and audit logs
  - constraints and indexes
  - base seed data
- A Python seeder in:

```text
seeders/seed_data.py
```

that populates:

- 48 teams
- 12 groups
- host cities and stadiums
- coaches
- players
- group-stage matches
- initial roles and users

The backend also already includes:

- `QueryRepository` and `QueryService` with the 4 mandatory academic queries
- `ReportRepository` and `ReportService` with the 4 mandatory academic reports
- `AuthService`, `AuthorizationService` and `UserService`
- password hashing utilities
- audit log session registration
- `SimulationService` for Poisson-based match result generation
- unit tests for:
  - queries
  - authentication
  - authorization
  - validators
  - simulation

### 24.2 What should NOT be reimplemented

Do not recreate or replace these features unless there is a real bug:

- login/logout backend flow
- role-based permission checks
- audit log persistence
- the 4 mandatory queries
- the 4 mandatory reports at backend level
- the base Poisson match simulation
- the current SQL schema for users, roles and audit logs
- the existing bulk seed strategy

If you need to improve them, extend them carefully instead of rewriting them from scratch.

### 24.3 Highest-priority missing work

The next agent should focus on the missing academic functionality that still blocks final delivery.

Priority order:

1. Implement backend CRUD for the main managed entities:
   - teams
   - players
   - coaches
   - cities
   - stadiums
   - matches
2. Add stronger business validations for those CRUD flows.
3. Extend simulation beyond a single persisted result:
   - standings
   - points
   - goals for and against
   - qualified teams
   - optional knockout stage if time allows
4. Prepare service APIs that the UI team can call directly without embedding business rules in UI files.
5. If academically required by the team/professor, add PDF export for reports only after backend data flows are stable.

### 24.4 Rules for the next agent

When continuing this repository:

- Read the existing implementation first before adding new services.
- Respect the current `src/` architecture.
- Keep SQL in repositories.
- Keep business rules in services.
- Do not move logic into UI files.
- Keep source code identifiers in English.
- Preserve Spanish only for user-facing text.
- Use parameterized SQL only.
- Add tests for each important business rule you add.
- Prefer extending current services and repositories over creating parallel duplicate abstractions.

### 24.5 Recommended next implementation sequence

Use this order unless the user explicitly asks for something else:

1. `team` CRUD
2. `player` CRUD
3. `coach` CRUD
4. `stadium` and `city` CRUD
5. `match` CRUD
6. simulation standings and qualification flow
7. report export integration
8. UI integration by the UI team
