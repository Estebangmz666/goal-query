# GoalQuery

Python desktop application to manage and simulate a football world championship using SQL Server, raw SQL and a layered architecture without frameworks or ORM.

## Current Status

The repository currently includes the base project configuration for Sprint 1:

- Python entrypoints in the repository root and `src/`
- application bootstrap and environment settings
- centralized database configuration model
- `.env.example` for local setup
- `requirements.txt` with the SQL Server driver dependency

Business features, SQL scripts, repositories, services and UI flows will be implemented incrementally in the next steps.

## Requirements

- Python 3.11 or newer
- SQL Server
- ODBC Driver 17 for SQL Server or compatible installed on the machine

## Local Setup

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

After copying `.env.example`, adjust the database values for your local SQL Server instance.

If you want to test the base bootstrap without database integration yet:

```powershell
python main.py
```

Or:

```powershell
python src/main.py
```

## Environment Variables

The application reads configuration from environment variables.

| Variable | Description |
| --- | --- |
| `APP_ENV` | Runtime environment such as `development` or `production`. |
| `APP_DEBUG` | Enables debug mode when the value is `true`. |
| `APP_NAME` | Display name for the application. |
| `DB_SERVER` | SQL Server host or instance name. |
| `DB_PORT` | SQL Server port. |
| `DB_NAME` | Database name. |
| `DB_USER` | Database user. |
| `DB_PASSWORD` | Database password. |
| `DB_DRIVER` | ODBC driver name. |
| `DB_TRUST_SERVER_CERTIFICATE` | Enables trusted certificate mode for local development. |

## Project Entry Point

The repository root `main.py` delegates execution to `src/main.py`. This keeps local execution simple while allowing the source code to live under `src/` as the project grows.
