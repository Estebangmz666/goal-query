# GoalQuery Backend Implementation Flow

## Objective

Bring the project close to 50% of the academic statement without UI, prioritizing database consistency, business logic, security, reports, and match simulation.

## Implemented Order

1. **Database foundation**
   - Extended the SQL schema with roles, users, and audit logs.
   - Added integrity constraints and indexes for security and reports.
2. **Academic data seeding**
   - Kept catalog SQL seed data.
   - Added a Python seeder that can generate 48 teams, 12 groups, host cities, stadiums, coaches, players, group-stage matches, roles, and initial users.
3. **Security and audit log**
   - Added password hashing, authentication, authorization, user creation, and session audit logging.
4. **Mandatory read use cases**
   - Preserved the 4 mandatory queries already present.
   - Added the 4 mandatory reports in the repository and service layers.
5. **Simulation**
   - Added a Poisson-based service for group-stage match simulation and result persistence.
6. **Tests**
   - Added unit tests for auth, authorization, validators, and simulation.

## Current Backend Scope

- SQL Server only
- Raw SQL only
- No ORM
- No frameworks
- No UI logic

## Next Suggested Steps

1. Wire these services to the future desktop UI.
2. Add CRUD repositories/services for teams, players, coaches, stadiums, and matches.
3. Extend simulation toward standings and qualified teams.
4. Add PDF export if the team decides to generate reports as files.
